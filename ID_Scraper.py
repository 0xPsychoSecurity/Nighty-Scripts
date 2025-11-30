@nightyScript(
    name="ID Scraper",
    author="glowx",
    description="Discord ID Collector: auto-logs unique user IDs on messages, mentions & joins, with hourly breakdowns and daily reports. All collected IDs are stored in the dumps folder under the data directory.",
    usage="[p]idstats"
)
def UltimateIDCollectorFinal():
    import os
    import json
    import discord
    import pathlib
    import subprocess
    import tempfile
    from datetime import datetime, timedelta
    import atexit
    from collections import defaultdict

    DATA_DIR = pathlib.Path(os.getenv('APPDATA')) / "Nighty Selfbot" / "data" / "dumps" / "ids"
    OUTPUT_FILE = DATA_DIR / "user_ids.txt"
    TIMESTAMPS_FILE = DATA_DIR / "id_timestamps.json"
    DAILY_STATS_FILE = DATA_DIR / "daily_stats.json"
    DEBUG_FILE = DATA_DIR / "ids_debug.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    state = {'join': 0, 'mention': 0, 'message_authors': 0, 'cached_members': 0, 'last_update': datetime.now().isoformat()}
    existing_ids = set()
    timestamps = {}
    daily_stats = defaultdict(lambda: {'total': 0, 'hours': defaultdict(int)})

    def default_to_regular(d):
        if isinstance(d, defaultdict):
            return {k: default_to_regular(v) for k, v in d.items()}
        return d

    def update_daily_stats():
        date = datetime.now().strftime("%Y-%m-%d")
        hour = datetime.now().strftime("%H")
        daily_stats[date]['total'] += 1
        daily_stats[date]['hours'][hour] += 1

    def save_all():
        try:
            with open(DEBUG_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            with open(TIMESTAMPS_FILE, 'w', encoding='utf-8') as f:
                json.dump(timestamps, f, indent=2)
            with open(DAILY_STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_to_regular(daily_stats), f, indent=2)
        except Exception:
            pass

    try:
        if OUTPUT_FILE.exists():
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_ids = {line.strip() for line in f if line.strip().isdigit()}
                state['cached_members'] = len(existing_ids)
        
        if DEBUG_FILE.exists():
            with open(DEBUG_FILE, 'r', encoding='utf-8') as f:
                state.update(json.load(f))
        
        if TIMESTAMPS_FILE.exists():
            with open(TIMESTAMPS_FILE, 'r', encoding='utf-8') as f:
                timestamps.update(json.load(f))
                
        if DAILY_STATS_FILE.exists():
            with open(DAILY_STATS_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                for date, data in loaded.items():
                    daily_stats[date] = {'total': data['total'], 'hours': defaultdict(int, data['hours'])}
    except Exception:
        pass

    @bot.listen()
    async def on_message(message):
        author_id = str(message.author.id)
        if not message.author.bot and author_id not in existing_ids:
            existing_ids.add(author_id)
            timestamps[author_id] = datetime.now().isoformat()
            state['message_authors'] += 1
            state['cached_members'] += 1
            update_daily_stats()
            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{author_id}\n")
            save_all()

        for user in message.mentions:
            uid = str(user.id)
            if not user.bot and uid not in existing_ids:
                existing_ids.add(uid)
                timestamps[uid] = datetime.now().isoformat()
                state['mention'] += 1
                state['cached_members'] += 1
                update_daily_stats()
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"{uid}\n")
                save_all()

    @bot.listen()
    async def on_member_join(member):
        uid = str(member.id)
        if not member.bot and uid not in existing_ids:
            existing_ids.add(uid)
            timestamps[uid] = datetime.now().isoformat()
            state['join'] += 1
            state['cached_members'] += 1
            update_daily_stats()
            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{uid}\n")
            save_all()

    @bot.command()
    async def idstats(ctx):
        await ctx.message.delete()

        console_script = f"""
import os
import json
import time
from datetime import datetime, timedelta

DEBUG_PATH = {json.dumps(str(DEBUG_FILE))}
TIMESTAMPS_PATH = {json.dumps(str(TIMESTAMPS_FILE))}
DAILY_PATH = {json.dumps(str(DAILY_STATS_FILE))}

def load_data():
    try:
        with open(DEBUG_PATH, 'r') as f:
            state = json.load(f)
        with open(TIMESTAMPS_PATH, 'r') as f:
            timestamps = json.load(f)
        with open(DAILY_PATH, 'r') as f:
            daily_stats = json.load(f)
        return state, timestamps, daily_stats
    except Exception as e:
        return {{}}, {{}}, {{}}

def format_line(label, value):
    return f"│ {{label:<20}} {{str(value):<16}} │"

while True:
    try:
        state, timestamps, daily_stats = load_data()
        now = datetime.now()
        
        last_hour = sum(
            1 for ts in timestamps.values()
            if datetime.fromisoformat(ts) > now - timedelta(hours=1)
        )
        today_total = daily_stats.get(now.strftime("%Y-%m-%d"), {{}}).get("total", 0)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("╔════════════════════════════════════════╗")
        print("║         LIVE ID COLLECTION STATS      ║")
        print("╠════════════════════════════════════════╣")
        print(format_line("Total IDs", state.get("cached_members", 0)))
        print(format_line("Last Hour", last_hour))
        print(format_line("Today's Total", today_total))
        print("╠════════════════════════════════════════╣")
        print(format_line("Join Events", state.get("join", 0)))
        print(format_line("Mentions", state.get("mention", 0)))
        print(format_line("Message Authors", state.get("message_authors", 0)))
        print("╠════════════════════════════════════════╣")
        print(format_line("Last Update", state.get("last_update", "N/A")))
        print("╚════════════════════════════════════════╝")
        print("\\nPress CTRL+C to exit...")
        time.sleep(2)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Error: {{str(e)}}")
        time.sleep(5)
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(console_script)
            temp_path = f.name

        subprocess.Popen(
            f'start cmd /k python "{temp_path}"',
            shell=True
        )

    atexit.register(save_all)

UltimateIDCollectorFinal()