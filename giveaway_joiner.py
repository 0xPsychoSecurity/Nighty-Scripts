# Giveaway Joiner V1.3.4.5 - Universal Giveaway Detection and Auto-Join System

# --- New Features ---
# - Added a new input for exclude channels.
# - A counter for analyzed messages was added to the UI.
# - New languages ​​have been added for GW detection: German, Portuguese, and Italian.
# - The script now detects words like: Open a ticket, and if the direct channel hasn't been entered, it will search for it and open it automatically.
# - It also detects when someone asks you to send a DM to claim your prize; activate it in the UI. (It doesn't support captchas, and I won't be adding support for them.)
# - A new toggle was added to disable failed to join logs.
# - Added new commands: [p]gw list, [p]gw undo and [p]gw remove <bot_id>
# - [p]gw list: List bots that has a pattern
# - [p]gw undo: Remove the most recent pattern you added
# - [p]gw remove <bot_id>: Remove a specific pattern by bot ID

# --- Improvements ---
# - UI improvements
# - The command was improved: [p]gw add <message_id> (It should be much more reliable and efficient).
# - Improvements to the .log file for better debugging.
# - Improvements to the embed logs.
# - New base false positives were added.
# - A new bot was added for new users (Bleed: 593921296224747521).
# - General improvements

# --- Fixes --- 

# --- Note ---
# - The following bots cannot currently have their wins detected by the script:
# - Lawliet (368521195940741122)
# - If you find any bug please report.
# - If your bot doesn't detect it, report it.

@nightyScript(
    name="Giveaway Joiner",
    author="Luxed",
    description="Universal multi-token giveaway detection and auto-join system with blacklist filtering and analytics",
    usage="UI OR [p]gw add <message_id>"
)
def giveaway_Joiner():
    import os
    import json
    import asyncio
    import aiohttp
    import random
    from datetime import datetime
    import traceback
    import re
    import discord
    import zipfile
    import io
    import threading
    from discord.http import Route

    __version__ = "1.3.4.5"

    DEFAULT_FP_PATTERNS = [
        {
        "title": "moderation statistics",
        "author_name": "",
        "bot_id": "155149108183695360"
        },
        {

            "title": "join and leave members server stats",
            "author_name": "",
            "bot_id": "720351927581278219"
        },

        {
            "title": "command:",
            "author_name": "",
            "bot_id": "155149108183695360"
        },
        {

            "title": "",
            "author_name": "member left",
            "bot_id": "155149108183695360"
        },
        {

            "title": "gracias por tu mejora",
            "author_name": "",
            "bot_id": "429457053791158281"
        },

        {

            "title": "invite tracker's help page",
            "author_name": "",
            "bot_id": "720351927581278219"
        },
        {
            "title": "",
            "author_name": "bump reminder",
            "bot_id": "302050872383242240"
        },
        {
        "title": "<a:nk:1263663997668819024> recordatorio registrado",
        "author_name": "",
        "bot_id": "429457053791158281"
        },
        {
        "title": "",
        "author_name": "member joined",
        "bot_id": "1099852260630085713"
        },
        {
        "bot_id": "155149108183695360",
        "title": "",
        "author_name": "",
        "footer_text": "",
        "content_match": "",
        "description_match": "<:dynoerror:314691684455809024> please use a valid limit less then 14 days. ex 3",
        "buttons_list": [],
        "field_names": []
        },
        {
        "bot_id": "270904126974590976",
        "title": "dice champs",
        "author_name": "",
        "footer_text": "",
        "content_match": "",
        "description_match": "> who's got the best rng? let's find out.\n> hit the button below to roll a d100 ",
        "buttons_list": [
            "sunbeard20"
        ],
        "field_names": []
        },
        {
        "bot_id": "270904126974590976",
        "title": "boss battle",
        "author_name": "",
        "footer_text": "",
        "content_match": "",
        "description_match": "> oh shit a boss spawned!\n> we need 2-5 people to send \"i'm ready\" to fight this",
        "buttons_list": [],
        "field_names": []
        },
        {
        "bot_id": "270904126974590976",
        "title": "daily coins",
        "author_name": "",
        "footer_text": "",
        "content_match": "",
        "description_match": "> \u23e3 102,160 was placed in your wallet!",
        "buttons_list": [
            "more rewards here"
        ],
        "field_names": [
            "base",
            "streak bonus",
            "donor bonus",
            "next daily",
            "next item reward",
            "streak"
        ]
        },
        {
        "bot_id": "593921296224747521",
        "title": "hwisnotgood (@imstrongerboy6)",
        "author_name": "squirrell",
        "footer_text": "roblox",
        "content_match": "",
        "description_match": "",
        "buttons_list": [],
        "field_names": [
            "**created**",
            "**last online**",
            "**badges (2)**",
            "**id**",
            "**following**",
            "**followers**"
        ]
        },
        {
        "bot_id": "270904126974590976",
        "title": "zayan8610",
        "author_name": "",
        "footer_text": "",
        "content_match": "",
        "description_match": "",
        "buttons_list": [],
        "field_names": [
            "level",
            "coins",
            "items",
            "commands",
            "pets",
            "showcase"
        ]
        },
        {
        "bot_id": "270904126974590976",
        "title": "robbable users in \ud83e\udeb7 \u0192\u03b1erie \ud80c\udc83 \u0741\u208a \u27e1 decor\u318dgames \u318dgiveaways  \u27e1 \u0741\u208a",
        "author_name": "",
        "footer_text": "your wishlist is gone now bub",
        "content_match": "",
        "description_match": "` \u23e3 13,618,723 ` <@959817610541805699> (ario.zona_)\n` \u23e3 12,013,781 ` <@809213412",
        "buttons_list": [
            "ario.zona_",
            "2radikal",
            "ruthielette",
            "hiali._",
            "mocha797"
        ],
        "field_names": []
        },
        {
        "bot_id": "270904126974590976",
        "title": "luka's daily coins",
        "author_name": "",
        "footer_text": "",
        "content_match": "",
        "description_match": "> \u23e3 102,160 was placed in your wallet!",
        "buttons_list": [
            "more rewards here"
        ],
        "field_names": [
            "base",
            "streak bonus",
            "donor bonus",
            "next daily",
            "next item reward",
            "streak"
        ]
        },
        {
        "bot_id": "270904126974590976",
        "title": "robbable users in \uff61\u02da\u0cc0 berry \u2601 guild tags\ufe52emojis\ufe52giveaways\ufe52social",
        "author_name": "",
        "footer_text": "your wishlist is gone now bub",
        "content_match": "",
        "description_match": "` \u23e3 3,795,253 ` <@1357847405688656132> (sirenoftheflame)\n` \u23e3 2,675,819 ` <@95618",
        "buttons_list": [
            "sirenoftheflame",
            "kofi.zx",
            "yahjenni",
            "vie7777",
            "spicy_er"
        ],
        "field_names": []
        },
        {
        "bot_id": "270904126974590976",
        "title": "\ud83c\udf8a store sale \ud83c\udf8a",
        "author_name": "",
        "footer_text": "",
        "content_match": "<@557496556270387201>",
        "description_match": "**-80%** for **dragon bucket bundle**\n-# until <t:1764374400:f>\n\n**-72%** for **",
        "buttons_list": [
            "view store"
        ],
        "field_names": []
        },
        {
        "bot_id": "270904126974590976",
        "title": "flasherz - free spirit",
        "author_name": "",
        "footer_text": "",
        "content_match": "",
        "description_match": "<a:omega2:901598549735784479> **omega 2**\n<:prestige3:573151027411419136> **pres",
        "buttons_list": [],
        "field_names": [
            "level",
            "gems",
            "showcase",
            "pets",
            "commands",
            "robbing",
            "collector",
            "fish",
            "friends"
        ]
        },
        {
        "bot_id": "270904126974590976",
        "title": "voting",
        "author_name": "",
        "footer_text": "",
        "content_match": "",
        "description_match": "> *check </advancements vote:1011560371041095694> to see the vote level rewards*",
        "buttons_list": [
            "discordbotlist",
            "top.gg",
            "freemium"
        ],
        "field_names": [
            "vote level"
        ]
        },
        {
        "bot_id": "899899858981371935",
        "title": "\ud83d\udcca server information",
        "author_name": "\u0b68\u0b67 \u318d/winnie\u0c68  social & giveaway",
        "footer_text": "requested by luminexwasgoat",
        "content_match": "",
        "description_match": "\ufe50               /winnie\ufe52\u0a6d\u09ce\ufe52\u2661\ufe52\ufe55       gws  social  tag\ufe52          join for your da",
        "buttons_list": [],
        "field_names": [
            "\ud83d\udcdc general info",
            "\ud83d\udc65 members & roles",
            "\ud83d\udc8e boost status",
            "\ud83d\udcc1 channels"
        ]
        },
        {
        "bot_id": "824119071556763668",
        "title": "time difference",
        "author_name": "",
        "footer_text": "showing difference between given id and command message id",
        "content_match": "",
        "description_match": "9.47 seconds",
        "buttons_list": [],
        "field_names": [
            "1443994122846212197",
            "1443994083143061627"
        ]
        }
    ]
    
    # --- Client Class ---
    class GiveawayAltClient(discord.Client):
        def __init__(self, manager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.manager = manager

        async def on_message(self, message):
            try:
                if self.manager:
                    await self.manager.process_message(message, self)
            except Exception as e:
                if self.manager:
                    self.manager.log(f"Critical error in client {self.user.name}: {e}", "ERROR")

    # --- Manager Class ---
    class GiveawayJoinerManager:
        
        def __init__(self, ui_elements, main_bot_client):
            self.ui = ui_elements
            self.bot = main_bot_client
            self.main_bot_id = main_bot_client.user.id
            self.pending_ticket_claims = {}
            self.running_clients = {}
            self.tokens = {}
            self.config = {}
            self.stats = {}
            self.history = {}
            self.bot_cache = {}
            self.cached_fp_patterns = []
            self.probed_messages_cache = {}
            self.input_debounce_task = None
            self.stat_saver_task = None
            self.server_save_task = None
            self.is_ready = None
            self.session = None
            self.history_lock = None
            self.stats_lock = None
            self.log_lock = threading.Lock()
            self.bot._gw_active_clients = self.running_clients

            # --- Paths ---
            self.scripts_path = getScriptsPath()
            self.data_dir = os.path.join(self.scripts_path, "json")
            self.logs_dir = os.path.join(self.scripts_path, "logs")
            
            self.config_path = os.path.join(self.data_dir, "giveaway_config.json")
            self.stats_path = os.path.join(self.data_dir, "giveaway_stats.json")
            self.history_path = os.path.join(self.data_dir, "giveaway_history.json")
            self.fp_patterns_path = os.path.join(self.data_dir, "giveaway_fp_patterns.json")
            self.log_path = os.path.join(self.logs_dir, "giveaway.log")
            
            self.tokens_path = os.path.join(self.data_dir, "giveaway_tokens.json")
            self.bot_cache_path = os.path.join(self.data_dir, "giveaway_bots_cache.json")

            self.flaresolverr_dir = os.path.normpath(os.path.join(self.scripts_path, "json", "flaresolverr"))
            self.flaresolverr_exe = os.path.normpath(os.path.join(self.flaresolverr_dir, "flaresolverr.exe"))

            self.default_config_gw = {
                "enabled": False,
                "monitored_bots": ["824119071556763668", "429457053791158281", "720351927581278219", "1245727635536085032", "270904126974590976", "155149108183695360", "159985870458322944", "1236347275052187688", "1363505774378225775", "368521195940741122", "563434444321587202", "530082442967646230", "294882584201003009"],
                "blacklist_keywords": ["ban", "kick", "mute", "timeout"],
                "join_delay_min": 2,
                "join_delay_max": 8,
                "webhook_url": "",
                "webhook_enabled": False,
                "webhook_mention_user": False,
                "webhook_mention_captcha": False,
                "webhook_mention_manual": False,
                "webhook_mention_ticket": False,
                "webhook_mention_requirements": False,
                "webhook_mention_token_fail": True,
                "webhook_disable_fail_join": False,
                "detection_keywords": ["giveaway", "sorteo", "🎉", "🎁", "gift", "premio", "raffle", "çekiliş", "concours", "dropped", "drop", "claim", "hediye", "concours", "cadeau", "gewinnspiel", "verlosung", "sorteio", "estrazione"],
                "require_button": True,
                "auto_detect_wins": True,
                "log_level": "INFO",
                "debug_mode": False,
                "component_target_user": "",
                "excluded_servers": [],
                "excluded_channels": [],
                "ticket_panel_detection_enabled": True,
                "prize_claim_enabled": True,
                "auto_claim_ticket_enabled": True,
                "auto_claim_dm_enabled": False,
                "ticket_wait_timeout": 3600,
                "auto_claim_send_message": False,
                "auto_claim_message": "Hello, I won the Giveaway",
                "auto_solve_captchas": False,
                "enable_alts_for_claiming": False,
                "flaresolverr_url": "http://localhost:8191",
                "flaresolverr_installed": False,
                "force_raw_fetch_bots": ["530082442967646230"]
            }
        
            self.prize_patterns = [
                re.compile(r"prize:?\s*\*\*(.+?)\*\*", re.IGNORECASE),
                re.compile(r"premio:?\s*\*\*(.+?)\*\*", re.IGNORECASE),
                re.compile(r"prize:?\s*(.+?)(?:\n|$)", re.IGNORECASE),
                re.compile(r"premio:?\s*(.+?)(?:\n|$)", re.IGNORECASE),
                re.compile(r"🎁\s*(.+?)(?:\n|$)", re.IGNORECASE),
                re.compile(r"🏆\s*(.+?)(?:\n|$)", re.IGNORECASE),
                re.compile(r"💎\s*(.+?)(?:\n|$)", re.IGNORECASE),
                re.compile(r"⭐\s*(.+?)(?:\n|$)", re.IGNORECASE)
            ]
            
            self.time_patterns = [
                re.compile(r"\d+[smhd]", re.IGNORECASE),
                re.compile(r"\d+\s*(second|minute|hour|day)", re.IGNORECASE),
                re.compile(r"\d+\s*(segundo|minuto|hora|día)", re.IGNORECASE),
                re.compile(r"<t:\d+:[RFfDdTt]>", re.IGNORECASE),
                re.compile(r"ends?:?\s*<t:\d+", re.IGNORECASE),
                re.compile(r"termina:?\s*<t:\d+", re.IGNORECASE),
                re.compile(r"finaliza:?\s*<t:\d+", re.IGNORECASE)
            ]
            
            self.win_prize_patterns = [
                re.compile(r"won\s+(?:the\s+)?(.+?)(?:\n|$|!|\.|,)", re.IGNORECASE),
                re.compile(r"ganaste\s+(?:el\s+|la\s+)?(.+?)(?:\n|$|!M\.|,)", re.IGNORECASE),
                re.compile(r"ha\s+ganado\s+(?:el\s+|la\s+)?(.+?)(?:\n|$|!|\.|,)", re.IGNORECASE),
                re.compile(r"prize[:\s]+(?:the\s+)?(.+?)(?:\n|$|!|\.|,)", re.IGNORECASE),
                re.compile(r"premio[:\s]+(?:el\s+|la\s+)?(.+?)(?:\n|$|!|\.|,)", re.IGNORECASE),
                re.compile(r"çekilişin ödülü[:\s]+(.+?)(?:\n|$|!|\.|,)", re.IGNORECASE),
                re.compile(r"prix[:\s]+(?:le\s+|la\s+)?(.+?)(?:\n|$|!|\.|,)", re.IGNORECASE),
                re.compile(r"lot[:\s]+(?:le\s+|la\s+)?(.+?)(?:\n|$|!|\.|,)", re.IGNORECASE),
                re.compile(r"récompense[:\s]+(?:le\s+|la\s+)?(.+?)(?:\n|$|!|\.|,)", re.IGNORECASE)
            ]
            
            self.hosted_patterns = [
                re.compile(r"hosted by:?\s*(.+?)(?:\n|$)", re.IGNORECASE),
                re.compile(r"organizado por:?\s*(.+?)(?:\n|$)", re.IGNORECASE),
                re.compile(r"host:?\s*(.+?)(?:\n|$)", re.IGNORECASE)
            ]
            
            self.mention_regex = re.compile(r'<[@#&!]\d+>')
            self.emoji_regex = re.compile(r'<:\w+:\d+>')
            self.channel_mention_regex = re.compile(r"<#\d+>")

            self.KNOWN_BOT_IDS = {
                "DYNO": "155149108183695360",
                "GIVEAWAY_BOAT": "530082442967646230",
                "INVITE_TRACKER": "720351927581278219",
                "Nekotina": "429457053791158281"
            }

        async def async_init_gw(self):
            self.history_lock = asyncio.Lock()
            self.stats_lock = asyncio.Lock()
            self.is_ready = asyncio.Event()
            self.session = aiohttp.ClientSession()
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.logs_dir, exist_ok=True)
            self.clear_giveaway_log()
            
            await self.load_config_gw()
            await self.load_stats()
            await self.load_history()
            await self.load_tokens()
            await self.load_bot_cache()
            self.load_fp_patterns(force_reload=True)

            main_username = self.bot.user.name
            main_avatar = self.bot.user.avatar.url if self.bot.user.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"

            if main_username not in self.tokens:
                self.tokens[main_username] = {
                    "token": self.bot.http.token, 
                    "valid": True, 
                    "date_added": "N/A (Main)",
                    "avatar_url": main_avatar,
                    "is_main": True
                }
            
            self.log(f"Giveaway Joiner V{__version__} initialized (UI Phase).", "SUCCESS")
            
            self.populate_ui_with_data()
            self.populate_bot_table_from_cache()
            self.bot.loop.create_task(self.start_tasks())
            
            self.is_ready.set()
        
        async def start_tasks(self):            
            self.log("Starting tasks (client login, cache verify)", "DEBUG")

            if self.session is None or self.session.closed:
                self.log("Session was closed or missing. Re-creating shared HTTP session.", "WARNING")
                self.session = aiohttp.ClientSession()
            await self.sync_token_data()
            if self.config.get("enabled", False):
                await self.start_all_clients()
            
            self.bot.loop.create_task(self.verify_bot_cache())
            if self.stat_saver_task and not self.stat_saver_task.done():
                self.stat_saver_task.cancel()
            self.stat_saver_task = self.bot.loop.create_task(self.periodic_stat_saver())
            self.log("Background tasks are running.", "DEBUG")

        # --- DATA MANAGEMENT ---
        def json_serializer_gw(self, obj):
            if hasattr(obj, 'value'): return obj.value
            if isinstance(obj, datetime): return obj.isoformat()
            try: return str(obj)
            except Exception: return f"[Non-serializable: {type(obj).__name__}]"

        async def load_json_gw(self, file_path, default_data={}):
            if not os.path.exists(file_path):
                return default_data
            try:
                def _sync_load():
                    with open(file_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                return await self.bot.loop.run_in_executor(None, _sync_load)
            except (json.JSONDecodeError, IOError) as e:
                self.log(f"[ERROR] Could not read file {file_path}: {e}", "ERROR")
                return default_data

        async def save_json_gw(self, file_path, data):
            try:
                def _sync_save():
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, default=self.json_serializer_gw)
                await self.bot.loop.run_in_executor(None, _sync_save)
            except (IOError, TypeError) as e:
                self.log(f"[ERROR] Could not write to file {file_path}: {e}", "ERROR")

        async def load_history(self):
            self.history = await self.load_json_gw(self.history_path)
        
        async def save_history(self):
            async with self.history_lock:
                data_snapshot = copy.deepcopy(self.history)
                await self.save_json_gw(self.history_path, data_snapshot)
        
        async def load_stats(self):
            default_stats = {
                "total_detected": 0, "total_joined": 0, "total_won": 0, 
                "total_filtered": 0, "total_captchas": 0, "total_scanned": 0, 
                "session_start": datetime.now().isoformat(), 
                "last_giveaway": None, "bot_stats": {}, "daily_stats": {}
            }
            self.stats = default_stats 

            if not os.path.exists(self.stats_path):
                return

            try:
                content = ""
                def _read():
                    with open(self.stats_path, "r", encoding="utf-8") as f:
                        return f.read().strip()
                
                content = await self.bot.loop.run_in_executor(None, _read)

                if not content: return

                try:
                    self.stats = json.loads(content)
                except json.JSONDecodeError:

                    try:
                        self.log("JSON corrupted detected. Using raw decoder...", "WARNING")
                        decoder = json.JSONDecoder()
                        self.stats, _ = decoder.raw_decode(content)
                        
                        self.log("JSON recovered successfully. Saving correction...", "SUCCESS")
                        await self.save_stats()
                        
                    except Exception as e:
                        self.log(f"JSON file is too corrupted (unrecoverable): {e}", "ERROR")
                        try: os.rename(self.stats_path, self.stats_path + ".corrupted")
                        except: pass

            except Exception as e:
                self.log(f"Error loading stats: {e}", "ERROR")

            for key, val in default_stats.items():
                if key not in self.stats:
                    self.stats[key] = val
        
        async def periodic_stat_saver(self):
            self.log("Starting periodic saving of statistics (60s)...", "DEBUG")
            while True:
                try:
                    await asyncio.sleep(60) 
                    await self.save_stats()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.log(f"Error in periodic statistics saving: {e}", "ERROR")

        async def save_stats(self):
            async with self.stats_lock:
                data_snapshot = copy.deepcopy(self.stats)
                await self.save_json_gw(self.stats_path, data_snapshot)

        async def load_config_gw(self):
            config = await self.load_json_gw(self.config_path, self.default_config_gw)
            was_modified = False

            for key, value in self.default_config_gw.items():
                if key not in config: 
                    config[key] = value
                    was_modified = True
            
            lists_to_clean = ["monitored_bots", "excluded_channels", "excluded_servers"]
            
            for list_key in lists_to_clean:
                if list_key in config and isinstance(config[list_key], list):
                    original_list = config[list_key]
                    cleaned_list = list(set(original_list))
                    
                    if len(cleaned_list) != len(original_list):
                        self.log(f"Found duplicates in '{list_key}'. Cleaning {len(original_list)} -> {len(cleaned_list)}...", "WARNING")
                        config[list_key] = cleaned_list
                        was_modified = True

            self.config = config
            self.excluded_servers_set = set(self.config.get("excluded_servers", []))

            if was_modified:
                await self.save_config_gw()
                self.log("Configuration file repaired and saved to disk.", "SUCCESS")
        
        async def save_config_gw(self):
            await self.save_json_gw(self.config_path, self.config)
            self.excluded_servers_set = set(self.config.get("excluded_servers", []))

        def load_fp_patterns(self, force_reload=False):
            if self.cached_fp_patterns and not force_reload:
                return self.cached_fp_patterns

            base_patterns = { (p.get("title"), p.get("author_name"), p.get("bot_id")): p for p in DEFAULT_FP_PATTERNS }
            user_patterns = []
            
            if os.path.exists(self.fp_patterns_path):
                try:
                    with open(self.fp_patterns_path, "r", encoding="utf-8") as f:
                        user_patterns = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"[ERROR] Could not read user FP patterns file: {e}")
            
            for pattern in user_patterns:
                key = (pattern.get("title"), pattern.get("author_name"), pattern.get("bot_id"))
                base_patterns[key] = pattern
            
            self.cached_fp_patterns = list(base_patterns.values())
            return self.cached_fp_patterns

        def save_fp_patterns(self, patterns_data):
            self.cached_fp_patterns = patterns_data
            def _write_file():
                try:
                    with open(self.fp_patterns_path, "w", encoding="utf-8") as f:
                        json.dump(patterns_data, f, indent=4)
                except IOError as e:
                    print(f"[ERROR] Could not write to FP patterns file: {e}")

            try:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(None, _write_file)
            except RuntimeError:
                _write_file()

        async def record_joined_giveaway(self, message, embed, prize, client):
            try:
                history_key = str(message.id)
                
                button_labels = []
                if message.components:
                    for row in message.components:
                        if hasattr(row, 'children'):
                            for child in row.children:
                                label = getattr(child, 'label', None)
                                emoji = getattr(child, 'emoji', None)
                                
                                if label:
                                    button_labels.append(str(label))
                                elif emoji:
                                    emoji_name = getattr(emoji, 'name', str(emoji))
                                    if emoji_name:
                                        button_labels.append(str(emoji_name))
                
                content_text = message.content if message.content else ""

                if history_key not in self.history:
                    self.history[history_key] = {
                        "message_id": str(message.id),
                        "channel_id": str(message.channel.id),
                        "guild_id": str(message.guild.id) if message.guild else None,
                        "bot_id": str(message.author.id),
                        "prize": prize,
                        "timestamp_first_joined": datetime.now().isoformat(),
                        "joined_accounts": [client.user.name],
                        "embed_data": embed.to_dict() if embed else None,
                        "message_content": content_text, 
                        "button_labels": button_labels
                    }
                    self.log(f"Recorded new joined giveaway to history: {message.id} | Account: {client.user.name}", "DEBUG")
                else:
                    if client.user.name not in self.history[history_key].get("joined_accounts", []):
                        self.history[history_key].setdefault("joined_accounts", []).append(client.user.name)
                        self.log(f"Added account {client.user.name} to history for giveaway {message.id}", "DEBUG")
                    else:
                        self.log(f"Account {client.user.name} already in history for {message.id}. Skipping save.", "DEBUG")
                        return

                await self.save_history()
            except Exception as e:
                self.log(f"Failed to record giveaway history for {message.id} | Account: {client.user.name} | Error: {e}", "ERROR")

        # --- LOGGING ---
        def log(self, message, level="INFO"):
            log_levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "SUCCESS": 4}
            current_log_level = self.config.get("log_level", "INFO")
            debug_mode = self.config.get("debug_mode", False)
            
            if level == "DEBUG" and not debug_mode: return
            if level != "DEBUG" and log_levels.get(level, 1) < log_levels.get(current_log_level, 1): return
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}"
            
            def _write_to_file():
                with self.log_lock: 
                    try:
                        with open(self.log_path, "a", encoding="utf-8") as f:
                            f.write(log_entry + "\n")
                    except Exception as e:
                        print(f"Logging error: {str(e)}")

            try:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(None, _write_to_file)
            except RuntimeError:
                _write_to_file()
                print(f"[WARNING] Logging failed in non-async context. Log entry: {log_entry}")

        def clear_giveaway_log(self):
            try:
                with open(self.log_path, "w", encoding="utf-8") as f: f.write("")
            except Exception as e: print(f"Error clearing giveaway log: {str(e)}")

        async def load_tokens(self):
            self.tokens = await self.load_json_gw(self.tokens_path)
            return self.tokens
        
        async def save_tokens(self):
            data_snapshot = copy.deepcopy(self.tokens)
            await self.save_json_gw(self.tokens_path, data_snapshot)
        
        async def load_bot_cache(self):
            self.bot_cache = await self.load_json_gw(self.bot_cache_path)
        
        async def save_bot_cache(self):
            data_snapshot = copy.deepcopy(self.bot_cache)
            await self.save_json_gw(self.bot_cache_path, data_snapshot)

        async def verify_token(self, token):
            headers = {"Authorization": token, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9015 Chrome/108.0.5359.215 Electron/22.3.2 Safari/537.36"}
            try:
                async with self.session.get("https://discord.com/api/v10/users/@me", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        user_id = user_data.get("id")
                        avatar_hash = user_data.get("avatar")
                        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png" if avatar_hash else "https://cdn.discordapp.com/embed/avatars/0.png"
                        username = user_data.get("username", "UnknownUser")
                        return True, username, avatar_url, user_id
                    else:
                        return False, f"Invalid (Status {response.status})", None, None
            except Exception as e:
                return False, f"Network Error ({e})", None, None

        async def add_token_to_storage(self, token):
            if token == self.bot.http.token:
                return "This is your main account token. It is added automatically."

            if not token:
                return "Token is empty."
            
            if any(data.get("token") == token for data in self.tokens.values()):
                return "This token is already added."
            is_valid, username_or_error, avatar_url = await self.verify_token(token) 
            
            if not is_valid:
                return f"Token verification failed: {username_or_error}"
            
            original_username = username_or_error
            username = original_username
            counter = 1
            while username in self.tokens:
                username = f"{original_username} ({counter})"
                counter += 1
            
            self.tokens[username] = {
                "token": token, 
                "valid": True, 
                "date_added": datetime.now().isoformat(),
                "avatar_url": avatar_url 
            }
            await self.save_tokens()
            
            self.log(f"Added and verified new token for: {username}", "SUCCESS")
            
            # If scanning is active, start this new client
            if self.config.get("enabled", False):
                await self.start_single_client(username, self.tokens[username])
            
            return f"Successfully added token for: {username}"

        async def sync_token_data(self):
            self.log("Syncing token data (Usernames & Avatars)...", "DEBUG")
            changes_made = False
            
            current_keys = list(self.tokens.keys())
            
            for stored_username in current_keys:
                data = self.tokens[stored_username]
                token = data.get("token")
                is_main = data.get("is_main", False)

                if not data.get("valid", True):
                    continue

                is_valid, discord_username, discord_avatar, _ = await self.verify_token(token)
                
                if is_valid:
                    if data.get("avatar_url") != discord_avatar:
                        self.tokens[stored_username]["avatar_url"] = discord_avatar
                        self.log(f"Updated avatar for {stored_username}", "DEBUG")
                        changes_made = True

                    if stored_username != discord_username and not is_main:
                        self.log(f"Username change detected: '{stored_username}' -> '{discord_username}'", "INFO")
                        
                        token_data = self.tokens[stored_username]
                        del self.tokens[stored_username]
                        self.tokens[discord_username] = token_data
                        
                        changes_made = True
                
                await asyncio.sleep(0.5)

            if changes_made:
                await self.save_tokens()
                await self.update_token_table_ui()
                await self.update_token_select_list()
                self.log("Token data synchronization complete. Saved changes.", "SUCCESS")
            else:
                self.log("Token data is up to date.", "DEBUG")

        async def import_tokens_from_nighty_config(self):
            added_count = 0
            skipped_count = 0
            failed_count = 0

            try:
                nighty_data = getConfigData()
                
                if not nighty_data:
                    return "The Nighty configuration could not be obtained (getConfigData returned empty)."

                logins = nighty_data.get("logins", {})
                if not logins:
                    return "No logins were found in the Nighty configuration."

                self.log(f"Starting import from Nighty Config ({len(logins)} found)", "INFO")

                for profile_name, login_data in logins.items():
                    token = login_data.get("token")
                    is_active_main = login_data.get("active", False)
                    if not token: continue

                    if is_active_main:
                        self.log(f"Import: Skipping active main account ({profile_name}).", "DEBUG")
                        continue

                    token_exists = False
                    for stored_user, stored_data in self.tokens.items():
                        if stored_data.get("token") == token:
                            token_exists = True
                            break
                    
                    if token_exists:
                        skipped_count += 1
                        continue

                    is_valid, username, avatar_url = await self.verify_token(token)
                    
                    if is_valid:
                        final_username = username
                        counter = 1
                        while final_username in self.tokens:
                            final_username = f"{username} ({counter})"
                            counter += 1

                        self.tokens[final_username] = {
                            "token": token,
                            "valid": True,
                            "date_added": datetime.now().isoformat(),
                            "avatar_url": avatar_url,
                            "imported_from": "nighty_config"
                        }
                        added_count += 1
                        self.log(f"Imported new token from Nighty: {final_username}", "SUCCESS")

                        if self.config.get("enabled", False):
                             await self.start_single_client(final_username, self.tokens[final_username])
                    else:
                        self.log(f"Invalid token found in Nighty config ({profile_name}): {username}", "WARNING")
                        failed_count += 1
                
                if added_count > 0:
                    await self.save_tokens()
                
                return f"Importation completed: {added_count} added, {skipped_count} duplicates, {failed_count} invalid."

            except Exception as e:
                self.log(f"Error importing from nighty.config: {e}", "ERROR")
                traceback.print_exc()
                return f"Critical error while reading configuration: {str(e)}"

        async def remove_token_from_storage(self, username):
            if username in self.running_clients:
                client_data = self.running_clients.pop(username)
                task = client_data.get("task")
                client = client_data.get("client")
                
                if task and not task.done():
                    task.cancel()
                    try:
                        await task 
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        self.log(f"Error waiting for task cancellation {username}: {e}", "DEBUG")
                
                if client and not client.is_closed():
                    try:
                        await client.close()
                        self.log(f"Successfully stopped client for {username}.", "INFO")
                    except Exception as e:
                        self.log(f"Error closing client {username}: {e}", "ERROR")
            
            if username in self.tokens:
                del self.tokens[username]
                await self.save_tokens()
                self.log(f"Removed token for {username} from storage.", "INFO")
                return True
                
            return False

        # --- CLIENT MANAGEMENT ---
        async def start_all_clients(self):
            if self.running_clients: 
                self.log("start_all_clients called, but clients are already running. Forcing stop before restart.", "WARNING")
                await self.stop_all_clients()
                self.log("Forced stop complete. Proceeding with restart.", "INFO")

            self.log("Starting all clients...", "INFO")
            
            active_count = 0
            for username, data in self.tokens.items():
                if data.get("valid", False):
                    success = await self.start_single_client(username, data)
                    if success:
                        active_count += 1
                        await asyncio.sleep(.2)
            
            self.log(f"Successfully started {active_count} clients (Main + Alts).", "SUCCESS")
            self.ui["status_toggle"].label = "Enable Giveaway Joiner (Running)"
            tab.toast(type="SUCCESS", title="Scrpt Enabled", description="All clients have been started.")
            self.log("Waiting 3s for clients to report guilds...", "DEBUG")
            await asyncio.sleep(3)
            await self.update_server_list_from_all_clients()

        async def start_single_client(self, username, token_data):
            token = token_data.get("token")
            
            if token_data.get("is_main", False):
                self.log(f"Attaching listener to main client, Account: {username}", "DEBUG")
                self.running_clients[username] = {"client": self.bot, "task": None} 
                return True
            
            alt_client = GiveawayAltClient(manager=self, chunk_guilds_at_startup=False, afk=True)
            
            async def client_runner():
                try:
                    self.log(f"Client {username} connecting (Persistent Session)", "INFO")
                    await alt_client.start(token)
                
                except discord.LoginFailure:
                    self.log(f"LOGIN FAILED, Account: {username}: Token is invalid or expired.", "ERROR")
                    self.bot.loop.create_task(self.send_unified_webhook(
                        title="❌ Token Login Failed",
                        description=f"**Account:** `{username}`\n**Error:** The token is improper or expired.",
                        color=0xED4245,
                        mention_type="token_fail"
                    ))
                    if username in self.tokens:
                        self.tokens[username]["valid"] = False
                        await self.save_tokens()
                        
                except Exception as e:
                    self.log(f"Client {username} crashed unexpectedly: {e}", "ERROR")
                
                finally:
                    if not alt_client.is_closed():
                        await alt_client.close()

            task = self.bot.loop.create_task(client_runner())
            
            try:
                self.log(f"Waiting for client {username} to become ready...", "DEBUG")
                await asyncio.wait_for(alt_client.wait_until_ready(), timeout=15.0)
            except asyncio.TimeoutError:
                self.log(f"Client {username} is taking too long to get ready. Continuing anyway...", "WARNING")
            
            if not alt_client.user:
                self.log(f"Client {username} failed to initialize user object properly.", "ERROR")
            
            self.running_clients[username] = {"client": alt_client, "task": task}
            return True

        async def stop_all_clients(self):
            self.log("Stopping all clients (Shutdown Phase)...", "INFO")
            tasks_to_cancel = []
            clients_to_close = []

            for username, data in self.running_clients.items():
                if data.get("is_main", False) or data.get("client") == self.bot:
                    continue

                task = data.get("task")
                if task and not task.done():
                    task.cancel()
                    tasks_to_cancel.append(task)
                
                client = data.get("client")
                if client and not client.is_closed():
                    clients_to_close.append(client)

            if tasks_to_cancel:
                self.log(f"Waiting for {len(tasks_to_cancel)} background tasks to cancel...", "DEBUG")
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
            
            if clients_to_close:
                self.log(f"Closing {len(clients_to_close)} alt client connections...", "DEBUG")
                close_routines = [client.close() for client in clients_to_close]
                await asyncio.gather(*close_routines, return_exceptions=True)
            
            self.running_clients.clear()
            
            if "status_toggle" in self.ui:
                self.ui["status_toggle"].label = "Enable Giveaway Joiner"
            
            self.log("All clients stopped and memory cleared.", "SUCCESS")

        async def shutdown_gw(self):
            self.log("Manager shutting down...", "WARNING")
            if self.stat_saver_task and not self.stat_saver_task.done():
                self.stat_saver_task.cancel()
                self.log("Periodic Stat Saver task cancelled.", "DEBUG")
            if self.is_ready:
                self.is_ready.clear()
            await self.stop_all_clients()
            if self.session and not self.session.closed:
                await self.session.close()
            
            self.log("Manager shutdown complete.", "SUCCESS")

        def refresh_ui_text(self):
            if hasattr(self.bot, '_giveaway_stats_text') and self.stats:
                total_detected = self.stats.get('total_detected', 0)
                total_scanned = self.stats.get('total_scanned', 0)
                total_joined = self.stats.get('total_joined', 0)
                total_won = self.stats.get('total_won', 0)
                
                success_rate = (total_joined / max(total_detected, 1)) * 100
                
                self.bot._giveaway_stats_text.content = (
                    f"• Messages analyzed: {total_scanned}\n"
                    f"• Detected: {total_detected}\n"
                    f"• Joined: {total_joined}\n"
                    f"• Won: {total_won}\n"
                    f"• Filtered: {self.stats.get('total_filtered', 0)}\n"
                    f"• Captchas: {self.stats.get('total_captchas', 0)}\n"
                    f"• Success Rate: {success_rate:.1f}%"
                )

        # --- STATS ---
        async def update_stats(self, event_type, bot_id=None, prize=None):
            async with self.stats_lock:
                today = datetime.now().strftime("%Y-%m-%d")
                
                if today not in self.stats["daily_stats"]:
                    self.stats["daily_stats"][today] = {"detected": 0, "joined": 0, "won": 0, "filtered": 0, "captchas": 0}
                
                if event_type == "detected":
                    self.stats["total_detected"] += 1
                    self.stats["daily_stats"][today]["detected"] += 1
                elif event_type == "joined":
                    self.stats["total_joined"] += 1
                    self.stats["daily_stats"][today]["joined"] += 1
                    self.stats["last_giveaway"] = datetime.now().isoformat()
                elif event_type == "won":
                    self.stats["total_won"] += 1
                    self.stats["daily_stats"][today]["won"] += 1
                elif event_type == "filtered":
                    self.stats["total_filtered"] += 1
                    self.stats["daily_stats"][today]["filtered"] += 1
                elif event_type == "captcha":
                    self.stats["total_captchas"] += 1
                    if "captchas" not in self.stats["daily_stats"][today]:
                         self.stats["daily_stats"][today]["captchas"] = 0
                    self.stats["daily_stats"][today]["captchas"] += 1
                
                if bot_id:
                    if bot_id not in self.stats["bot_stats"]:
                        self.stats["bot_stats"][bot_id] = {"detected": 0, "joined": 0, "won": 0}
                    if event_type in ["detected", "joined", "won"]:
                        self.stats["bot_stats"][bot_id][event_type] += 1
                
                await self.save_json_gw(self.stats_path, self.stats)
            
            self.refresh_ui_text()

        # --- GIVEAWAY DETECTION ---
        def extract_prize_from_embed(self, embed, client, message):
            if not embed: return ""
            detected_prize = ""
            
            if embed.description:
                description = embed.description
                for pattern in self.prize_patterns:
                    match = pattern.search(description)
                    if match:
                        prize_text = match.group(1).strip()
                        prize_text = self.mention_regex.sub('', prize_text) 
                        prize_text = self.emoji_regex.sub('', prize_text)
                        prize_text = prize_text.strip()
                        if prize_text:
                            detected_prize = prize_text
                            self.log(f"Prize detected in description: {detected_prize} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
                            break
            
            if not detected_prize and hasattr(embed, 'fields') and embed.fields:
                for field in embed.fields:
                    try:
                        field_name = str(field.name or '').lower()
                        field_value = str(field.value or '')
                        if any(keyword in field_name for keyword in ['prize', 'premio', 'reward', 'recompensa']):
                            prize_text = re.sub(r'\*\*(.+?)\*\*', r'\1', field_value)
                            prize_text = re.sub(r'<[@#&!]\d+>', '', prize_text)
                            prize_text = re.sub(r'<:\w+:\d+>', '', prize_text)
                            prize_text = prize_text.strip()
                            if prize_text:
                                detected_prize = prize_text
                                self.log(f"Prize detected in field '{field_name}': {detected_prize} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
                                break
                    except Exception as e:
                        self.log(f"Error processing embed field for prize: {e} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
            
            if not detected_prize and embed.title:
                title_lower = embed.title.lower()
                generic_titles = ['giveaway', 'sorteo', 'giveaway ended', 'sorteo terminado']
                if not any(generic in title_lower for generic in generic_titles):
                    detected_prize = embed.title
                    self.log(f"Prize detected in title: {detected_prize} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
            
            if not detected_prize and embed.description:
                lines = embed.description.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3 and len(line) < 100:
                        if not re.match(r'^[🎉🎁🏆💎⭐🎊\s]*$', line) and not re.search(r'<t:\d+:[RFfDdTt]>', line):
                            clean_line = re.sub(r'<[@#&!]\d+>', '', line)
                            clean_line = re.sub(r'<:\w+:\d+>', '', clean_line)
                            clean_line = clean_line.strip()
                            if clean_line and len(clean_line) > 3:
                                detected_prize = clean_line[:50]
                                self.log(f"Prize detected from description line (last resort): {detected_prize} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
                                break
            
            return self.sanitize_text(detected_prize)

        def is_giveaway_embed(self, embed, message, client):
            if not embed: return False, 0.0, ""
            
            try:
                patterns = self.load_fp_patterns()
                if patterns:
                    inc_title = (embed.title or "").lower().strip()
                    if not inc_title and embed.description:
                        inc_title = embed.description.split('\n')[0].lower().strip()[:80]
                    
                    inc_author = (embed.author.name or "").lower().strip() if embed.author else ""
                    inc_footer = (embed.footer.text or "").lower().strip() if embed.footer else ""
                    inc_bot_id = str(message.author.id)
                    
                    inc_msg_content = (message.content or "").lower()
                    inc_desc_content = (embed.description or "").lower()
                    inc_full_text = inc_msg_content + " " + inc_desc_content

                    inc_buttons = []
                    if message.components:
                        for row in message.components:
                            if hasattr(row, 'children'):
                                for child in row.children:
                                    if hasattr(child, 'label') and child.label:
                                        inc_buttons.append(child.label.lower())
                                    elif hasattr(child, 'emoji') and child.emoji:
                                        ename = getattr(child.emoji, 'name', str(child.emoji))
                                        if ename: inc_buttons.append(str(ename).lower())

                    inc_field_names = []
                    if embed.fields:
                        for f in embed.fields:
                            if f.name: inc_field_names.append(f.name.lower().strip())

                    for pattern in patterns:
                        p_bot_id = str(pattern.get("bot_id") or "")
                        if p_bot_id and p_bot_id != inc_bot_id: continue

                        p_title = (pattern.get("title") or "").lower().strip()
                        p_author = (pattern.get("author_name") or "").lower().strip()
                        p_footer = (pattern.get("footer_text") or "").lower().strip()                        
                        p_content = (pattern.get("content_match") or "").lower().strip()
                        p_desc = (pattern.get("description_match") or "").lower().strip()                        
                        p_field_names = pattern.get("field_names", [])                   
                        p_btns = pattern.get("buttons_list", [])
                        p_btn_single = (pattern.get("button_match") or "").lower().strip()
                        forbidden_btns = set(p_btns)
                        if p_btn_single: forbidden_btns.add(p_btn_single)

                        score = 0
                        max_score = 0 
                        
                        matched_strong_indicators = 0
                        matched_text_indicators = 0

                        if p_footer:
                            max_score += 1
                            if p_footer in inc_footer:
                                score += 1
                                matched_strong_indicators += 1

                        if forbidden_btns:
                            max_score += 1
                            if any(b in forbidden_btns for b in inc_buttons):
                                score += 1
                                matched_strong_indicators += 1

                        if p_field_names:
                            max_score += 1 
                            matches = 0
                            for pf in p_field_names:
                                if any(pf in inf for inf in inc_field_names): matches += 1
                            if len(p_field_names) > 0 and (matches / len(p_field_names)) >= 0.7:
                                score += 1
                                matched_strong_indicators += 1

                        if p_content:
                            max_score += 1
                            if p_content in inc_msg_content:
                                score += 1
                                matched_text_indicators += 1
                            elif p_content in inc_full_text:
                                score += 0.5
                                matched_text_indicators += 0.5

                        if p_desc:
                            max_score += 1
                            if p_desc in inc_desc_content:
                                score += 1
                                matched_text_indicators += 1

                        strong_id = (matched_strong_indicators >= 1) or (matched_text_indicators >= 1)
                        
                        if p_title:
                            if not strong_id: max_score += 1
                            if p_title in inc_title: 
                                if not strong_id: score += 1 
                                else: score += 0.5

                        if p_author:
                            if not strong_id: max_score += 1
                            if p_author == inc_author: 
                                if not strong_id: score += 1
                                else: score += 0.5

                        if max_score > 0:
                            match_percentage = score / max_score
                            
                            threshold = 0.50 if strong_id else 0.60

                            if match_percentage >= threshold:
                                log_msg = f"Embed skipped: Match ({match_percentage:.0%}) | ID: {p_bot_id}"
                                
                                if p_title: log_msg += f" | Title: '{p_title}'"
                                if p_author: log_msg += f" | Author: '{p_author}'"
                                if p_footer: log_msg += f" | Footer: '{p_footer}'"
                                if p_content: log_msg += f" | Content: '{p_content}'"
                                if p_desc: log_msg += f" | Desc: '{p_desc}'"
                                if p_btns: log_msg += f" | Btns: [{', '.join(p_btns)}]"
                                if p_field_names: log_msg += f" | Fields: [{', '.join(p_field_names)}]"
                                
                                log_msg += f" | Account: {client.user.name}"
                                self.bot.loop.create_task(self.update_stats("filtered", p_bot_id))
                                
                                self.log(log_msg, "INFO")
                                return False, 0.0, ""

            except Exception as e:
                self.log(f"Error checking False Positive patterns: {e} | Account: {client.user.name} | Error: {e}", "ERROR")

            if hasattr(embed, 'flags') and embed.flags and (embed.flags & 64): 
                self.log(f"Embed is ephemeral - skipping giveaway detection | Account: {client.user.name}", "DEBUG")
                return False, 0.0, ""
            
            confidence = 0.0
            title = (embed.title or "").lower()
            description = (embed.description or "").lower()
            content = f"{title} {description}"
            
            field_content_for_check = ""
            if hasattr(embed, 'fields') and embed.fields:
                for field in embed.fields:
                    try:
                        if hasattr(field, 'name') and field.name: field_content_for_check += f" {str(field.name).lower()}"
                        if hasattr(field, 'value') and field.value: field_content_for_check += f" {str(field.value).lower()}"
                    except Exception as e:
                        self.log(f"Error processing field content: {e} | Account: {client.user.name}", "DEBUG")
            content += field_content_for_check

            for keyword in self.config["detection_keywords"]:
                if keyword.lower() in content:
                    confidence += 0.3
                    self.log(f"Giveaway keyword detected: {keyword} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
            
            giveaway_indicators = ["winner", "ganador", "ends", "termina", "react", "reacciona", "prize", "premio", "free", "gratis", "enter", "participa", "hosted by", "entries", "winners", "requisitos", "requirements", "participantes", "creador:", "ganadores:", "participantes:", "kazanan", "katılmak", "gagnant", "se termine", "finit", "prix", "lot", "participer", "récompense", "gewinner", "endet", "teilnehmen", "reagiere", "teilnehmer", "vencedor", "acaba", "reaja", "participar", "vincitore", "partecipa"]
            for indicator in giveaway_indicators:
                if indicator in title: confidence += 0.1
                if indicator in description: confidence += 0.1
                        
            if hasattr(embed, 'fields') and embed.fields:
                for field in embed.fields:
                    try:
                        field_name = str(field.name or '')
                        field_value = str(field.value or '')
                        field_content = f"{field_name} {field_value}".lower()
                        
                        field_indicators = ["entries", "winners", "ends", "termina", "hosted by", "requirements", "requisitos", "çekiliş", "kazanan", "katılmak", "gagnant", "se termine", "finit", "prix", "lot", "participer", "récompense"]
                        for indicator in field_indicators:
                            if indicator in field_content: confidence += 0.15
                        
                        for pattern in self.time_patterns:
                            if pattern.search(field_value):
                                confidence += 0.15
                    except Exception as e:
                        self.log(f"Error processing embed field: {e}", "DEBUG")
            
            if (message.components and len(message.components) > 0) or "button" in content or "click" in content:
                confidence += 0.1
            
            giveaway_emojis = ["🎉", "🎁", "🏆", "💎", "⭐", "🎊"]
            for emoji in giveaway_emojis:
                if emoji in content: confidence += 0.2
            
            detected_prize = self.extract_prize_from_embed(embed, client, message)
            
            for pattern in self.time_patterns:
                if pattern.search(content):
                    confidence += 0.15
            
            if detected_prize and confidence >= 0.15: confidence += 0.2
            is_giveaway = confidence >= 0.50
            self.log(f"Giveaway detection - Confidence: {confidence:.2f}, Is Giveaway: {is_giveaway} | Prize: {detected_prize} | message ID: {message.id} | Account: {client.user.name}", "DEBUG")
            return is_giveaway, confidence, detected_prize

        def passes_blacklist_filter(self, prize_text):
            if not prize_text: return True
            prize_lower = prize_text.lower()
            for keyword in self.config["blacklist_keywords"]:
                if keyword.lower() in prize_lower:
                    self.log(f"Giveaway filtered by blacklist keyword: {keyword}", "INFO")
                    return False
            return True

        # --- TICKET PANEL DETECTION ---
        def is_ticket_panel_embed(self, embed, message, client):
            if not embed: return False, 0.0
            confidence = 0.0
            title = (embed.title or "").lower()
            description = (embed.description or "").lower()
            footer_text = (embed.footer.text or "").lower() if embed.footer else ""
            author_name = (embed.author.name or "").lower() if embed.author else ""
            full_text = f"{title} {description} {footer_text} {author_name}"

            strong_keywords = ["create ticket", "open ticket", "ticket tool", "tickety", "create a ticket", "open a support ticket", "contact us", "tickets"]
            for keyword in strong_keywords:
                if keyword in full_text:
                    confidence += 0.6
                    self.log(f"Ticket Panel: Strong keyword '{keyword}' found. | Account: {client.user.name}", "DEBUG")
                    break
            
            medium_keywords = ["ticket", "support", "soporte", "contact", "technical support", "consultation"]
            if confidence < 0.5:
                for keyword in medium_keywords:
                    if keyword in full_text:
                        confidence += 0.3
                        self.log(f"Ticket Panel: Medium keyword '{keyword}' found. | Account: {client.user.name}", "DEBUG")
                        break
            
            has_components = message.components and len(message.components) > 0
            if has_components and confidence > 0.0:
                self.log(f"Ticket Panel: Has components and text match. Boosting confidence. | Account: {client.user.name}", "DEBUG")
                confidence += 0.5
            elif has_components and (title or description):
                component_text = ""
                try:
                    for row in message.components:
                        if hasattr(row, 'children'):
                            for comp in row.children:
                                if hasattr(comp, 'label') and comp.label: component_text += comp.label.lower() + " "
                                if hasattr(comp, 'options') and comp.options:
                                    for opt in comp.options:
                                        if hasattr(opt, 'label') and opt.label: component_text += opt.label.lower() + " "
                                        if hasattr(opt, 'description') and opt.description: component_text += opt.description.lower() + " "
                except Exception as e:
                    self.log(f"Ticket Panel: Error parsing component text: {e}", "DEBUG")
                
                component_keywords = ["support", "purchase", "hwid", "reseller", "apply", "consultation", "tech", "pre-sale", "giveaway"]
                for keyword in component_keywords:
                    if keyword in component_text:
                        confidence += 0.4
                        self.log(f"Ticket Panel: Component keyword '{keyword}' found. | Account: {client.user.name}", "DEBUG")
                        break

            if "tickettool.xyz" in footer_text or "tickety.top" in footer_text:
                confidence += 0.3
                self.log(f"Ticket Panel: Known footer text found. | Account: {client.user.name}", "DEBUG")

            is_panel = confidence >= 0.5
            self.log(f"Ticket Panel Detection - Confidence: {confidence:.2f}, Is Panel: {is_panel} | Account: {client.user.name}", "DEBUG")
            return is_panel, confidence

        async def find_and_click_weighted_ticket(self, target_channel_id, prize, message, client):
            KEYWORD_WEIGHTS = {
                "claim": 10, "prize": 10, "reclamar": 10, "premio": 10, "won": 9, "ganaste": 9,
                "support": 5, "soporte": 5, "general": 4, "open": 3, "create": 3, "ticket": 2,
                "purchase": 1, "comprar": 1, "hwid": 1, "license": 1,
                "report": -5, "ban": -5, "appeal": -5, "close": -10
            }
            try:
                channel = await client.fetch_channel(int(target_channel_id))
                if not channel:
                    self.log(f"Weighted Ticket: Could not find channel {target_channel_id}", "ERROR")
                    return "manual_required", None
            except Exception as e:
                self.log(f"Weighted Ticket: Error fetching channel {target_channel_id}: {e}", "ERROR")
                return "manual_required", None

            panel_message_data = None
            clickable_options = []
            
            try:
                self.log(f"Weighted Ticket: Scanning history in #{channel.name}... | Account: {client.user.name}", "DEBUG")
                async for msg_stub in channel.history(limit=25):
                    if not msg_stub.author.bot: continue
                    try:
                        # Use the specific client's HTTP methods
                        msg_data = await client.http.get_message(channel.id, msg_stub.id)
                    except Exception as http_e:
                        self.log(f"Weighted Ticket: Could not http_get msg {msg_stub.id}: {http_e} | Account: {client.user.name}", "DEBUG")
                        continue
                    
                    if "components" in msg_data and msg_data["components"]:
                        panel_message_data = msg_data
                        self.log(f"Weighted Ticket: Found panel message {panel_message_data['id']} | Account: {client.user.name}", "DEBUG")
                        break
                
                if not panel_message_data:
                    self.log(f"Weighted Ticket: Could not find a panel message with components in #{channel.name}", "ERROR")
                    return "manual_required", None

                msg_id_str = str(panel_message_data["id"])
                app_id_str = str(panel_message_data["author"]["id"])
                
                for row_data in panel_message_data["components"]:
                    if "components" not in row_data: continue
                    for comp_data in row_data["components"]:
                        comp_type = comp_data.get('type', 0)
                        custom_id = comp_data.get('custom_id', None)
                        if not custom_id: continue
                        if comp_type == 2: # Button
                            label = comp_data.get('label', '').lower()
                            clickable_options.append({"type": "button", "text": label, "action_data": {"component_type": 2, "custom_id": custom_id}})
                        elif comp_type == 3: # Select Dropdown
                            placeholder = comp_data.get('placeholder', '').lower()
                            for opt in comp_data.get('options', []):
                                opt_label = opt.get('label', '').lower()
                                opt_desc = opt.get('description', '').lower()
                                opt_value = opt.get('value', None)
                                if not opt_value: continue
                                clickable_options.append({"type": "dropdown_option", "text": f"{placeholder} {opt_label} {opt_desc}", "action_data": {"component_type": 3, "custom_id": custom_id, "values": [opt_value]}})

                if not clickable_options:
                    self.log(f"Weighted Ticket: Panel message found, but no clickable options (buttons/menus). | Account: {client.user.name}", "WARNING")
                    return "manual_required", None
                
                if len(clickable_options) == 1:
                    self.log(f"Weighted Ticket: Only one option found. Clicking it. | Account: {client.user.name}", "INFO")
                    best_option = clickable_options[0]
                else:
                    self.log(f"Weighted Ticket: {len(clickable_options)} options found. Calculating scores... | Account: {client.user.name}", "DEBUG")
                    best_score = -float('inf')
                    best_option = None
                    for option in clickable_options:
                        current_score = 0
                        option_text = option["text"]
                        for keyword, weight in KEYWORD_WEIGHTS.items():
                            if keyword in option_text: current_score += weight
                        self.log(f"Weighted Ticket: Option '{option_text[:50]}' scored {current_score}", "DEBUG")
                        if current_score > best_score:
                            best_score = current_score
                            best_option = option
                    
                    if best_score <= 0:
                        self.log(f"Weighted Ticket: No option scored > 0. Requiring manual join. | Account: {client.user.name}", "WARNING")
                        return "manual_required", None
                    self.log(f"Weighted Ticket: Best option found: '{best_option['text']}' (Score: {best_score}) | Account: {client.user.name}", "SUCCESS")

                if not client.ws or not client.ws.session_id:
                    self.log(f"Weighted Ticket: FAILED. WebSocket session not ready/None. | Account: {client.user.name}", "ERROR")
                    return "click_failed", None
                
                real_session_id = client.ws.session_id
                interaction_data = {"type": 3, "channel_id": str(channel.id), "message_id": msg_id_str, "session_id": real_session_id, "application_id": app_id_str, "guild_id": str(channel.guild.id) if channel.guild else None, "data": best_option["action_data"]}

                def check_ticket_reply(msg):
                    try:
                        if msg.author.id != int(app_id_str): return False
                        if msg.channel.id != channel.id: return False
                        if not (hasattr(msg, 'flags') and msg.flags and (msg.flags.value & 64)): return False
                        content = msg.content.lower()
                        embed_desc = msg.embeds[0].description.lower() if msg.embeds and msg.embeds[0].description else ""
                        if ("ticket created" in content or "ticket created" in embed_desc or self.channel_mention_regex.search(content) or self.channel_mention_regex.search(embed_desc) or "ticket limit reached" in content or "you already have" in content):
                            self.log("Weighted Ticket: Ephemeral reply detected.", "DEBUG")
                            return True
                        return False
                    except Exception: return False

                # Use the specific client's loop and wait_for
                new_message_task = client.loop.create_task(client.wait_for("message", check=check_ticket_reply, timeout=10.0))
                edited_message_task = client.loop.create_task(client.wait_for("message_edit", check=lambda before, after: check_ticket_reply(after), timeout=10.0))

                click_success = False
                route = Route("POST", "/interactions")

                try:
                    await client.http.request(route, json=interaction_data)
                    
                    self.log(f"Weighted Ticket: Interaction sent successfully. | Account: {client.user.name}", "SUCCESS")
                    click_success = True

                except discord.HTTPException as e:
                    self.log(f"Weighted Ticket: API Error {e.status} - {e.text} | Account: {client.user.name}", "ERROR")
                    if not new_message_task.done(): new_message_task.cancel()
                    if not edited_message_task.done(): edited_message_task.cancel()
                    return "click_failed", None

                except Exception as e:
                    self.log(f"Weighted Ticket: Connection Error: {e} | Account: {client.user.name}", "ERROR")
                    if not new_message_task.done(): new_message_task.cancel()
                    if not edited_message_task.done(): edited_message_task.cancel()
                    return "click_failed", None
                
                if click_success:
                    try:
                        done, pending = await asyncio.wait([new_message_task, edited_message_task], return_when=asyncio.FIRST_COMPLETED)
                        reply_message = None
                        if done:
                            result = done.pop().result()
                            reply_message = result[1] if isinstance(result, tuple) else result
                        for task in pending: task.cancel()

                        if reply_message:
                            content = reply_message.content.lower()
                            embed_desc = reply_message.embeds[0].description.lower() if reply_message.embeds and reply_message.embeds[0].description else ""
                            if "ticket limit reached" in content or "you already have" in content:
                                self.log(f"Weighted Ticket: Detected 'Ticket limit reached' reply. | Account: {client.user.name}", "WARNING")
                                return "limit_reached", None
                            
                            new_ticket_id = self.parse_channel_link(reply_message.content)
                            if not new_ticket_id and reply_message.embeds and reply_message.embeds[0].description:
                                 new_ticket_id = self.parse_channel_link(reply_message.embeds[0].description)
                            
                            if new_ticket_id:
                                self.log(f"Weighted Ticket: Successfully parsed new ticket channel: <#{new_ticket_id}> | Account: {client.user.name}", "SUCCESS")
                                return "success", new_ticket_id
                            else:
                                self.log(f"Weighted Ticket: Caught reply, but couldn't parse ticket ID. | Account: {client.user.name}", "WARNING")
                                return "success", None
                        else:
                            self.log(f"Weighted Ticket: Click succeeded, no ephemeral reply caught (Timeout). | Account: {client.user.name}", "DEBUG")
                            return "success", None 
                    
                    except (asyncio.TimeoutError, asyncio.CancelledError):
                        self.log(f"Weighted Ticket: Listener timed out waiting for reply. | Account: {client.user.name}", "DEBUG")
                        return "success", None
                    except Exception as e:
                        self.log(f"Weighted Ticket: Error processing listener reply: {e} | Account: {client.user.name}", "ERROR")
                        return "success", None
                return "click_failed", None
            except Exception as e:
                self.log(f"Weighted Ticket: Unhandled error: {e} | Account: {client.user.name}", "ERROR")
                traceback.print_exc()
                return "click_failed", None

        def has_dm_instruction(self, text):
            if not text: return False
            text = text.lower()
            triggers = [
                "dm me", "send me a dm", "message me", "pm me", "direct message me", 
                "dm host", "dm the host", "send dm", "send dm to", "send a message to",
                "envia md", "manda md", "escribeme al privado", "mensaje directo", 
                "envía dm", "manda dm", "md al host", "abre md", "abre dm",
                "mp moi", "envoyer un mp", "senden sie eine dm", "dm at", "dm @"
            ]
            return any(t in text for t in triggers)

        async def attempt_auto_dm_claim(self, message, client, prize):
            try:
                target_user = None
                
                if message.mentions:
                    valid_mentions = [u for u in message.mentions if u.id != client.user.id]
                    if valid_mentions:
                        target_user = valid_mentions[0]
                        self.log(f"Auto-DM: Message mentions {target_user.name}. Target locked.", "DEBUG")
                
                if not target_user:
                    target_user = message.author
                    self.log(f"Auto-DM: No specific mention found. Targeting message author ({target_user.name}).", "DEBUG")

                claim_msg = self.config.get("auto_claim_message", "Hello, I won the giveaway!").strip()
                if not claim_msg:
                    claim_msg = "Hello! I won the giveaway"

                if not getattr(target_user, 'dm_channel', None):
                    await target_user.create_dm()
                
                typing_duration = min(len(claim_msg) / 5, 6.0)
                typing_duration = max(2.0, typing_duration)
                                
                async with target_user.dm_channel.typing():
                    await asyncio.sleep(typing_duration)

                self.log(f"Auto-DM: Sending DM to {target_user.name}...", "INFO")
                await target_user.send(claim_msg)
                
                self.log(f"Auto-DM: SUCCESS. DM sent to {target_user.name} | Account: {client.user.name}", "SUCCESS")
                return "success", target_user

            except discord.HTTPException as e:
                if e.status == 400 and (e.code == -1 or "captcha" in str(e).lower()):
                    self.log(f"Auto-DM: Discord (Captcha Required). | Account: {client.user.name}", "ERROR")
                    self.bot.loop.create_task(self.send_unified_webhook(
                        title="Auto-DM Blocked (Captcha)", 
                        description=f"**🎁 Prize:** {prize}\n**❌ Error:** Discord requires Captcha verification.\n**⚠️ Action:** Login manually to `{client.user.name}` and send a DM to solve it.", 
                        color=0xFF0000, 
                        mention_type="token_fail", 
                        message=message, 
                        client=client
                    ))
                    return "captcha", target_user
                else:
                    self.log(f"Auto-DM: HTTP Error sending DM: {e}", "ERROR")
                    return "failed", target_user

            except discord.Forbidden:
                self.log(f"Auto-DM: FAILED. Cannot send DM to {target_user.name} (Closed DMs).", "ERROR")
                return "failed", target_user
            except Exception as e:
                self.log(f"Auto-DM: FAILED with error: {e}", "ERROR")
                return "failed", None

        # --- REACTION SYSTEM ---
        async def add_giveaway_reaction(self, message, client):
            giveaway_emojis = ["🎉", "🎁", "🏆", "✨", "🎊", "🔥", "💎", "⭐"]
            
            initial_delay = random.uniform(self.config["join_delay_min"], self.config["join_delay_max"])
            self.log(f"Giveaway Reaction - Waiting {initial_delay:.1f}s before checking... | Account: {client.user.name}", "DEBUG")
            await asyncio.sleep(initial_delay)

            max_retries = 3
            
            for attempt in range(1, max_retries + 1):
                try:
                    try:
                        message = await message.channel.fetch_message(message.id)
                    except Exception as e:
                        self.log(f"Giveaway Reaction - Fetch error (Attempt {attempt}): {e} | Account: {client.user.name}", "DEBUG")

                    if message.reactions:
                        target_emoji = None
                        
                        for reaction in message.reactions:
                            try:
                                if reaction.me:
                                    self.log(f"Giveaway Reaction - Already reacted to {str(reaction.emoji)} | Account: {client.user.name}", "DEBUG")
                                    return True

                                async for user in reaction.users(limit=50):
                                    if user.id == message.author.id or user.bot:
                                        target_emoji = reaction.emoji
                                        reactor_name = user.name
                                        self.log(f"Giveaway Reaction - Found Valid Bot reaction ({reactor_name}): {str(target_emoji)} | Account: {client.user.name}", "DEBUG")
                                        break
                                if target_emoji: break
                            except Exception: continue
                        
                        if not target_emoji:
                            for reaction in message.reactions:
                                if str(reaction.emoji) in giveaway_emojis:
                                    target_emoji = reaction.emoji
                                    self.log(f"Giveaway Reaction - Found Standard emoji: {str(target_emoji)} Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
                                    break
                        
                        # 3. Intentar unirse
                        if target_emoji:
                            try:
                                await message.add_reaction(target_emoji)
                                self.log(f"Giveaway Reaction - SUCCESS: Added reaction {str(target_emoji)} Message ID: {message.id} | Account: {client.user.name}", "INFO")
                                return True
                            except Exception as e:
                                self.log(f"Giveaway Reaction - Error adding reaction: {e} | Message ID: {message.id} | Account: {client.user.name}", "ERROR")
                                return False
                    
                    if attempt < max_retries:
                        self.log(f"Giveaway Reaction - No reaction found yet. Retrying in 2s (Attempt {attempt}/{max_retries})... Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
                        await asyncio.sleep(1.0)
                
                except Exception as e:
                    self.log(f"Giveaway Reaction loop error: {e} Message ID: {message.id} | Account: {client.user.name}", "ERROR")

            self.log(f"Giveaway Reaction - FAILED: Timed out looking for a valid reaction. Message ID: {message.id} | Account: {client.user.name}", "INFO")
            return False

        # --- BUTTON INTERACTION SYSTEM ---
        async def click_giveaway_button(self, message, client, specific_components=None):
            try:
                components_source = specific_components if specific_components else getattr(message, 'components', [])
                
                if not components_source or len(components_source) == 0:
                    return False
                
                target_custom_id = None
                button_labels = ["join", "enter", "participate", "🎉", "🎁", "unirse", "participar", "katılmak", "participer", "rejoindre", "claim", "drop", "vote"]
                seen_labels = []

                for row in components_source:
                    children = []
                    if hasattr(row, 'children'): children = row.children
                    elif isinstance(row, dict): children = row.get('components', [])
                    
                    for button in children:
                        label = (getattr(button, 'label', "") or (button.get('label', "") if isinstance(button, dict) else "")).lower()
                        emoji = getattr(button, 'emoji', None) or (button.get('emoji') if isinstance(button, dict) else None)
                        custom_id = getattr(button, 'custom_id', None) or (button.get('custom_id') if isinstance(button, dict) else None)
                        disabled = getattr(button, 'disabled', False) if hasattr(button, 'disabled') else (button.get('disabled', False) if isinstance(button, dict) else False)

                        emoji_str = str(emoji) if emoji else ""
                        if isinstance(emoji, dict): emoji_str = emoji.get('name', "")

                        seen_labels.append(f"'{label}' (ID: {custom_id})")

                        if disabled: continue
                        
                        if any(l in label for l in button_labels) or any(e in emoji_str for e in ["🎉", "🎁", "🏆"]):
                             target_custom_id = custom_id
                             break
                    if target_custom_id: break
                
                if not target_custom_id:
                    self.log(f"Button Click Failed: No matching button found. Saw buttons: {', '.join(seen_labels)} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
                    return False
                
                self.log(f"Giveaway Button Click - Attempting to join (CustomID: {target_custom_id}) | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")

                payload = {
                    "type": 3,
                    "guild_id": str(message.guild.id) if message.guild else None,
                    "channel_id": str(message.channel.id),
                    "message_id": str(message.id),
                    "application_id": str(message.author.id),
                    "session_id": client.ws.session_id,
                    "data": {
                        "component_type": 2,
                        "custom_id": target_custom_id
                    }
                }
                
                await client.http.request(Route("POST", "/interactions"), json=payload)
                self.log(f"Giveaway Button Click - SUCCESS: Joined giveaway (CustomID: {target_custom_id}) | Message ID: {message.id} | Account: {client.user.name}", "INFO")
                return True
                
            except Exception as e:
                self.log(f"Giveaway Button Click Error - {str(e)} | Message ID: {message.id} | Account: {client.user.name}", "ERROR")
                return False

        # --- CAPTCHA TASK ---
        async def wait_for_captcha_task(self, message, client):
            def check_for_ephemeral(msg):
                try:
                    if msg.channel.id != message.channel.id: return False
                    if msg.author.id != message.author.id: return False
                    if not (hasattr(msg, 'flags') and msg.flags is not None): return False
                    flags_value = msg.flags.value if hasattr(msg.flags, 'value') else msg.flags
                    if not (flags_value & 64): return False
                    return True
                except Exception: return False
            
            try:
                # Use the specific client to wait for the message
                ephemeral_msg = await client.wait_for("message", check=check_for_ephemeral, timeout=10.0)                
                self.log(f"Ephemeral message {ephemeral_msg.id} caught. Waiting 2.0s for embeds... | Account: {client.user.name}", "DEBUG")
                await asyncio.sleep(2.0)
                
                if self.is_captcha_message(ephemeral_msg):
                    self.log(f"Captcha message detected! Message ID: {ephemeral_msg.id} | Account: {client.user.name}", "INFO")
                    await self.update_stats("captcha", str(ephemeral_msg.author.id))
                    
                    captcha_url = None
                    if ephemeral_msg.components and hasattr(ephemeral_msg.components[0], 'children'):
                        button = ephemeral_msg.components[0].children[0]
                        if hasattr(button, 'url'): captcha_url = button.url

                    gw_boat_id = self.KNOWN_BOT_IDS["GIVEAWAY_BOAT"]
                    can_auto_solve = (self.config.get("auto_solve_captchas", False) and str(ephemeral_msg.author.id) == gw_boat_id and captcha_url)
                    
                    if not can_auto_solve:
                        desc_parts = [f"A giveaway requires manual verification.", f"**🤖 Bot:** {ephemeral_msg.author.name}", f"**💻 Server:** {ephemeral_msg.guild.name if ephemeral_msg.guild else 'DM'}"]
                        if captcha_url: desc_parts.append(f"\n**🔗 [Click Here to Verify]({captcha_url})**")
                        if self.config.get("auto_solve_captchas", False) and str(ephemeral_msg.author.id) != gw_boat_id:
                            desc_parts.append(f"\n*(Auto-solve skipped: Not Giveaway Boat)*")
                        
                        self.bot.loop.create_task(self.send_unified_webhook(
                            title="⚠️ Captcha Required!", 
                            description="\n".join(desc_parts), 
                            color=0xFFA500, mention_type="captcha", 
                            footer_text=f"Giveaway Joiner V{__version__} • Captcha", 
                            message=ephemeral_msg, 
                            client=client
                        ))
                        if hasattr(self.bot, '_giveaway_joiner_tab'):
                            self.bot._giveaway_joiner_tab.toast(type="INFO", title="⚠️ Captcha Required!", description=f"Bot {ephemeral_msg.author.name} requires verification.")
                        return

                    max_attempts = 3
                    edit_detected = False
                    for attempt in range(1, max_attempts + 1):
                        self.log(f"Captcha Solver: Attempt {attempt}/{max_attempts} for {captcha_url} | Account: {client.user.name}", "INFO")
                        edit_task = None
                        solution_success = False
                        try:
                            def check_edit_captcha(before, after):
                                if after.id != ephemeral_msg.id: return False
                                if (before.embeds and after.embeds and hasattr(before.embeds[0], 'description') and hasattr(after.embeds[0], 'description') and before.embeds[0].description != after.embeds[0].description): return True
                                if before.content != after.content: return True
                                if before.components != after.components: return True
                                return False

                            edit_task = asyncio.create_task(client.wait_for("message_edit", check=check_edit_captcha, timeout=70.0))
                            self.log(f"Attempt {attempt}: Edit listener started.", "DEBUG")
                            
                            solution_success = await self.solve_captcha_task(captcha_url, client)
                            if not solution_success:
                                continue

                            self.log(f"Attempt {attempt}: Solver succeeded. Checking for edit... | Account: {client.user.name}", "DEBUG")
                            edited_msg = None
                            if edit_task.done() and not edit_task.exception():
                                edited_msg_tuple = edit_task.result()
                                edited_msg = edited_msg_tuple[1]
                                self.log(f"Attempt {attempt}: Edit detected. | Account: {client.user.name}", "DEBUG")
                            elif not edit_task.done():
                                self.log(f"Attempt {attempt}: Solver finished. Waiting 5s for edit... | Account: {client.user.name}", "DEBUG")
                                edited_msg_tuple = await asyncio.wait_for(edit_task, timeout=5.0)
                                edited_msg = edited_msg_tuple[1]
                                self.log(f"Attempt {attempt}: Edit detected. | Account: {client.user.name}", "DEBUG")
                            
                            if edited_msg:
                                edit_detected = True
                                self.bot.loop.create_task(self.send_unified_webhook(
                                    title=f"✅ Captcha Solved │ Attempt {attempt}", 
                                    description=(
                                        f"**🤖 Bot:** {ephemeral_msg.author.name}\n"
                                        f"**💻 Server:** {ephemeral_msg.guild.name if ephemeral_msg.guild else 'DM'}\n"
                                        f"**🔗 URL:** {captcha_url}"
                                        ), 
                                        color=0x00FF00, 
                                        mention_type="none", 
                                        footer_text=f"Giveaway Joiner V{__version__} • Captcha Solver",
                                        message=ephemeral_msg, 
                                        client=client
                                ))
                                if hasattr(self.bot, '_giveaway_joiner_tab'):
                                    self.bot._giveaway_joiner_tab.toast(type="SUCCESS", title="✅ Captcha Solved", description=f"Bot {ephemeral_msg.author.name} verified.")
                                break
                        except (asyncio.TimeoutError, asyncio.CancelledError):
                            self.log(f"Attempt {attempt}: Solver succeeded, but edit listener timed out. | Message ID: {message.id} | Account: {client.user.name}", "WARNING")
                        except Exception as e:
                            self.log(f"Attempt {attempt}: Unhandled error: {e} | Message ID: {message.id} | Account: {client.user.name}", "ERROR")
                            traceback.print_exc()
                        finally:
                            if edit_task and not edit_task.done(): edit_task.cancel()
                        if attempt < max_attempts: await asyncio.sleep(2.0)
                    
                    if not edit_detected:
                        self.log(f"Captcha Solver: Failed to verify edit after {max_attempts} attempts. | Account: {client.user.name}", "ERROR")
                        desc_parts = [f"A giveaway requires manual verification.", f"**🤖 Bot:** {ephemeral_msg.author.name}", f"**💻 Server:** {ephemeral_msg.guild.name if ephemeral_msg.guild else 'DM'}", f"\n**🔗 [Click Here to Verify]({captcha_url})**", f"\n*(Auto-solve failed {max_attempts} times.)*"]
                        self.bot.loop.create_task(self.send_unified_webhook(
                            title="⚠️ Captcha Verification Failed!", 
                            description="\n".join(desc_parts), 
                            color=0xFF0000, mention_type="captcha", 
                            footer_text=f"Giveaway Joiner V{__version__} • Captcha Failure", 
                            message=ephemeral_msg, 
                            client=client
                        ))

                elif self.is_requirement_denial(ephemeral_msg):
                    self.log(f"❌ Entry Denied by Requirements detected! Account: {client.user.name}", "WARNING")
                    await self.update_stats("filtered", str(ephemeral_msg.author.id))
                    
                    reason = "Requirements not met."
                    if ephemeral_msg.embeds:
                        reason = ephemeral_msg.embeds[0].description or reason
                        reason = reason.replace("\n", " ").replace("**", "")[:100]

                    self.bot.loop.create_task(self.send_unified_webhook(
                        title="⛔ Entry Denied (Requirements)",
                        description=f"**🤖 Bot:** {ephemeral_msg.author.name}\n**❌ Reason:** {reason}",
                        color=0xFF0000,
                        mention_type="requirements",
                        message=ephemeral_msg,
                        client=client
                    ))
                    return

                else:
                    self.log(f"Ephemeral received but unknown type. | Account: {client.user.name}", "DEBUG")

            except asyncio.TimeoutError:
                self.log(f"Listener timed out. No ephemeral response detected. Account {client.user.name}", "DEBUG")
            except Exception as e:
                self.log(f"Error in wait_for_captcha_task: {e} | Account: {client.user.name}", "ERROR")
                traceback.print_exc()

        async def solve_captcha_task(self, captcha_url, client):
            self.log(f"Captcha Solver: Starting task (FlareSolverr) for {captcha_url} | Account: {client.user.name}", "INFO")
            flaresolverr_url = self.config.get("flaresolverr_url", "").strip()
            if not flaresolverr_url:
                self.log("Captcha Solver (Error): FlareSolverr URL not configured.", "ERROR")
                return False

            flaresolverr_api_url = f"{flaresolverr_url.rstrip('/')}/v1"
            payload = {"cmd": "request.get", "url": captcha_url, "maxTimeout": 60000}
            try:
                async with self.session.post(flaresolverr_api_url, json=payload, timeout=70) as response:
                    if response.status != 200:
                        self.log(f"Captcha Solver (Error): FlareSolverr status code: {response.status} | Account: {client.user.name}", "ERROR")
                        return False
                    data = await response.json()
                    if data.get("status") == "ok":
                        self.log(f"Captcha Solver (Success): FlareSolverr solved. | Account: {client.user.name}", "SUCCESS")
                        return True
                    else:
                        self.log(f"Captcha Solver (Error): FlareSolverr failed. Message: {data.get('message', 'N/A')} | Account: {client.user.name}", "ERROR")
                        return False
            except asyncio.TimeoutError:
                self.log(f"Captcha Solver (Error): Timeout waiting for FlareSolverr. | Account: {client.user.name}", "ERROR")
                return False
            except aiohttp.ClientConnectorError:
                self.log(f"Captcha Solver (Error): Failed to connect to FlareSolverr at {flaresolverr_api_url} | Account: {client.user.name}", "ERROR")
                return False
            except Exception as e:
                self.log(f"Captcha Solver (Exception): {e} | Account: {client.user.name}", "ERROR")
                traceback.print_exc()
                return False

        def is_captcha_message(self, message):
            try:
                if not message.embeds: return False
                embed = message.embeds[0]
                embed_text = ""
                if hasattr(embed, 'author') and hasattr(embed.author, 'name') and embed.author.name:
                    embed_text += embed.author.name.lower() + " "
                if hasattr(embed, 'description') and embed.description:
                    embed_text += embed.description.lower() + " "
                captcha_keywords = ["verify", "verification", "captcha", "not a bot", "verificar"]
                for keyword in captcha_keywords:
                    if keyword in embed_text: return True
                return False
            except Exception as e:
                self.log(f"Error in is_captcha_message: {e} | Account: {client.user.name}", "ERROR")
                return False

        # --- REQUIREMENT DETECTION ---
        def is_requirement_denial(self, message):
            try:
                denial_keywords = [
                    "entry denied", "access denied", "requirements", "missing role", 
                    "not enough messages", "required to send", "must be in server",
                    "account age", "dénié", "requisitos", "faltan mensajes"
                ]
                
                content = (message.content or "").lower()
                embed_desc = ""
                embed_title = ""
                embed_author = ""
                
                if message.embeds:
                    embed = message.embeds[0]
                    embed_desc = (embed.description or "").lower()
                    embed_title = (embed.title or "").lower()
                    if embed.author and embed.author.name:
                        embed_author = (embed.author.name or "").lower()

                full_text = f"{content} {embed_title} {embed_desc} {embed_author}"
                
                for keyword in denial_keywords:
                    if keyword in full_text:
                        return True
                return False
            except Exception as e:
                self.log(f"Error in is_requirement_denial: {e}", "ERROR")
                return False

        # --- WIN DETECTION ---
        async def is_win_message(self, message, embed, client):
            try:
                # Use the specific client's user ID
                user_id = client.user.id
                
                content_lower = message.content.lower() if message.content else ""
                embed_desc = (message.embeds[0].description or "").lower() if message.embeds else ""
                embed_title = (message.embeds[0].title or "").lower() if message.embeds else ""
                
                full_text_lower = f"{content_lower}\n{embed_title}\n{embed_desc}"

                lines = full_text_lower.split('\n')
                
                found_valid_mention = False
                
                host_keywords = [
                    "hosted by", "host:", "created by",
                    "creador", "organizado por", "planificado por",
                    "moderado por", "Organized by", "Powered by",
                    "criado por", "anfitrião", "realizado por",
                    "créé par", "organisé par", "hôte", "lancé par",
                    "veranstaltet von", "erstellt von", "gastgeber",
                    "ospitato da", "creato da", "organizzato da",
                    "gehost door", "gemaakt door", "organisator",
                    "tarafından", "düzenleyen", "oluşturan", "sahibi"
                ]

                for line in lines:
                    if str(user_id) in line or client.user.name.lower() in line:
                        
                        is_host_line = any(keyword in line for keyword in host_keywords)
                        
                        if not is_host_line:
                            found_valid_mention = True
                            break
                        else:
                            self.log(f"Win Check: Ignored self-mention as Host in line: '{line.strip()}'", "DEBUG")

                if not found_valid_mention:
                    return False, None
                
                if str(message.author.id) == self.KNOWN_BOT_IDS["GIVEAWAY_BOAT"]:
                    self.log(f"Win Check: Mentioned by Giveaway Boat. Fetching raw... | Message ID: {message.id} | Account {client.user.name}", "DEBUG")
                    try:
                        # Use the specific client's HTTP
                        msg_data = await client.http.get_message(message.channel.id, message.id)
                        raw_components = msg_data.get('components', [])
                        if not raw_components: return False, None

                        target_user = self.config.get("component_target_user", "").strip()
                        target_user_id = int(target_user) if target_user.isdigit() else user_id
                        
                        win_regex_normal = r'<@(\d+)>\s*won\s*(.+)'
                        win_regex_reroll = r'new winner of the giveaway\s*(.+?)\s*is\s*<@(\d+)>'

                        def search_raw_components_recursive(components_list):
                            for comp_data in components_list:
                                text_to_check = comp_data.get('content', None)
                                if text_to_check:
                                    normal_match = re.search(win_regex_normal, text_to_check, re.IGNORECASE)
                                    if normal_match:
                                        winner_id = int(normal_match.group(1))
                                        raw_prize = normal_match.group(2)
                                        
                                        if winner_id == target_user_id:
                                            self.log(f"Component win detected (Normal): User {winner_id} won {raw_prize} | Account {client.user.name}", "INFO")
                                            prize = raw_prize.split('\n')[0]
                                            prize = re.sub(r'\*\*(.+?)\*\*', r'\1', prize)
                                            prize = re.sub(r'the giveaway of\s', '', prize, flags=re.IGNORECASE)
                                            prize = prize.strip('!,. ')
                                            return True, prize

                                    reroll_match = re.search(win_regex_reroll, text_to_check, re.IGNORECASE)
                                    if reroll_match:
                                        raw_prize = reroll_match.group(1)
                                        winner_id = int(reroll_match.group(2))
                                        
                                        if winner_id == target_user_id:
                                            self.log(f"Component win detected (Reroll): User {winner_id} won {raw_prize} | Account {client.user.name}", "INFO")
                                            prize = raw_prize.split('\n')[0]
                                            prize = re.sub(r'\*\*(.+?)\*\*', r'\1', prize)
                                            prize = prize.strip('!,. ')
                                            return True, prize

                                if 'components' in comp_data and comp_data['components']:
                                    found = search_raw_components_recursive(comp_data['components'])
                                    if found: return found
                            return None
                        result = search_raw_components_recursive(raw_components)
                        if result: return result
                    except Exception as e:
                        self.log(f"Error checking Giveaway Boat win (HTTP): {e} | Message ID: {message.id} | Account {client.user.name}", "ERROR")
                
                win_patterns = ["congratulations", "congrats", "winner", "ganaste", "ganador", "felicidades", "ha ganado", "felicitaciones", "has ganado", "you won the", "won", "you are the winner", "eres el ganador", "kazanan", "félicitations", "gagnant", "gagné", "bravo", "gewinner", "herzlichen glückwunsch", "vencedor", "parabéns", "vincitore", "auguri"]
                content_text = message.content.lower() if message.content else ""
                embed_text = ""
                if embed:
                    if hasattr(embed, 'title') and embed.title: embed_text += embed.title.lower() + " "
                    if hasattr(embed, 'description') and embed.description: embed_text += embed.description.lower() + " "
                full_text = content_text + " " + embed_text
                
                exclusion_patterns = ["level", "reached level", "nivel", "alcanzado nivel"]
                for pattern in exclusion_patterns:
                    if pattern in full_text: return False, None
                
                for pattern in win_patterns:
                    if pattern in full_text:
                        prize = self.extract_prize_from_win_message(full_text, embed)
                        return True, prize
                return False, None
            except Exception as e:
                self.log(f"Error in win detection: {e} | Message ID: {message.id} | Account {client.user.name}", "ERROR")
                traceback.print_exc()
                return False, None

        def clean_prize_text(self, prize_text):
            if not prize_text: return "Unknown Prize"
            articles = ['the ', 'a ', 'an ', 'el ', 'la ', 'un ', 'una ']
            cleaned = prize_text.strip()
            for article in articles:
                if cleaned.lower().startswith(article.lower()):
                    cleaned = cleaned[len(article):].strip()
                    break
            cleaned = re.sub(r'[.!,;]+$', '', cleaned.strip())
            if cleaned and cleaned[0].islower():
                cleaned = cleaned[0].upper() + cleaned[1:]
            return cleaned if cleaned else "Unknown Prize"

        def extract_prize_from_win_message(self, text, embed=None):
            try:
                for pattern in self.win_prize_patterns:
                    match = pattern.search(text)
                    if match:
                        raw_prize = match.group(1).strip()
                        raw_prize = re.sub(r'\*\*(.+?)\*\*', r'\1', raw_prize).strip()
                        if len(raw_prize) > 1:
                            return self.clean_prize_text(raw_prize)[:100]
                
                if embed:
                    if hasattr(embed, 'title') and embed.title and len(embed.title) < 100:
                        return self.clean_prize_text(embed.title)
                    if hasattr(embed, 'description') and embed.description and len(embed.description) < 200:
                        first_line = embed.description.split('\n')[0]
                        if len(first_line) < 100:
                            return self.clean_prize_text(first_line)
                return "Unknown Prize"
            except Exception as e:
                self.log(f"Error extracting prize from win message: {e}", "ERROR")
                return "Unknown Prize"

        # --- WEBHOOK ---
        def extract_giveaway_info(self, embed, message):
            info = {"end_time": None, "hosted_by": None, "channel": None, "message_link": None}
            embed_content = ""
            if embed:
                if embed.title: embed_content += embed.title + " "
                if embed.description: embed_content += embed.description + " "
                if embed.fields:
                    for field in embed.fields:
                        if hasattr(field, 'name') and field.name: embed_content += f"{field.name} "
                        if hasattr(field, 'value') and field.value: embed_content += f"{field.value} "
            
            timestamp_patterns = [r"<t:(\d+):[RFfDdTt]>", r"ends?:?\s*<t:(\d+)", r"termina:?\s*<t:(\d+)"]
            for pattern in timestamp_patterns:
                match = re.search(pattern, embed_content, re.IGNORECASE)
                if match:
                    try:
                        timestamp = int(match.group(1))
                        end_time = datetime.fromtimestamp(timestamp)
                        now = datetime.now()
                        if end_time > now:
                            time_diff = end_time - now
                            days, hours, minutes, seconds = time_diff.days, time_diff.seconds // 3600, (time_diff.seconds % 3600) // 60, time_diff.seconds % 60
                            time_parts = []
                            if days > 0: time_parts.append(f"{days} day{'s' if days != 1 else ''}")
                            if hours > 0: time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
                            if minutes > 0: time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
                            if seconds > 0: time_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
                            info["end_time"] = " ".join(time_parts) if time_parts else "Less than 1 second"
                            break
                    except (ValueError, OSError): continue
            
            hosted_patterns = [r"hosted by:?\s*(.+?)(?:\n|$)", r"organizado por:?\s*(.+?)(?:\n|$)", r"host:?\s*(.+?)(?:\n|$)"]
            for pattern in hosted_patterns:
                match = re.search(pattern, embed_content, re.IGNORECASE)
                if match:
                    info["hosted_by"] = match.group(1).strip()
                    break
            if not info["hosted_by"]: info["hosted_by"] = message.author.name
            
            info["channel"] = f"#{message.channel.name}" if message.guild and message.channel else "DM"
            info["message_link"] = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}" if message.guild else f"https://discord.com/channels/@me/{message.channel.id}/{message.id}"
            return info

        def sanitize_text(self, text):
            if not text: return text
            text = str(text).replace("`", "'").replace(">", "").replace("*", "")
            text = text.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
            return text.strip(" :")

        async def send_unified_webhook(self, title: str, description: str, color: int, mention_type: str = "none", footer_text: str = None, message: 'discord.Message' = None, embed: 'discord.Embed' = None, show_fp_suggestion: bool = False, client=None):
            if not self.config.get("webhook_enabled", False) or not self.config.get("webhook_url", "").strip():
                self.log(f"Webhook disabled or URL not set. Skipping: '{title}'", "DEBUG")
                return

            try:
                enhanced_description = description
                if message:
                    try:
                        embed_to_parse = embed if embed else (message.embeds[0] if message.embeds else None)
                        giveaway_info = self.extract_giveaway_info(embed_to_parse, message)
                        
                        server_name = self.sanitize_text(message.guild.name) if message.guild else "DM"
                        channel_name = self.sanitize_text(giveaway_info.get("channel"))
                        
                        if giveaway_info.get("end_time"): enhanced_description += f"\n**⏰ Ends In:** {giveaway_info['end_time']}"
                        if channel_name: enhanced_description += f"\n**📍 Channel:** {channel_name}"
                        if message.guild:
                            server_link = f"https://discord.com/channels/{message.guild.id}"
                            enhanced_description += f"\n**💻 Server:** [{server_name}](<{server_link}>)"
                        
                        raw_host = giveaway_info.get("hosted_by", "")
                        mention_match = re.search(r"(<@!?\d+>)", raw_host)
                        if mention_match:
                            hosted_by = mention_match.group(1)
                        else:
                            hosted_by = self.sanitize_text(raw_host)
                        if hosted_by: enhanced_description += f"\n**👤 Hosted By:** {hosted_by}"
                        if client:
                            enhanced_description += f"\n**🚀 Account:** `{client.user.name}`"
                        if giveaway_info.get("message_link"): enhanced_description += f"\n🔗 [**Jump to Message**](<{giveaway_info['message_link']}>)"
                        if show_fp_suggestion:
                            if "Message ID:" not in enhanced_description:
                                enhanced_description += f"\n**Message ID:** ```{message.id}```"
                                enhanced_description += "\nIf this embed is not a giveaway, use the command [p]gw add <message_id>"
                    except Exception as e:
                        self.log(f"Failed to extract extra info for webhook: {e}", "DEBUG")

                content = ""
                mention_key_map = {"win": "webhook_mention_user", "captcha": "webhook_mention_captcha", "manual_join": "webhook_mention_manual", "manual_ticket": "webhook_mention_ticket", "requirements": "webhook_mention_requirements", "token_fail": "webhook_mention_token_fail"}
                config_key = mention_key_map.get(mention_type)
                mention_user_id = self.bot.user.id
                
                if config_key and self.config.get(config_key, False):
                    content = f"<@{mention_user_id}>"

                footer_text = footer_text if footer_text else f"Giveaway Joiner V{__version__}"
                embed_data = {"title": title, "description": enhanced_description, "color": color, "timestamp": datetime.utcnow().isoformat(), "footer": {"text": footer_text}}
                webhook_data = {"content": content, "embeds": [embed_data]}

                try:
                    async with self.session.post(self.config["webhook_url"], json=webhook_data, timeout=aiohttp.ClientTimeout(total=10.0)) as response:
                        if response.status == 204:
                            self.log(f"Webhook sent successfully: '{title}' | Account: {client.user.name}", "DEBUG")
                        else:
                            self.log(f"Webhook failed {response.status}: {await response.text()} | Account: {client.user.name}", "ERROR")
                except Exception as e:
                    self.log(f"Error sending webhook request ('{title}'): {e} | Account: {client.user.name}", "ERROR")

            except Exception as e:
                self.log(f"Critical error preparing webhook ('{title}'): {e} | Account: {client.user.name}", "ERROR")
                traceback.print_exc()

        def parse_channel_link(self, content_text):
            if not content_text: return None
            match = re.search(r"<#(\d+)>", content_text)
            return match.group(1) if match else None

        # --- FLARESOLVERR ---
        async def thread_gw(self, func, *args, **kwargs):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

        def extract_flaresolverr(self, zip_path, path):
            try:
                os.makedirs(path, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as z:
                    file_list = z.namelist()
                    if not file_list: return False, "Zip file is empty."
                    prefix = ""
                    prefix_len = 0
                    parts = file_list[0].split('/')
                    if len(parts) > 1 and all(f.startswith(parts[0] + '/') for f in file_list if not f.endswith('/')):
                        prefix = parts[0] + '/'
                        prefix_len = len(prefix)
                    for member_name in file_list:
                        if member_name.endswith('/'): continue
                        final_name = member_name[prefix_len:]
                        final_path = os.path.join(path, final_name)
                        final_dir = os.path.dirname(final_path)
                        if final_dir: os.makedirs(final_dir, exist_ok=True)
                        with z.open(member_name) as source, open(final_path, "wb") as target:
                            target.write(source.read())
                if os.path.exists(os.path.join(path, "flaresolverr.exe")):
                    return True, None
                else:
                    return False, "flaresolverr.exe not found after extraction."
            except Exception as e:
                self.log(f"Extraction error: {e}", "ERROR")
                return False, str(e)

        def create_startup_shortcut(self, target_exe_path, target_dir_path):
            try:
                target_exe_path = os.path.normpath(target_exe_path)
                target_dir_path = os.path.normpath(target_dir_path)
                startup_dir = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
                if not os.path.exists(startup_dir): os.makedirs(startup_dir)
                bat_path = os.path.join(startup_dir, "start_flaresolverr.bat")
                bat_content = f'@echo off\nstart "FlareSolverr" /D "{target_dir_path}" "{target_exe_path}"\n'
                with open(bat_path, "w", encoding="utf-8") as f: f.write(bat_content)
                return True, None
            except Exception as e:
                self.log(f"Error creating startup shortcut: {e}", "ERROR")
                return False, str(e)

        def get_startup_bat_path(self):
            return os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', "start_flaresolverr.bat")

        def toggle_startup_shortcut(self, enable):
            try:
                bat_path = self.get_startup_bat_path()
                
                if enable:
                    target_exe = self.flaresolverr_exe
                    target_dir = self.flaresolverr_dir
                    if not os.path.exists(target_exe):
                        return False, "FlareSolverr executable not found."
                        
                    bat_content = f'@echo off\nstart "FlareSolverr" /D "{target_dir}" "{target_exe}"\n'
                    with open(bat_path, "w", encoding="utf-8") as f:
                        f.write(bat_content)
                    return True, "Added to Windows Startup."
                else:
                    if os.path.exists(bat_path):
                        os.remove(bat_path)
                        return True, "Removed from Windows Startup."
                    else:
                        return True, "Shortcut was already removed."
            except Exception as e:
                return False, str(e)

        def save_file_sync(self, file_path, data):
            try:
                with open(file_path, "wb") as f:
                    f.write(data)
                return True, None
            except Exception as e:
                return False, str(e)

        async def download_flaresolverr(self, tab, status_text, download_button, open_folder_button):
            download_button.loading = True
            download_button.disabled = True
            status_text.content = "Status: Searching for latest version..."
            FLARESOLVERR_ASSET_NAME = "flaresolverr_windows_x64.zip"
            FLARESOLVER_GITHUB_LINK = "https://api.github.com/repos/FlareSolverr/FlareSolverr/releases/latest"
            
            temp_zip_path = os.path.join(self.data_dir, "flaresolverr_temp.zip")

            try:
                async with self.session.get(FLARESOLVER_GITHUB_LINK) as response:
                    if response.status != 200: raise Exception(f"GitHub API returned {response.status}")
                    data = await response.json()
                    download_url = None
                    for asset in data.get("assets", []):
                        if asset.get("name") == FLARESOLVERR_ASSET_NAME:
                            download_url = asset.get("browser_download_url")
                            break
                    if not download_url: raise Exception(f"File '{FLARESOLVERR_ASSET_NAME}' not found.")
                    
                    status_text.content = "Status: Downloading..."
                    self.log(f"Downloading FlareSolverr from: {download_url}", "INFO")

                    file_content = None
                    async with self.session.get(download_url) as response:
                        if response.status != 200: raise Exception(f"Failed to download, status {response.status}")
                        file_content = await response.read()

                    status_text.content = "Status: Writing to disk..."
                    write_success, write_error = await self.thread_gw(self.save_file_sync, temp_zip_path, file_content)
                    
                    if not write_success:
                        raise Exception(f"Disk write failed: {write_error}")
                    
                    del file_content

                status_text.content = "Status: Extracting..."
                success, error = await self.thread_gw(self.extract_flaresolverr, temp_zip_path, self.flaresolverr_dir)
                
                if os.path.exists(temp_zip_path):
                    try:
                        os.remove(temp_zip_path)
                    except:
                        pass

                if not success: raise Exception(f"Extraction failed: {error}")
                
                status_text.content = "Status: Installed"
                self.log("FlareSolverr extracted successfully.", "SUCCESS")
                tab.toast(type="SUCCESS", title="FlareSolverr", description="Successfully installed.")
                status_text.content = "Status: Adding to Windows Startup..."
                
                success_startup, error_startup = await self.thread_gw(self.create_startup_shortcut, self.flaresolverr_exe, self.flaresolverr_dir)
                
                if success_startup:
                    self.log("Successfully added FlareSolverr to Windows Startup.", "SUCCESS")
                    tab.toast(type="SUCCESS", title="Windows Startup", description="FlareSolverr added to Windows Startup.")
                else:
                    self.log(f"Failed to add to startup: {error_startup}", "ERROR")
                    tab.toast(type="ERROR", title="Startup Error", description=f"Could not be added: {error_startup}")
                
                status_text.content = "Status: Installed (Starts with Windows)"
                self.config["flaresolverr_installed"] = True
                await self.save_config_gw()
                download_button.visible = False
                open_folder_button.visible = True
                if "flaresolverr_startup_toggle" in self.ui:
                    self.ui["flaresolverr_startup_toggle"].visible = True
                    self.ui["flaresolverr_startup_toggle"].checked = True
            except Exception as e:
                self.log(f"Failed to download/install FlareSolverr: {e}", "ERROR")
                status_text.content = "Status: Installation Error"
                tab.toast(type="ERROR", title="Installation Error", description=str(e))
                
                if os.path.exists(temp_zip_path):
                    try: os.remove(temp_zip_path)
                    except: pass
                    
                download_button.loading = False
                download_button.disabled = False

        async def smart_message_fetch(self, message, client):
            bot_id = str(message.author.id)
            
            if bot_id in self.config.get("force_raw_fetch_bots", []):
                try:
                    self.log(f"Fetching full message via API for known complex bot: {message.author.name} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
                    msg_data = await client.http.get_message(message.channel.id, message.id)
                    return True, msg_data
                except Exception as e:
                    self.log(f"API Fetch failed: {e} | Message ID: {message.id} | Account: {client.user.name}", "ERROR")
                    return False, message

            content_lower = (message.content or "").lower()
            embed_desc = ""
            if message.embeds:
                embed_desc = (message.embeds[0].description or "").lower()
            
            full_text = content_lower + " " + embed_desc
            is_potential_giveaway = any(k in full_text for k in self.config["detection_keywords"])
            
            if is_potential_giveaway and not message.components:
                msg_id = str(message.id)
                current_time = datetime.now().timestamp()

                keys_to_remove = [k for k, v in self.probed_messages_cache.items() if current_time - v > 300]
                for k in keys_to_remove: 
                    del self.probed_messages_cache[k]

                if msg_id in self.probed_messages_cache:
                    return False, message
                
                self.probed_messages_cache[msg_id] = current_time

                self.log(f"Suspicious message from {message.author.name}: Looks like GW but no components. Probing API... | Message ID: {message.id} | Account:{client.user.name}", "DEBUG")
                try:
                    raw_data = await client.http.get_message(message.channel.id, message.id)
                    
                    if raw_data.get('components'):
                        self.log(f"HIDDEN COMPONENTS DETECTED! Adding {message.author.name} ({bot_id}) to force_api list. | Account:{client.user.name}", "WARNING")
                        
                        if "force_raw_fetch_bots" not in self.config:
                            self.config["force_raw_fetch_bots"] = []
                        
                        if bot_id not in self.config["force_raw_fetch_bots"]:
                            self.config["force_raw_fetch_bots"].append(bot_id)
                            await self.save_config_gw()
                        
                        return True, raw_data
                    else:
                        self.log(f"Probe result: No components found in Raw Data. | Account:{client.user.name} | Message ID: {message.id}", "DEBUG")
                
                except Exception as e:
                    self.log(f"Probe API failed: {e} | Account:{client.user.name} | Message ID: {message.id}", "DEBUG")

            return False, message

        def find_ticket_channel(self, guild, client):
            if not guild: return None
            
            priority_keywords = ["claim", "prize", "premio", "reclamar", "ganador", "winner", "récompense", "ödül"]
            
            ticket_keywords = [
                "ticket", "tiquet", "support", "soporte", "ayuda", "help", "contact", 
                "apoyo", "ajuda", "assistance", "destek", "hilfe"
            ]

            open_keywords = ["open", "abrir", "crear", "create", "new", "nuevo"]

            candidates = []
            for channel in guild.text_channels:
                permissions = channel.permissions_for(guild.me)
                if not permissions.view_channel or not permissions.read_message_history:
                    continue
                
                chan_name = channel.name.lower().replace("-", " ").replace("_", " ")
                
                score = 0
                
                if any(pk == chan_name for pk in priority_keywords): score += 50
                elif any(tk == chan_name for tk in ticket_keywords): score += 30
                
                if any(pk in chan_name for pk in priority_keywords): score += 10
                if any(tk in chan_name for tk in ticket_keywords): score += 5
                
                if any(ok in chan_name for ok in open_keywords): score += 2
                
                if "log" in chan_name or "transcript" in chan_name or "closed" in chan_name:
                    score -= 50

                if score > 0:
                    candidates.append((score, channel))

            candidates.sort(key=lambda x: x[0], reverse=True)
            
            if candidates:
                best_channel = candidates[0][1]
                self.log(f"Smart Channel Search: Found potential ticket channel: #{best_channel.name} (Score: {candidates[0][0]}) | Account: {client.user.name}", "DEBUG")
                return str(best_channel.id)
            
            return None

        def has_explicit_ticket_instruction(self, text):
            if not text: return False
            text = text.lower()
            
            triggers = [
                "open a ticket", "create a ticket", "open ticket", "create ticket", "go to ticket",
                "claim in ticket", "claim via ticket", "support ticket", "ticket to claim",
                "abre un ticket", "crea un ticket", "abrir ticket", "crear ticket", "ve a ticket",
                "reclama en ticket", "soporte", "reclamar por ticket",
                "ouvrir un ticket", "créer un ticket", "allez dans ticket",
                "abrir ticket", "criar ticket", "vá para o ticket",
                "ticket öffnen", "ticket erstellen",
                "apri un ticket", "crea un ticket",
                "ticket aç", "destek talebi"
            ]
            
            action_words = ["open", "create", "make", "abrir", "crear", "hacer", "ouvrir", "claim", "reclamar"]
            target_words = ["ticket", "support", "soporte", "tiquet", "destek", "hilfe"]
            
            if any(phrase in text for phrase in triggers):
                return True
            
            has_action = any(a in text for a in action_words)
            has_target = any(t in text for t in target_words)
            
            return has_action and has_target

        # --- MAIN EVENT HANDLER ---
        async def process_message(self, message, client):
            if not client.is_ready() or not client.user:
                self.log(f"Ignored message for {client.user.name}: Client not ready.", "DEBUG")
                return

            if self.stats is not None:
                self.stats["total_scanned"] = self.stats.get("total_scanned", 0) + 1
                if self.stats["total_scanned"] % 1000 == 0:
                    self.refresh_ui_text()

            try:
                join_was_successful = False
                if not self.config:
                    return
                
                # --- PRIZE CLAIM SYSTEM ---
                channel_id_str = str(message.channel.id)

                if not self.config.get("prize_claim_enabled", True):
                    pass
                elif client.user.id != self.bot.user.id and not self.config.get("enable_alts_for_claiming", False):
                    pass
                elif channel_id_str in self.pending_ticket_claims:
                    claims_list = self.pending_ticket_claims[channel_id_str]
                    my_claim = None

                    for claim in claims_list:
                        if claim.get("winner_client_id") == client.user.id:
                            my_claim = claim
                            break
                    
                    if my_claim:
                        timeout_seconds = self.config.get("ticket_wait_timeout", 3600)
                        
                        if (datetime.now() - my_claim["timestamp"]).total_seconds() > timeout_seconds:
                            if my_claim in claims_list:
                                claims_list.remove(my_claim)
                            if not claims_list:
                                del self.pending_ticket_claims[channel_id_str]
                            self.log(f"Prize Claim: Expired claim on channel {message.channel.id} for {client.user.name}", "DEBUG")
                        
                        else:
                            full_msg_content = (message.content or "") + " "
                            if message.embeds:
                                full_msg_content += (message.embeds[0].description or "")
                            full_msg_content = full_msg_content.lower()

                            target_channel_id = self.parse_channel_link(message.content)
                            if not target_channel_id and message.embeds and message.embeds[0].description:
                                target_channel_id = self.parse_channel_link(message.embeds[0].description)

                            if not target_channel_id and message.guild:
                                if self.has_explicit_ticket_instruction(full_msg_content):
                                    self.log(f"Prize Claim: Ticket instruction detected. Running smart search... | Account: {client.user.name}", "DEBUG")
                                    target_channel_id = self.find_ticket_channel_smart(message.guild, client)
                                else:
                                    if self.has_dm_instruction(full_msg_content):
                                        self.log(f"Prize Claim: Ignoring ticket search (DM instruction detected). | Account: {client.user.name}", "DEBUG")
                                    else:
                                        self.log(f"Prize Claim: No explicit ticket instruction found. | Account: {client.user.name}", "DEBUG")

                            is_privileged = message.author.bot or (message.guild and message.author.guild_permissions and message.author.guild_permissions.manage_messages)
                            
                            ticket_action_taken = False

                            if target_channel_id and is_privileged:
                                ticket_action_taken = True
                                prize = my_claim["prize"]
                                self.log(f"Prize Claim: Ticket instruction detected for '{prize}' in channel <#{target_channel_id}> | Account:{client.user.name}", "INFO")
                                
                                if my_claim in claims_list:
                                    claims_list.remove(my_claim)
                                if not claims_list:
                                    del self.pending_ticket_claims[channel_id_str]
                                
                                if self.config.get("auto_claim_ticket_enabled", True):
                                    self.log(f"Prize Claim: Auto-Claim ENABLED. Running weighted click...", "DEBUG")
                                    status, new_ticket_id = await self.find_and_click_weighted_ticket(target_channel_id, prize, message, client)
                                    
                                    desc_parts = [f"**🎁 Prize:** {prize}", f"**💻 Server:** {message.guild.name if message.guild else 'DM'}"]
                                    title_str = "⚠️ Ticket Action Required!"
                                    color_hex = 0xFFA500
                                    mention = "manual_ticket"

                                    if status == "success":
                                        self.log(f"Prize Claim: Auto-Claim SUCCEEDED. | Account:{client.user.name}", "SUCCESS")
                                        title_str = "✅ Auto-Claimed Ticket!"
                                        color_hex = 0x00FF00
                                        mention = "none"
                                        if new_ticket_id:
                                            desc_parts.append(f"**🔗 Ticket Opened In:** <#{new_ticket_id}>")
                                            if self.config.get("auto_claim_send_message", False):
                                                message_to_send = self.config.get("auto_claim_message", "").strip()
                                                if message_to_send:
                                                    try:
                                                        await asyncio.sleep(random.uniform(2.0, 4.0)) 
                                                        new_channel = await client.fetch_channel(int(new_ticket_id))
                                                        await new_channel.send(message_to_send)
                                                        desc_parts.append(f"*Successfully sent auto-claim message!*")
                                                    except Exception as e:
                                                        self.log(f"Auto-Claim: Error sending message: {e} | Account:{client.user.name}", "ERROR")
                                                        desc_parts.append(f"*Failed to send message.*")
                                        else:
                                            desc_parts.append(f"**🔗 Ticket Panel:** <#{target_channel_id}>")
                                    
                                    elif status == "limit_reached":
                                        title_str = "⚠️ Auto-Claim Failed: Limit Reached"
                                        desc_parts.append(f"**🔗 Ticket Panel:** <#{target_channel_id}>\n\n*Please close your existing ticket.*")
                                    
                                    else:
                                        desc_parts.append(f"*(Auto-Claim failed to find a valid button.)*\n\n**🔗 Open Ticket In:** <#{target_channel_id}>")

                                    self.bot.loop.create_task(self.send_unified_webhook(
                                        title=title_str, 
                                        description="\n".join(desc_parts), 
                                        color=color_hex, mention_type=mention, 
                                        footer_text=f"Giveaway Joiner V{__version__} • Auto-Claim", 
                                        message=message, 
                                        client=client
                                    ))
                                    return

                                else: # Auto-claim disabled
                                    self.bot.loop.create_task(self.send_unified_webhook(
                                        title="⚠️ Ticket Action Required!", 
                                        description=(f"**🎁 Prize:** {prize}\n"
                                        f"**🔗 Open Ticket In:** <#{target_channel_id}>"), 
                                        color=0xFFA500, 
                                        mention_type="manual_ticket", 
                                        footer_text=f"Giveaway Joiner V{__version__} • Prize Claim", 
                                        message=message, 
                                        client=client
                                    ))
                                return

                            # --- BLOCK 2: DM ATTEMPT ---
                            if not ticket_action_taken and self.config.get("auto_claim_dm_enabled", False):
                                full_text = (message.content or "") + " " + (message.embeds[0].description or "" if message.embeds else "")
                                
                                if self.has_dm_instruction(full_text):
                                    self.log(f"Prize Claim: DM instruction detected. Attempting Auto-DM... | Account: {client.user.name}", "INFO")
                                    
                                    prize = my_claim["prize"]
                                    status, target = await self.attempt_auto_dm_claim(message, client, prize)
                                    
                                    if status == "success":
                                        if my_claim in claims_list: claims_list.remove(my_claim)
                                        if not claims_list: del self.pending_ticket_claims[channel_id_str]
                                        
                                        target_desc = f"{target.mention} (`{target.name}`)" if target else "Unknown User"
                                        msg_content = self.config.get('auto_claim_message', 'Hello...')

                                        self.bot.loop.create_task(self.send_unified_webhook(
                                            title="✅ Auto-Claimed via DM!", 
                                            description=f"**🎁 Prize:** {prize}\n**📩 Sent DM to:** {target_desc}\n**💬 Message:** *{msg_content}*", 
                                            color=0x00FF00, 
                                            mention_type="none", 
                                            footer_text=f"Giveaway Joiner V{__version__} • Auto-DM", 
                                            message=message, 
                                            client=client
                                        ))
                                        return 
                                    
                                    elif status == "failed":
                                        target_name = target.name if target else "User"
                                        self.bot.loop.create_task(self.send_unified_webhook(
                                            title="⚠️ Auto-DM Failed", 
                                            description=f"**🎁 Prize:** {prize}\nTried to DM **{target_name}** but failed (DMs Closed?).\n\n**Action Required:** Please DM them manually.", 
                                            color=0xFF0000, 
                                            mention_type="manual_ticket", 
                                            message=message, 
                                            client=client
                                        ))
                                        return
                                    
                                    else:
                                        self.log(f"Prize Claim: DM instruction detected ('{message.content}') but Auto-DM is DISABLED in settings.", "WARNING")

                # --- GLOBAL CHECKS ---
                if not self.config["enabled"]: return
                
                if message.author.id == client.user.id: return
                
                # Server exclusion
                if message.guild and str(message.guild.id) in getattr(self, 'excluded_servers_set', set()):
                    return
                
                if str(message.channel.id) in self.config.get("excluded_channels", []):
                    return

                if hasattr(message, 'flags') and message.flags and (message.flags.value & 64): return
                
                dyno_bot_id = self.KNOWN_BOT_IDS["DYNO"]
                dyno_is_monitored = dyno_bot_id in self.config["monitored_bots"]
                is_monitored_bot = str(message.author.id) in self.config["monitored_bots"]
                is_dyno_webhook = (dyno_is_monitored and message.author.bot and message.author.name.lower() == "dyno")

                if not is_monitored_bot and not is_dyno_webhook: return
                
                is_raw, data_obj = await self.smart_message_fetch(message, client)
                
                has_components = False
                if is_raw: has_components = len(data_obj.get('components', [])) > 0
                else: has_components = message.components and len(message.components) > 0

                if (is_dyno_webhook or str(message.author.id) == dyno_bot_id) and message.content:
                    if "uploaded a new video" in message.content.lower():
                        self.log(f"Skipping Dyno FP (YouTube): {message.content[:60]}...", "INFO")
                        return
                
                if str(message.author.id) == "530082442967646230" and message.content:
                    if "review your giveaway" in message.content.lower():
                        self.log(f"Skipping Giveaway Boat FP (Review): {message.content[:60]}... | Account:{client.user.name}", "INFO")
                        return

                # --- WIN DETECTION ---
                if self.config.get("auto_detect_wins", True):
                    embed_for_win = message.embeds[0] if message.embeds else None
                    is_win, prize = await self.is_win_message(message, embed_for_win, client)
                    
                    if is_win:
                        await self.update_stats("won", str(message.author.id), prize)
                        self.log(f"🎉 WIN DETECTED! Prize: {prize}, Bot: {message.author.name} | Account:{client.user.name} | Message ID: {message.id}", "SUCCESS")

                        if self.config.get("prize_claim_enabled", True):
                            channel_id_str = str(message.channel.id)
                            if channel_id_str not in self.pending_ticket_claims:
                                self.pending_ticket_claims[channel_id_str] = []
                            
                            self.pending_ticket_claims[channel_id_str].append({
                                "prize": prize, 
                                "timestamp": datetime.now(),
                                "winner_client_id": client.user.id
                            })
                            
                            self.log(f"Prize Claim: Standby activated on {message.channel.id} for '{prize}' | Account:{client.user.name}", "INFO")
                        
                        self.bot.loop.create_task(self.send_unified_webhook(
                            title="🎉 Giveaway Won!", 
                            description=(f"**🎁 Prize:** {prize}\n"
                            f"**🤖 Bot:** {message.author.name}"), 
                            color=0xFFD700, 
                            mention_type="win",
                            footer_text=f"Giveaway Joiner V{__version__} • Win Detection", 
                            message=message, 
                            client=client
                        ))
                        if hasattr(self.bot, '_giveaway_joiner_tab'):
                            self.bot._giveaway_joiner_tab.toast(type="SUCCESS", title="🎉 Giveaway Won!", description=f"You won: {prize[:50]}{'...' if len(prize) > 50 else ''}")
                        return 

                # --- GIVEAWAY DETECTION ---
                if not message.embeds: return
                self.log(f"Processing message from {message.author.name} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
                
                for embed in message.embeds:
                    is_giveaway, confidence, prize = self.is_giveaway_embed(embed, message, client)
                    if is_giveaway:
                        history_key = str(message.id)
                        if history_key in self.history:
                            entry = self.history[history_key]
                            if client.user.name in entry.get("joined_accounts", []):
                                self.log(f"Account: {client.user.name} already joined {history_key}. Skipping.", "DEBUG")
                                continue
                        await self.update_stats("detected", str(message.author.id), prize)
                        server_name = message.guild.name if message.guild else "DM"
                        self.log(f"Giveaway detected! Server: {server_name} | Bot: {message.author.name} | Message ID: {message.id} | Prize: {prize[:50]}... | Account: {client.user.name}", "INFO")
                        
                        if not self.passes_blacklist_filter(prize):
                            await self.update_stats("filtered", str(message.author.id))
                            await self.record_joined_giveaway(message, embed, prize, client)
                            continue
                                                
                        if is_dyno_webhook and not has_components:
                            self.log(f"Dyno giveaway (no button) detected: {prize} | Account: {client.user.name}", "INFO")
                            gw_url = getattr(embed, 'url', None)
                            desc_parts_dyno = [f"A giveaway from **{message.author.name}** has no join button.", "**Must join manually.**", f"\n**🎁 Prize:** {prize}"]
                            if gw_url: desc_parts_dyno.append(f"\n**🔗 [Click Here to Join]({gw_url})**")
                            self.bot.loop.create_task(self.send_unified_webhook(
                                title="Manual Join Required", 
                                description="\n".join(desc_parts_dyno), 
                                color=0xFFA500, mention_type="manual_join", 
                                footer_text=f"Giveaway Joiner V{__version__} • Manual", 
                                message=message, 
                                embed=embed, 
                                show_fp_suggestion=True, 
                                client=client
                            ))
                            await self.update_stats("filtered", str(message.author.id))
                            await self.record_joined_giveaway(message, embed, prize, client)
                            continue
                        
                        if self.config["require_button"] and not has_components:
                            self.log(f"No buttons - attempting reaction fallback for: {prize} | Message ID: {message.id} | Account: {client.user.name}", "DEBUG")
                            reaction_success = await self.add_giveaway_reaction(message, client)
                            if reaction_success:
                                join_was_successful = True
                                await self.update_stats("joined", str(message.author.id), prize)
                                await self.record_joined_giveaway(message, embed, prize, client)
                                self.log(f"Successfully joined via reaction: {prize[:50]}{'...' if len(prize) > 50 else ''} | Message ID: {message.id} | Account: {client.user.name}", "SUCCESS")
                                
                                self.bot.loop.create_task(self.send_unified_webhook(
                                    title="🎉 Joined Giveaway (Reaction)!", 
                                    description=(f"**🎁 Prize:** {prize}\n"
                                    f"**🤖 Bot:** {message.author.name}\n"
                                    f"**📝 Method:** Reaction"), 
                                    color=0x00ff00, 
                                    footer_text=f"Giveaway Joiner V{__version__} • Joined", 
                                    message=message, 
                                    embed=embed,
                                    show_fp_suggestion=True,
                                    client=client
                                ))
                                if hasattr(self.bot, '_giveaway_joiner_tab'):
                                    self.bot._giveaway_joiner_tab.toast(type="SUCCESS", title="Joined (Reaction)!", description=f"Prize: {prize[:30]}...")
                            else:
                                self.log(f"Failed to join via reaction: {prize[:50]}{'...' if len(prize) > 50 else ''} | Account: {client.user.name} | Message ID: {message.id}", "ERROR")
                                await self.record_joined_giveaway(message, embed, prize, client)
                                self.bot.loop.create_task(self.send_unified_webhook(
                                    title="❌ Failed to Join Giveaway", 
                                    description=(f"**🎁 Prize:** {prize}\n"
                                    f"**🤖 Bot:** {message.author.name}\n"
                                    f"**❔ Reason:** No button and reaction failed."), 
                                    color=0xFF0000, 
                                    footer_text=f"Giveaway Joiner V{__version__} • Join Failure", 
                                    message=message, 
                                    embed=embed, 
                                    show_fp_suggestion=True, 
                                    client=client
                                ))
                            continue
                        
                        # --- DELAY LOGIC ---
                        base_delay = random.uniform(self.config["join_delay_min"], self.config["join_delay_max"])
                        extra_delay = 0
                        try:
                            if client.user.id == self.main_bot_id:
                                extra_delay = 0
                            else:
                                active_accounts = list(self.running_clients.keys())
                                if client.user.name in active_accounts:
                                    index = active_accounts.index(client.user.name)
                                    base_interval = random.uniform(1.5, 3.5)
                                    jitter = random.uniform(-0.5, 0.5)
                                    extra_delay = (index * base_interval) + jitter
                        except:
                            pass
                        
                        total_delay = base_delay + extra_delay
                        self.log(f"Waiting {total_delay:.1f}s before clicking button | Account: {client.user.name}", "DEBUG")
                        await asyncio.sleep(total_delay)
                        
                        if history_key in self.history:
                            entry = self.history[history_key]
                            if client.user.name in entry.get("joined_accounts", []):
                                self.log(f"Post-delay check: Account {client.user.name} already joined {history_key}. Aborting.", "DEBUG")
                                continue
                        
                        captcha_task = asyncio.create_task(self.wait_for_captcha_task(message, client))
                        
                        join_success = False
                        if is_raw:
                             join_success = await self.click_giveaway_button(message, client, specific_components=data_obj['components'])
                        else:
                             join_success = await self.click_giveaway_button(message, client)
                        
                        if join_success:
                            join_was_successful = True
                            await self.update_stats("joined", str(message.author.id), prize)
                            await self.record_joined_giveaway(message, embed, prize, client)
                            self.log(f"Successfully joined via button: {prize[:50]}{'...' if len(prize) > 50 else ''} | Account: {client.user.name}", "SUCCESS")
                            self.bot.loop.create_task(self.send_unified_webhook(
                                title="🎉 Joined Giveaway!", 
                                description=(f"**🎁 Prize:** {prize}\n"
                                f"**🤖 Bot:** {message.author.name}\n"
                                f"**📝 Method:** Button"), 
                                color=0x00ff00, 
                                footer_text=f"Giveaway Joiner V{__version__} • Joined", 
                                message=message, 
                                embed=embed, 
                                show_fp_suggestion=True, 
                                client=client
                            ))
                            if hasattr(self.bot, '_giveaway_joiner_tab'):
                                self.bot._giveaway_joiner_tab.toast(type="SUCCESS", title="Giveaway Joined!", description=f"Prize: {prize[:30]} | Account: {client.user.name}")
                        else:
                            captcha_task.cancel()
                            self.log("Button click failed - attempting reaction fallback", "INFO")
                            reaction_success = await self.add_giveaway_reaction(message, client)
                            if reaction_success:
                                join_was_successful = True
                                await self.update_stats("joined", str(message.author.id), prize)
                                await self.record_joined_giveaway(message, embed, prize, client)
                                self.log(f"Successfully joined via reaction fallback: {prize[:50]}{'...' if len(prize) > 50 else ''} | Account: {client.user.name}", "SUCCESS")
                                self.bot.loop.create_task(self.send_unified_webhook(
                                    title="🎉 Joined Giveaway (Reaction Fallback)!", 
                                    description=(f"**🎁 Prize:** {prize}\n"
                                    f"**🤖 Bot:** {message.author.name}\n"
                                    f"**📝 Method:** Reaction (Button Failed)"), 
                                    color=0xFFA500, 
                                    footer_text=f"Giveaway Joiner V{__version__} • Joined (Fallback)", 
                                    message=message, 
                                    embed=embed, 
                                    show_fp_suggestion=True, 
                                    client=client
                                ))
                                if hasattr(self.bot, '_giveaway_joiner_tab'):
                                    self.bot._giveaway_joiner_tab.toast(type="SUCCESS", title="Joined (Fallback)!", description=f"Prize: {prize[:30]} | Account: {client.user.name}")
                            else:
                                self.log(f"Failed to join (both button and reaction): {prize[:50]}{'...' if len(prize) > 50 else ''} | Account: {client.user.name}", "ERROR")
                                await self.record_joined_giveaway(message, embed, prize, client)
                                if not self.config.get("webhook_disable_fail_join", False):
                                    self.bot.loop.create_task(self.send_unified_webhook(
                                        title="❌ Failed to Join Giveaway", 
                                        description=(f"**🎁 Prize:** {prize}\n"
                                        f"**🤖 Bot:** {message.author.name}\n"
                                        f"**❔ Reason:** Button click and reaction fallback failed."), 
                                        color=0xFF0000, 
                                        footer_text=f"Giveaway Joiner V{__version__} • Join Failure", 
                                        message=message, 
                                        embed=embed, 
                                        show_fp_suggestion=True, 
                                        client=client
                                    ))
            
            except Exception as e:
                self.log(f"Error in process_message | Account: {client.user.name}: {str(e)}", "ERROR")
                traceback.print_exc()

        # --- UI CREATION ---
        async def update_token_table_ui(self):
            token_table = self.ui.get("token_table")
            if not token_table: return
            
            rows = []
            for username, data in self.tokens.items():
                status_text = "Valid" if data.get("valid", False) else "Invalid"
                status_color = "success" if data.get("valid", False) else "danger"
                rows.append({
                    "id": username,
                    "cells": [
                        {"text": username},
                        {"text": data.get("token", "N/A")[:10] + "..." + data.get("token", "N/A")[-4:]},
                        {"text": status_text, "color": status_color},
                        {"text": data.get("date_added", "N/A").split("T")[0]},
                        {} # For remove button
                    ]
                })
            token_table.rows = rows

        def populate_bot_table_from_cache(self):
            bot_list = list(set(self.config.get("monitored_bots", [])))
            rows = []
            default_avatar = "https://cdn.discordapp.com/embed/avatars/0.png"

            for bot_id in bot_list:
                cached_data = self.bot_cache.get(bot_id, {})
                username = cached_data.get("name", f"Bot ID: {bot_id}")
                avatar_url = cached_data.get("avatar_url", default_avatar)

                rows.append({
                    "id": bot_id,
                    "cells": [
                        {"text": username, "imageUrl": avatar_url},
                        {"text": bot_id},
                        {}
                    ]
                })

            if not rows:
                rows.append({"id": "none", "cells": [{"text": "No bots monitored.", "imageUrl": default_avatar}, {"text": ""}, {}]})
            
            self.ui["monitored_bots_table"].rows = rows

        async def verify_bot_cache(self):
            await asyncio.sleep(5)
            self.log("Verifying bot cache", "DEBUG")
            
            default_avatar = "https://cdn.discordapp.com/embed/avatars/0.png"
            cache_updated = False

            for bot_id in self.config.get("monitored_bots", []):
                try:
                    user = await self.bot.fetch_user(int(bot_id))
                    new_name = user.name
                    new_avatar_url = user.avatar.url if user.avatar else default_avatar
                    
                    cached_data = self.bot_cache.get(bot_id, {})
                    old_name = cached_data.get("name")
                    old_avatar_url = cached_data.get("avatar_url")
                    
                    if new_name != old_name or new_avatar_url != old_avatar_url:
                        self.log(f"Bot cache outdated for {bot_id}. Updating.", "DEBUG")
                        self.bot_cache[bot_id] = {"name": new_name, "avatar_url": new_avatar_url}
                        cache_updated = True
                        
                        self.ui["monitored_bots_table"].update_rows([{
                            "id": bot_id,
                            "cells": [
                                {"text": new_name, "imageUrl": new_avatar_url},
                                {"text": bot_id},
                                {}
                            ]
                        }])
                    
                    await asyncio.sleep(.2)
                
                except (discord.NotFound, discord.HTTPException):
                    pass
                except Exception as e:
                    self.log(f"Error verifying bot cache for {bot_id}: {e}", "ERROR")

            if cache_updated:
                await self.save_bot_cache()
        
        async def update_token_select_list(self):
            token_select = self.ui.get("token_select_list")
            if not token_select: return
            
            items = []
            default_avatar = "https://cdn.discordapp.com/embed/avatars/0.png"

            for username, data in self.tokens.items():
                if data.get("is_main", False):
                    continue
                status = " (Invalid)" if not data.get("valid", False) else ""
                avatar_url = data.get("avatar_url", default_avatar)
                
                items.append({
                    "id": username,
                    "title": f"{username}{status}",
                    "iconUrl": avatar_url
                })

            if not items:
                items.append({
                    "id": "none",
                    "title": "No tokens added",
                    "iconUrl": default_avatar
                })
            
            token_select.items = items

        async def update_server_list_from_all_clients(self):
            self.log("Fetching server lists from all clients...", "DEBUG")
            all_servers = {}
            default_icon = "https://cdn.discordapp.com/embed/avatars/0.png"

            for client_data in self.running_clients.values():
                client = client_data.get("client")
                if client:
                    for server in client.guilds:
                        all_servers[server.id] = server

            excluded_ids = set(self.config.get("excluded_servers", []))
            active_server_list = []
            excluded_server_list = []

            for server_id, server in all_servers.items():
                server_row = {
                    "id": str(server_id), 
                    "title": server.name, 
                    "iconUrl": server.icon.url if server.icon else default_icon
                }
                
                if str(server_id) in excluded_ids:
                    excluded_server_list.append(server_row)
                else:
                    active_server_list.append(server_row)

            active_server_list.sort(key=lambda x: x["title"].lower())
            excluded_server_list.sort(key=lambda x: x["title"].lower())
            servers_select_list = [{"id": "select_server", "title": "Select servers to exclude"}] + active_server_list + excluded_server_list
            
            self.ui["excluded_servers_select"].items = servers_select_list
            self.ui["excluded_servers_select"]._full_list = servers_select_list
            
            self.log(f"Server exclusion list populated with {len(all_servers)} unique servers.", "DEBUG")

        def populate_ui_with_data(self):
            try:
                # Stats
                self.bot._giveaway_stats_text.content = (
                    f"• Messages analyzed: {self.stats['total_scanned']}\n"
                    f"• Detected: {self.stats['total_detected']}\n"
                    f"• Joined: {self.stats['total_joined']}\n"
                    f"• Won: {self.stats['total_won']}\n"
                    f"• Filtered: {self.stats['total_filtered']}\n"
                    f"• Captchas: {self.stats['total_captchas']}\n"
                    f"• Success Rate: {(self.stats['total_joined']/max(self.stats['total_detected'], 1)*100):.1f}%"
                )
                
                # Toggles
                self.ui["status_toggle"].checked = self.config.get("enabled", False)
                self.ui["status_toggle"].label = "Enable Giveaway Joiner" + (" (Running)" if self.config.get("enabled", False) else "")
                self.ui["webhook_toggle"].checked = self.config.get("webhook_enabled", False)
                self.ui["webhook_mention_win_toggle"].checked = self.config.get("webhook_mention_user", False)
                self.ui["webhook_mention_captcha_toggle"].checked = self.config.get("webhook_mention_captcha", False)
                self.ui["webhook_mention_manual_toggle"].checked = self.config.get("webhook_mention_manual", False)
                self.ui["webhook_mention_ticket_toggle"].checked = self.config.get("webhook_mention_ticket", False)
                self.ui["webhook_mention_req_toggle"].checked = self.config.get("webhook_mention_requirements", False)
                self.ui["webhook_mention_token_fail_toggle"].checked = self.config.get("webhook_mention_token_fail", True)
                self.ui["webhook_disable_fail_join_toggle"].checked = self.config.get("webhook_disable_fail_join", False)
                self.ui["debug_toggle"].checked = self.config.get("debug_mode", False)
                self.ui["prize_claim_toggle"].checked = self.config.get("prize_claim_enabled", True)
                self.ui["auto_claim_toggle"].checked = self.config.get("auto_claim_ticket_enabled", True)
                self.ui["auto_dm_toggle"].checked = self.config.get("auto_claim_dm_enabled", False)
                self.ui["auto_claim_send_toggle"].checked = self.config.get("auto_claim_send_message", False)
                alts_claiming_enabled = self.config.get("enable_alts_for_claiming", False)
                self.ui["alts_claim_toggle"].checked = alts_claiming_enabled
                self.ui["solver_toggle"].checked = self.config.get("auto_solve_captchas", False)

                # Inputs
                self.ui["webhook_input"].value = self.config.get("webhook_url", "")
                self.ui["blacklist_input"].value = ", ".join(self.config.get("blacklist_keywords", []))
                self.ui["min_delay_input"].value = str(self.config.get("join_delay_min", 2))
                self.ui["max_delay_input"].value = str(self.config.get("join_delay_max", 8))
                self.ui["auto_claim_message_input"].value = self.config.get("auto_claim_message", "")
                self.ui["timeout_input_gw"].value = str(self.config.get("ticket_wait_timeout", 3600))
                self.ui["flaresolverr_url_input"].value = self.config.get("flaresolverr_url", "http://localhost:8191")

                # Visibility
                auto_claim_enabled = self.config.get("auto_claim_ticket_enabled", True)
                prize_claim_enabled = self.config.get("prize_claim_enabled", True)
                self.ui["auto_claim_toggle"].visible = prize_claim_enabled
                self.ui["auto_dm_toggle"].visible = prize_claim_enabled
                self.ui["timeout_input_gw"].visible = prize_claim_enabled
                self.ui["alts_claim_toggle"].visible = prize_claim_enabled
                self.ui["auto_claim_message_group"].visible = auto_claim_enabled
                self.ui["auto_claim_message_input"].visible = self.config.get("auto_claim_send_message", False)
                self.ui["flaresolverr_url_input"].visible = self.config.get("auto_solve_captchas", False)

                # FlareSolverr buttons
                flaresolverr_installed = self.config.get("flaresolverr_installed", False)
                self.ui["flaresolverr_status_text"].content = "Status: Installed (Starts with Windows)" if flaresolverr_installed else "Status: Not Installed"
                self.ui["flaresolverr_download_button"].visible = not flaresolverr_installed
                self.ui["flaresolverr_open_folder_button"].visible = flaresolverr_installed
                self.ui["flaresolverr_startup_toggle"].visible = flaresolverr_installed
                self.ui["flaresolverr_startup_toggle"].checked = os.path.exists(self.get_startup_bat_path())
                
                # Excluded Servers
                servers_select_list = [{"id": "select_server", "title": "Select servers to exclude"}]
                for server in self.bot.guilds:
                    server_row = {"id": str(server.id), "title": server.name, "iconUrl": server.icon.url if server.icon else "https."}
                    servers_select_list.append(server_row)
                self.ui["excluded_servers_select"].items = servers_select_list
                self.ui["excluded_servers_select"].selected_items = self.config.get("excluded_servers", [])

                # Token Table
                self.bot.loop.create_task(self.update_token_select_list())
                
                self.log("UI populated with loaded data.", "DEBUG")

            except Exception as e:
                self.log(f"Error populating UI: {e}", "ERROR")
                traceback.print_exc()

    def create_giveaway_ui(manager_ref):
        ui = {}
        tab = Tab(name="Giveaway Joiner", title="Giveaway Joiner Control Panel", icon="gift")
        bot._giveaway_joiner_tab = tab
        
        main_container = tab.create_container(type="columns", gap=10)
        
        # --- Card 1: Global Controls, Tokens & Debug ---
        controls_card = main_container.create_card(width="full", height="full", gap=4)
        controls_card.create_ui_element(UI.Text, content="Global Controls", size="xl", weight="bold")
        
        async def on_status_toggle(checked):
            manager = manager_ref()
            if not manager:
                tab.toast(type="ERROR", title="Script not ready", description="The script is starting, please wait a moment.")
                return
            manager.config["enabled"] = checked
            await manager.save_config_gw()
            if checked:
                manager.ui["status_toggle"].label = "Enable Giveaway Joiner (Starting...)"
                tab.toast(type="SUCCESS", title="Script Enabled", description="Starting clients in background...")
                manager.bot.loop.create_task(manager.start_all_clients())
            else:
                manager.ui["status_toggle"].label = "Enable Giveaway Joiner (Stopping...)"
                await manager.stop_all_clients()
                manager.ui["status_toggle"].label = "Enable Giveaway Joiner"
                tab.toast(type="INFO", title="Script Disabled", description="All clients stopped.")

        ui["status_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Enable Giveaway Joiner", checked=False, onChange=on_status_toggle)
        
        controls_card.create_ui_element(UI.Text, content="📊 Statistics", size="lg", weight="bold", margin="mt-4")
        stats_text = controls_card.create_ui_element(UI.Text, content="Loading stats...", size="sm", color="var(--text-muted)")
        bot._giveaway_stats_text = stats_text
        
        controls_card.create_ui_element(UI.Text, content="Webhook Notifications", weight="bold", size="lg", margin="mt-4")
        
        async def on_webhook_toggle(checked):
            manager = manager_ref(); manager.config["webhook_enabled"] = checked; await manager.save_config_gw()
            tab.toast(type="SUCCESS" if checked else "INFO", title="Webhook Notifications Updated", description=f"Webhook notifications {'enabled' if checked else 'disabled'}")
        
        ui["webhook_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Enable Webhook Notifications", checked=False, onChange=on_webhook_toggle)
        ui["webhook_input"] = controls_card.create_ui_element(UI.Input, label="Webhook URL", placeholder="https://discord.com/api/webhooks/...", full_width=True)
        
        async def on_webhook_save():
            manager = manager_ref(); manager.config["webhook_url"] = ui["webhook_input"].value.strip(); await manager.save_config_gw()
            tab.toast(type="SUCCESS", title="Webhook Saved", description="Webhook URL has been saved")
        
        controls_card.create_ui_element(UI.Button, label="Save Webhook", color="primary", full_width=True, margin="mt-2", onClick=on_webhook_save)
        
        async def on_mention_win(checked): manager = manager_ref(); manager.config["webhook_mention_user"] = checked; await manager.save_config_gw()
        async def on_mention_captcha(checked): manager = manager_ref(); manager.config["webhook_mention_captcha"] = checked; await manager.save_config_gw()
        async def on_mention_manual(checked): manager = manager_ref(); manager.config["webhook_mention_manual"] = checked; await manager.save_config_gw()
        async def on_mention_ticket(checked): manager = manager_ref(); manager.config["webhook_mention_ticket"] = checked; await manager.save_config_gw()
        async def on_mention_req(checked): manager = manager_ref(); manager.config["webhook_mention_requirements"] = checked; await manager.save_config_gw()
        async def on_mention_token_fail(checked): manager = manager_ref(); manager.config["webhook_mention_token_fail"] = checked; await manager.save_config_gw()
        async def on_disable_fail_join_toggle(checked): manager = manager_ref(); manager.config["webhook_disable_fail_join"] = checked; await manager.save_config_gw()
        
        ui["webhook_mention_win_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Mention on Win", checked=False, onChange=on_mention_win)
        ui["webhook_mention_captcha_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Mention on Captcha", checked=False, onChange=on_mention_captcha)
        ui["webhook_mention_manual_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Mention on Manual Join", checked=False, onChange=on_mention_manual)
        ui["webhook_mention_ticket_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Mention on Manual Ticket", checked=False, onChange=on_mention_ticket)
        ui["webhook_mention_req_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Mention on Requirements Denied", checked=False, onChange=on_mention_req)
        ui["webhook_mention_token_fail_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Mention on Token Failure", checked=True, onChange=on_mention_token_fail)
        ui["webhook_disable_fail_join_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Disable 'Failed to Join' Logs", checked=False, onChange=on_disable_fail_join_toggle)

        # --- Token Management ---
        controls_card.create_ui_element(UI.Text, content="Token Management", size="xl", weight="bold", margin="mt-4")
        
        async def on_token_input(value):
            button = ui.get("add_token_button")
            if not button: return            
            if len(value.strip()) > 50:
                button.disabled = False
            else:
                button.disabled = True

        token_input_group = controls_card.create_group(type="columns", gap=8)
        ui["token_input"] = token_input_group.create_ui_element(
            UI.Input, 
            label="New Token", 
            placeholder="Enter Token", 
            full_width=True,
            onInput=on_token_input
        )
        
        async def handle_add_token_click():
            manager = manager_ref()
            if not manager:
                tab.toast(type="ERROR", title="Script not ready", description="The script is starting, please wait a moment.")
                return
            token = ui["token_input"].value.strip()
            if not token:
                tab.toast(type="ERROR", title="Error", description="Token field is empty.")
                return
            
            ui["add_token_button"].loading = True
            ui["add_token_button"].label = "Verifying..."
            
            result_message = await manager.add_token_to_storage(token)
            
            if "Success" in result_message:
                tab.toast(type="SUCCESS", title="Token Added", description=result_message)
                await manager.update_token_select_list()
                tab.toast(type="INFO", title="Updating Servers", description="Fetching server list from new token...")
                await asyncio.sleep(2)
                await manager.update_server_list_from_all_clients()
            else:
                tab.toast(type="ERROR", title="Error Adding Token", description=result_message)

            ui["token_input"].value = ""
            ui["add_token_button"].loading = False
            ui["add_token_button"].label = "Add Token"
            ui["add_token_button"].disabled = True

        ui["add_token_button"] = token_input_group.create_ui_element(
            UI.Button, 
            label="Add Token", 
            color="primary", 
            onClick=handle_add_token_click,
            disabled=True
        )
        
        async def handle_import_nighty():
            manager = manager_ref()
            if not manager:
                tab.toast(type="ERROR", title="Script not ready", description="The script is starting, please wait a moment.")
                return
            
            btn = ui["import_nighty_btn"]
            btn.loading = True
            btn.label = "Importing..."
            
            try:
                msg = await manager.import_tokens_from_nighty_config()
                
                if "Error" in msg:
                    tab.toast(type="ERROR", title="Import Failed", description=msg)
                else:
                    tab.toast(type="SUCCESS", title="Import Results", description=msg)
                    
                    await manager.update_token_select_list()
                    if "0 added" not in msg:
                        await manager.update_token_select_list()
                        tab.toast(type="INFO", title="Updating", description="New tokens detected. Refreshing server lists...")
                        await manager.update_server_list_from_all_clients()
                    else:
                        pass

            except Exception as e:
                 tab.toast(type="ERROR", title="Error", description=str(e))
            
            btn.loading = False
            btn.label = "Load tokens from Nighty"

        ui["import_nighty_btn"] = controls_card.create_ui_element(
            UI.Button,
            label="Load tokens from Nighty",
            color="default", 
            full_width=True,
            onClick=handle_import_nighty
        )

        async def handle_remove_token(selected_ids):
            manager = manager_ref()
            if not manager:
                tab.toast(type="ERROR", title="Script not ready", description="The script is starting, please wait a moment.")
                return
            if not selected_ids: return 
            
            username = selected_ids[0] 
            if username == "none": return

            if await manager.remove_token_from_storage(username):
                tab.toast(type="SUCCESS", title="Token Removed", description=f"Stopped and removed client for {username}.")
                await manager.update_token_select_list()
                await manager.update_server_list_from_all_clients()
            else:
                tab.toast(type="ERROR", title="Error", description="Could not remove token.")
            
            ui["token_select_list"].selected_items = []
        
        ui["token_select_list"] = controls_card.create_ui_element(UI.Select,
            label="Added Tokens (Select to remove)",
            full_width=True,
            mode="single",
            disabled_items=["none"],
            items=[{"id": "none", "title": "Loading tokens...", "iconUrl": "https://cdn.discordapp.com/embed/avatars/0.png"}],
            onChange=handle_remove_token
        )

        controls_card.create_ui_element(UI.Text, content="Debug Settings", weight="bold", size="lg", margin="mt-4")
        
        async def on_debug_toggle(checked): manager = manager_ref(); manager.config["debug_mode"] = checked; await manager.save_config_gw()
        
        ui["debug_toggle"] = controls_card.create_ui_element(UI.Toggle, label="Enable Debug Mode", checked=False, onChange=on_debug_toggle)
        
        def open_file_log():
            manager = manager_ref()
            if not manager or not os.path.exists(manager.log_path):
                tab.toast(type="ERROR", title="File Not Found", description="Log file not found.")
                return
            os.startfile(manager.log_path)
        
        controls_card.create_ui_element(UI.Button, label="Open log file", onClick=open_file_log, full_width=True)

        # --- Card 2: Bot Management ---
        bots_card = main_container.create_card(width="full", height="full", gap=4)
        bots_card.create_ui_element(UI.Text, content="Monitored Bots", size="xl", weight="bold")
        
        async def on_bot_id_input(value):
            manager = manager_ref()
            if not manager: return
            
            if manager.input_debounce_task and not manager.input_debounce_task.done():
                manager.input_debounce_task.cancel()
            
            async def validate_logic():
                await asyncio.sleep(0.15)
                
                button = ui.get("add_bot_button")
                input_field = ui.get("bot_id_input")
                if not button or not input_field: return

                bot_id = value.strip()
                
                should_be_disabled = True
                is_invalid = False
                error_msg = ""

                if not bot_id:
                    should_be_disabled = True
                    is_invalid = False
                    error_msg = ""
                elif not bot_id.isdigit() or len(bot_id) < 17:
                    should_be_disabled = True
                    is_invalid = True
                    error_msg = "Must be a valid 17+ digit ID"
                elif bot_id in manager.config["monitored_bots"]:
                    should_be_disabled = True
                    is_invalid = True
                    error_msg = "Bot is already monitored"
                else:
                    should_be_disabled = False
                    is_invalid = False
                    error_msg = ""
                
                if button.disabled != should_be_disabled:
                    button.disabled = should_be_disabled
                
                if input_field.invalid != is_invalid:
                    input_field.invalid = is_invalid
                    
                if input_field.error_message != error_msg:
                    input_field.error_message = error_msg

            manager.input_debounce_task = bot.loop.create_task(validate_logic())

        bot_input_group = bots_card.create_group(type="columns", gap=8)
        
        ui["bot_id_input"] = bot_input_group.create_ui_element(
            UI.Input, 
            label="Bot ID", 
            placeholder="Enter Bot ID to add", 
            full_width=True,
            onInput=on_bot_id_input
        )

        async def handle_add_bot():
            manager = manager_ref()
            if not manager:
                tab.toast(type="ERROR", title="Script not ready", description="The script is starting, please wait a moment.")
                return
            
            button = ui.get("add_bot_button")
            if not button: return

            button.loading = True
            bot_id = ui["bot_id_input"].value.strip()
            
            if bot_id and bot_id.isdigit() and len(bot_id) >= 17:
                if bot_id not in manager.config["monitored_bots"]:
                    
                    default_avatar = "https://cdn.discordapp.com/embed/avatars/0.png"
                    try:
                        user = await bot.fetch_user(int(bot_id))
                        user_display = user.name 
                        user_avatar = user.avatar.url if user.avatar else default_avatar
                    except discord.NotFound:
                        user_display = "Unknown Bot"
                        user_avatar = default_avatar
                    except Exception as e:
                        manager.log(f"Error fetching user {bot_id}: {str(e)}", "ERROR")
                        user_display = "Error Fetching Bot"
                        user_avatar = default_avatar
                    
                    manager.config["monitored_bots"].append(bot_id)
                    manager.bot_cache[bot_id] = {"name": user_display, "avatar_url": user_avatar}
                    await manager.save_config_gw()
                    await manager.save_bot_cache()
                    
                    ui["monitored_bots_table"].insert_rows([{
                        "id": bot_id,
                        "cells": [
                            {"text": user_display, "imageUrl": user_avatar},
                            {"text": bot_id},
                            {}
                        ]
                    }])
                    
                    tab.toast(type="SUCCESS", title="Bot Added", description=f"Now monitoring bot ID: {bot_id}")
                else:
                    tab.toast(type="ERROR", title="Error", description="Bot ID already being monitored")
            else:
                tab.toast(type="ERROR", title="Error", description="Please enter a valid bot ID")
            
            ui["bot_id_input"].value = ""
            button.loading = False
            button.disabled = True
        
        ui["add_bot_button"] = bot_input_group.create_ui_element(
            UI.Button, 
            label="Add Bot", 
            color="primary", 
            onClick=handle_add_bot,
            disabled=True
        )
        
        async def handle_remove_bot(row_id):
            manager = manager_ref()
            if not manager or row_id == "none": return
            
            bot_id = row_id
            if bot_id in manager.config["monitored_bots"]:
                manager.config["monitored_bots"].remove(bot_id)
                if bot_id in manager.bot_cache:
                    del manager.bot_cache[bot_id]
                
                await manager.save_config_gw()
                await manager.save_bot_cache()
                
                manager.populate_bot_table_from_cache()
                tab.toast(type="SUCCESS", title="Bot Removed", description=f"Bot {bot_id} is no longer monitored.")

        ui["monitored_bots_table"] = bots_card.create_ui_element(UI.Table, 
            selectable=False, 
            search=True, 
            items_per_page=5,
            columns=[
                {"type": "text", "label": "User"},
                {"type": "text", "label": "User ID"},
                {"type": "button", "label": "Actions", "buttons": [
                    {"label": "Remove", "color": "danger", "onClick": handle_remove_bot}
                ]}
            ],
            rows=[]
        )

        # --- Card 3: Settings & Configuration ---
        settings_card = main_container.create_card(width="full", height="full", gap=4)
        settings_card.create_ui_element(UI.Text, content="Settings & Configuration", size="xl", weight="bold")

        settings_card.create_ui_element(UI.Text, content="Filter Settings", weight="bold", size="lg", margin="mt-1")
        ui["blacklist_input"] = settings_card.create_ui_element(UI.Input, label="Blacklist Keywords (comma separated)", placeholder="ban, kick, mute", full_width=True)
        
        settings_card.create_ui_element(UI.Text, content="Delay Settings", weight="bold", size="lg", margin="mt-4")
        delay_group = settings_card.create_group(type="columns", gap=8, full_width=True)
        ui["min_delay_input"] = delay_group.create_ui_element(UI.Input, label="Min Delay (s)", placeholder="2", full_width=True)
        ui["max_delay_input"] = delay_group.create_ui_element(UI.Input, label="Max Delay (s)", placeholder="8", full_width=True)
        
        settings_card.create_ui_element(UI.Text, content="Ticket Panel & Prize Claim", weight="bold", size="lg", margin="mt-4")
        
        async def on_prize_claim_toggle(checked):
            manager = manager_ref(); manager.config["prize_claim_enabled"] = checked; await manager.save_config_gw()
            ui["auto_claim_toggle"].visible = checked
            ui["timeout_input_gw"].visible = checked
            ui["alts_claim_toggle"].visible = checked
            ui["auto_dm_toggle"].visible = checked
        ui["prize_claim_toggle"] = settings_card.create_ui_element(UI.Toggle, label="Enable Prize Claim Detection", checked=True, onChange=on_prize_claim_toggle)

        async def on_alts_claim_toggle(checked):
            manager = manager_ref(); manager.config["enable_alts_for_claiming"] = checked; await manager.save_config_gw()
            tab.toast(type="SUCCESS", title="Setting Updated", description=f"Alts claiming tickets {'Enabled' if checked else 'Disabled'}")
        
        ui["alts_claim_toggle"] = settings_card.create_ui_element(
            UI.Toggle, 
            label="Enable Alts for Prize Claiming", 
            checked=False, 
            onChange=on_alts_claim_toggle,
            visible=False
        )

        async def on_auto_claim_toggle(checked):
            manager = manager_ref(); manager.config["auto_claim_ticket_enabled"] = checked; await manager.save_config_gw()
            ui["auto_claim_message_group"].visible = checked 
        ui["auto_claim_toggle"] = settings_card.create_ui_element(UI.Toggle, label="Enable Auto-Claim Ticket", checked=True, onChange=on_auto_claim_toggle)
        
        async def on_auto_dm_toggle(checked):
            manager = manager_ref(); manager.config["auto_claim_dm_enabled"] = checked; await manager.save_config_gw()
        
        ui["auto_dm_toggle"] = settings_card.create_ui_element(
            UI.Toggle, 
            label="Enable Auto-Claim via DM", 
            checked=False, 
            onChange=on_auto_dm_toggle
        )
        ui["auto_claim_message_group"] = settings_card.create_group(type="rows", gap=8, full_width=True, margin="mt-2")
        
        async def on_auto_claim_send_toggle(checked):
            manager = manager_ref(); manager.config["auto_claim_send_message"] = checked; await manager.save_config_gw()
            ui["auto_claim_message_input"].visible = checked 
        ui["auto_claim_send_toggle"] = ui["auto_claim_message_group"].create_ui_element(UI.Toggle, label="Send Message After Auto-Claiming", checked=False, onChange=on_auto_claim_send_toggle)
        ui["auto_claim_message_input"] = ui["auto_claim_message_group"].create_ui_element(UI.Input, label="Message to Send", placeholder="Hello, I'm here to claim my prize!", full_width=True, visible=False)

        ui["timeout_input_gw"] = settings_card.create_ui_element(UI.Input, label="Max Wait Time for Ticket Message (s)", placeholder="3600", full_width=True)
        
        settings_card.create_ui_element(UI.Text, content="Captcha Solver Settings", weight="bold", size="lg", margin="mt-4")
        
        async def on_solver_toggle(checked):
            manager = manager_ref(); manager.config["auto_solve_captchas"] = checked; await manager.save_config_gw()
            ui["flaresolverr_url_input"].visible = checked
        ui["solver_toggle"] = settings_card.create_ui_element(UI.Toggle, label="Enable Auto-Solver (FlareSolverr)", checked=False, onChange=on_solver_toggle)
        ui["flaresolverr_url_input"] = settings_card.create_ui_element(UI.Input, label="FlareSolverr URL", placeholder="http://localhost:8191", full_width=True, visible=False)

        settings_card.create_ui_element(UI.Text, content="FlareSolverr Management", weight="bold", size="lg", margin="mt-4")
        
        def open_flaresolverr_folder(*args):
            manager = manager_ref()
            if os.path.exists(manager.flaresolverr_dir): os.startfile(manager.flaresolverr_dir)
            else: tab.toast(type="ERROR", title="Error", description="Folder not found.")
        
        startup_bat_exists = False
        manager = manager_ref()
        if manager and hasattr(manager, 'get_startup_bat_path'):
            try:
                startup_path = manager.get_startup_bat_path()
                startup_bat_exists = os.path.exists(startup_path)
            except Exception as e:
                print(f"Error checking startup path: {e}")
                startup_bat_exists = False

        async def on_startup_toggle_change(checked):
            manager = manager_ref()
            if not manager: return
            
            success, msg = manager.toggle_startup_shortcut(checked)
            if success:
                tab.toast(type="SUCCESS", title="Startup Settings", description=msg)
                installed = manager.config.get("flaresolverr_installed", False)
                status_msg = "Installed (Starts with Windows)" if checked else "Installed (Manual Start)"
                ui["flaresolverr_status_text"].content = f"Status: {status_msg}" if installed else "Status: Not Installed"
            else:
                tab.toast(type="ERROR", title="Error", description=msg)
                ui["flaresolverr_startup_toggle"].checked = not checked

        ui["flaresolverr_status_text"] = settings_card.create_ui_element(UI.Text, content="Status: Not Installed", size="sm", color="var(--text-muted)")
        ui["flaresolverr_download_button"] = settings_card.create_ui_element(UI.Button, label="Download and Install FlareSolverr", color="primary", full_width=True, visible=True)
        ui["flaresolverr_open_folder_button"] = settings_card.create_ui_element(UI.Button, label="Open FlareSolverr Folder", color="default", full_width=True, visible=False, onClick=open_flaresolverr_folder)
        ui["flaresolverr_startup_toggle"] = settings_card.create_ui_element(UI.Toggle, label="Start FlareSolverr with Windows", checked=startup_bat_exists, onChange=on_startup_toggle_change)

        def handle_download_flaresolverr(*args):
            manager = manager_ref()
            tab.toast(type="INFO", title="Downloading FlareSolverr", description="Please wait...")
            manager.log("Downloading FlareSolverr", "INFO")
            bot.loop.create_task(manager.download_flaresolverr(tab, ui["flaresolverr_status_text"], ui["flaresolverr_download_button"], ui["flaresolverr_open_folder_button"]))
        ui["flaresolverr_download_button"].onClick = handle_download_flaresolverr

        settings_card.create_ui_element(UI.Text, content="Server Exclusions", weight="bold", size="lg", margin="mt-1")
        
        def filter_server_list(search_value):
            manager = manager_ref()
            search_lower = search_value.lower().strip()
            full_list = ui["excluded_servers_select"]._full_list
            if not search_lower:
                ui["excluded_servers_select"].items = full_list
                return
            placeholder = full_list[0]
            filtered = [s for s in full_list[1:] if search_lower in s["title"].lower()]
            ui["excluded_servers_select"].items = [placeholder] + filtered

        ui["server_search_input"] = settings_card.create_ui_element(UI.Input, label="Search Servers", placeholder="Type to filter...", full_width=True, onInput=filter_server_list)
        
        async def update_excluded_servers(selected):
            manager = manager_ref()
            if not manager: return
            
            manager.config["excluded_servers"] = selected
            
            if manager.server_save_task and not manager.server_save_task.done():
                manager.server_save_task.cancel()

            async def delayed_save():
                await asyncio.sleep(1.5)
                try:
                    await manager.save_config_gw()
                    tab.toast(type="SUCCESS", title="Servers Saved", description=f"Exclusion list updated ({len(selected)} servers).")
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    tab.toast(type="ERROR", title="Save Error", description=str(e))

            manager.server_save_task = bot.loop.create_task(delayed_save())
        
        ui["excluded_servers_select"] = settings_card.create_ui_element(UI.Select, label="Excluded Servers", full_width=True, disabled_items=['select_server'], selected_items=[], mode="multiple", items=[{"id": "select_server", "title": "Select servers to exclude"}], onChange=update_excluded_servers)
        ui["excluded_servers_select"]._full_list = []
        
        settings_card.create_ui_element(UI.Text, content="Channel Exclusions", weight="bold", size="lg", margin="mt-4")
        
        async def update_channel_list():
            manager = manager_ref()
            if not manager: return
            
            items = []
            default_icon = "https://cdn.discordapp.com/embed/avatars/0.png" 
            current_list = manager.config.get("excluded_channels", [])
            
            for cid in current_list:
                icon = default_icon
                title = f"Channel ID: {cid}"
                
                try:
                    channel_obj = manager.bot.get_channel(int(cid))
                    
                    if not channel_obj:
                        for client_data in manager.running_clients.values():
                            c = client_data.get("client")
                            if c:
                                channel_obj = c.get_channel(int(cid))
                                if channel_obj: break
                    
                    if channel_obj:
                        guild_name = channel_obj.guild.name if channel_obj.guild else "Direct Message"
                        chan_name = channel_obj.name
                        title = f"#{chan_name} | {guild_name}"
                        
                        if channel_obj.guild and channel_obj.guild.icon:
                            icon = channel_obj.guild.icon.url
                except Exception:
                    pass

                items.append({"id": cid, "title": title, "iconUrl": icon})
            
            if not items:
                items.append({"id": "none", "title": "No channels excluded", "iconUrl": default_icon, "disabled": True})
            
            if "excluded_channels_list" in ui:
                ui["excluded_channels_list"].items = items
                ui["excluded_channels_list"].selected_items = []

        async def on_channel_id_input(value):
            manager = manager_ref()
            if not manager: return
            
            if manager.input_debounce_task and not manager.input_debounce_task.done():
                manager.input_debounce_task.cancel()
            
            async def validate_channel_logic():
                await asyncio.sleep(0.15)
                
                button = ui.get("excl_channel_btn")
                input_field = ui.get("excl_channel_input")
                if not button or not input_field: return

                chan_id = value.strip()
                current_list = manager.config.get("excluded_channels", [])

                should_be_disabled = True
                is_invalid = False
                error_msg = ""

                if not chan_id:
                    should_be_disabled = True
                    is_invalid = False
                    error_msg = ""
                elif not chan_id.isdigit() or len(chan_id) < 17:
                    should_be_disabled = True
                    is_invalid = True
                    error_msg = "Must be a valid 17+ digit ID"
                elif chan_id in current_list:
                    should_be_disabled = True
                    is_invalid = True
                    error_msg = "Channel already excluded"
                else:
                    should_be_disabled = False
                    is_invalid = False
                    error_msg = ""

                if button.disabled != should_be_disabled: button.disabled = should_be_disabled
                if input_field.invalid != is_invalid: input_field.invalid = is_invalid
                if input_field.error_message != error_msg: input_field.error_message = error_msg

            manager.input_debounce_task = bot.loop.create_task(validate_channel_logic())
        
        channel_excl_group = settings_card.create_group(type="columns", gap=8)
        
        ui["excl_channel_input"] = channel_excl_group.create_ui_element(
            UI.Input, 
            label="Channel ID", 
            placeholder="123456789", 
            full_width=True,
            onInput=on_channel_id_input
        )

        async def add_excluded_channel():
            manager = manager_ref()
            if not manager: return
            
            button = ui.get("excl_channel_btn")
            input_field = ui.get("excl_channel_input")
            
            if button.loading: 
                return
            
            button.loading = True
            button.label = "Saving..."
            
            try:
                chan_id = input_field.value.strip()
                
                if not chan_id.isdigit() or len(chan_id) < 17:
                    tab.toast(type="ERROR", title="Invalid ID", description="Invalid Channel ID.")
                    button.loading = False
                    button.label = "Exclude Channel"
                    return

                current_list = manager.config.get("excluded_channels", [])
                if chan_id not in current_list:
                    current_list.append(chan_id)
                    manager.config["excluded_channels"] = current_list
                    await manager.save_config_gw()
                    
                    await update_channel_list()
                    tab.toast(type="SUCCESS", title="Channel Excluded", description=f"Added {chan_id}.")
                
                input_field.value = ""
                button.disabled = True 
                
            except Exception as e:
                tab.toast(type="ERROR", title="Error", description=str(e))
            
            button.loading = False
            button.label = "Exclude Channel"

        ui["excl_channel_btn"] = channel_excl_group.create_ui_element(
            UI.Button, 
            label="Exclude Channel", 
            color="danger", 
            onClick=add_excluded_channel,
            disabled=True
        )

        async def remove_excluded_channel(selected):
            manager = manager_ref()
            if not manager or not selected: return
            item_id = selected[0]
            if item_id == "none": return

            current_list = manager.config.get("excluded_channels", [])
            if item_id in current_list:
                current_list.remove(item_id)
                manager.config["excluded_channels"] = current_list
                await manager.save_config_gw()
                await update_channel_list()
                tab.toast(type="SUCCESS", title="Channel Removed", description="Channel unblocked.")

        ui["excluded_channels_list"] = settings_card.create_ui_element(
            UI.Select, 
            label="Excluded Channels (Click to remove)",
            full_width=True,
            mode="single",
            items=[{"id": "none", "title": "Loading...", "iconUrl": "https://cdn.discordapp.com/embed/avatars/0.png"}],
            onChange=remove_excluded_channel
        )

        bot.loop.create_task(update_channel_list())
        
        async def on_save_gw():
            manager = manager_ref()
            if not manager:
                tab.toast(type="ERROR", title="Script not ready", description="The script is starting, please wait a moment.")
                return
            try:
                blacklist_text = ui["blacklist_input"].value.strip()
                manager.config["blacklist_keywords"] = [kw.strip() for kw in blacklist_text.split(",") if kw.strip()]
                
                min_delay = float(ui["min_delay_input"].value) if ui["min_delay_input"].value.replace(".", "").isdigit() else 2
                max_delay = float(ui["max_delay_input"].value) if ui["max_delay_input"].value.replace(".", "").isdigit() else 8
                manager.config["join_delay_min"] = max(0.5, min_delay)
                manager.config["join_delay_max"] = max(manager.config["join_delay_min"], max_delay)
                
                manager.config["webhook_url"] = ui["webhook_input"].value.strip()
                manager.config["debug_mode"] = ui["debug_toggle"].checked
                manager.config["ticket_wait_timeout"] = int(ui["timeout_input_gw"].value) if ui["timeout_input_gw"].value.isdigit() else 3600
                manager.config["auto_claim_message"] = ui["auto_claim_message_input"].value
                manager.config["flaresolverr_url"] = ui["flaresolverr_url_input"].value.strip()

                await manager.save_config_gw()
                tab.toast(type="SUCCESS", title="Configuration Saved", description="All settings have been updated")
            except Exception as e:
                tab.toast(type="ERROR", title="Save Error", description=f"Error saving config: {str(e)}")
        
        settings_card.create_ui_element(UI.Button, label="Save Configuration", color="primary", full_width=True, margin="mt-6", onClick=on_save_gw)
        
        return tab, ui

    # --- SCRIPT INITIALIZATION ---
    async def main_initializer_gw(ui_elements, manager):
        if not hasattr(bot, '_gw_joiner_lock'):
            bot._gw_joiner_lock = asyncio.Lock()
            
        async with bot._gw_joiner_lock:
            try:
                if hasattr(bot, '_giveaway_joiner_manager_old') and bot._giveaway_joiner_manager_old:
                    await bot._giveaway_joiner_manager_old.shutdown_gw()
            
                if hasattr(bot, '_gw_joiner_on_message_listener_old'):
                    try:
                        bot.remove_listener(bot._gw_joiner_on_message_listener_old, "on_message")
                    except ValueError:
                        pass 

                bot._giveaway_joiner_manager = manager
                await manager.async_init_gw()

            except Exception as e:
                init_error_msg = f"Giveaway Joiner initialization FAILED: {str(e)}"
                print(init_error_msg, type_="ERROR")
                traceback.print_exc()

    try:
        if hasattr(bot, '_giveaway_joiner_manager'):
            bot._giveaway_joiner_manager_old = bot._giveaway_joiner_manager
        
        if hasattr(bot, '_gw_joiner_on_message_listener'):
            bot._gw_joiner_on_message_listener_old = bot._gw_joiner_on_message_listener
        
        manager_ref = lambda: getattr(bot, '_giveaway_joiner_manager', None)
        tab, ui_elements = create_giveaway_ui(manager_ref)
        manager = GiveawayJoinerManager(ui_elements, bot)
        
        @bot.listen("on_message")
        async def main_bot_message_listener(message):
            m = getattr(bot, '_giveaway_joiner_manager', None)
            if m and m.config.get("enabled", False) and m.bot:
                bot.loop.create_task(m.process_message(message, m.bot))
        
        bot._gw_joiner_on_message_listener = main_bot_message_listener
        
        tab.render()

        bot.loop.create_task(main_initializer_gw(ui_elements, manager))

    except Exception as e:
        init_error_msg = f"Giveaway Joiner (Toplevel) initialization FAILED: {str(e)}"
        print(init_error_msg, type_="ERROR")
        traceback.print_exc()
        
    @bot.command(name="gw", description="Manage False Positive patterns (Add, Remove, Undo, List).")
    async def gw_command(ctx, *, args: str = None):
        try: await ctx.message.delete()
        except: pass
        
        manager = getattr(bot, '_giveaway_joiner_manager', None)
        if not manager:
            await ctx.send("Manager not initialized.", delete_after=10)
            return

        if args is None:
            await ctx.send("Use: `gw add <msg_id>`, `gw remove <bot_id>`, `gw list` or `gw undo`", delete_after=10)
            return

        parts = args.split()
        action = parts[0].lower()
        
        if action == "undo":
            patterns = manager.load_fp_patterns()
            if not patterns:
                await ctx.send("There are no patterns to undo.", delete_after=5)
                return
            
            removed = patterns.pop()
            manager.save_fp_patterns(patterns)
            
            desc = removed.get("title") or removed.get("content_match") or removed.get("description_match") or "No Data"
            await ctx.send(f"↩️ **Undone:** Pattern for Bot `{removed.get('bot_id')}` deleted.\n📄 *Ref: {desc[:50]}...*", delete_after=10)
            return

        elif action == "list":
            patterns = manager.load_fp_patterns()
            if not patterns:
                await ctx.send("⚠️ No False Positive patterns found.", delete_after=10)
                return

            bot_stats = {}
            for p in patterns:
                bid = str(p.get("bot_id", "Unknown"))
                if bid not in bot_stats:
                    bot_stats[bid] = 0
                bot_stats[bid] += 1

            msg_lines = ["**📋 False Positive Patterns List**\n"]
            
            cache_updated = False

            for bot_id, count in bot_stats.items():
                bot_name = f"Bot ID: {bot_id}"
                
                if bot_id in manager.bot_cache:
                    bot_name = manager.bot_cache[bot_id].get("name", bot_name)
                
                if bot_name.startswith("Bot ID:") and bot_id.isdigit():
                    try:
                        user_obj = bot.get_user(int(bot_id))
                        
                        if not user_obj:
                            try:
                                user_obj = await bot.fetch_user(int(bot_id))
                            except discord.NotFound:
                                pass
                        
                        if user_obj:
                            bot_name = user_obj.name
                            manager.bot_cache[bot_id] = {
                                "name": user_obj.name, 
                                "avatar_url": user_obj.avatar.url if user_obj.avatar else ""
                            }
                            cache_updated = True
                    except Exception as e:
                        pass
                
                msg_lines.append(f"• **{bot_name}** ({bot_id}): {count} patterns")

            msg_lines.append(f"\n*Total Patterns: {len(patterns)}*")
            
            if cache_updated:
                await manager.save_bot_cache()

            full_msg = "\n".join(msg_lines)
            if len(full_msg) > 1900:
                full_msg = full_msg[:1900] + "\n...(list truncated)"
            
            await ctx.send(full_msg, delete_after=60)
            return

        elif action == "remove":
            if len(parts) < 2:
                await ctx.send("❌ Usage: `[p]gw remove <bot_id>`", delete_after=5); return
            
            target_bot_id = parts[1].strip()
            patterns = manager.load_fp_patterns()
            
            candidates = []
            for i, p in enumerate(patterns):
                if str(p.get("bot_id")) == target_bot_id:
                    candidates.append((i, p))
            
            if not candidates:
                await ctx.send(f"⚠️ No found patterns for Bot ID `{target_bot_id}`.", delete_after=10)
                return
            
            if len(candidates) == 1:
                index_to_delete = candidates[0][0]
                removed_p = patterns.pop(index_to_delete)
                manager.save_fp_patterns(patterns)
                await ctx.send(f"🗑️ Pattern deleted for Bot `{target_bot_id}`.", delete_after=10)
                return
            
            else:
                msg_lines = [f"**Found {len(candidates)} patterns for `{target_bot_id}`.**", "Write the number to delete (or 'cancel'):\n"]
                
                for idx, (orig_idx, p) in enumerate(candidates):
                    summary = []
                    if p.get("title"): summary.append(f"Title: {p['title']}")
                    if p.get("content_match"): summary.append(f"Content: {p['content_match'][:20]}..")
                    if p.get("footer_text"): summary.append(f"Footer: {p['footer_text']}")
                    if p.get("buttons_list"): summary.append(f"Buttons: {p['buttons_list']}")
                    
                    details = " | ".join(summary) if summary else "(No text data)"
                    msg_lines.append(f"**{idx + 1}.** {details}")
                
                prompt_msg = await ctx.send("\n".join(msg_lines), delete_after=60)
                
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                
                try:
                    reply = await bot.wait_for('message', check=check, timeout=30.0)
                    content = reply.content.lower().strip()
                    try: await reply.delete(); 
                    except: pass
                    
                    if content == 'cancel':
                        await ctx.send("Operation cancelled.", delete_after=5)
                        return
                    
                    if not content.isdigit():
                        await ctx.send("❌ That's not a number.", delete_after=5)
                        return
                    
                    choice = int(content)
                    if 1 <= choice <= len(candidates):
                        index_to_delete = candidates[choice - 1][0]
                        
                        patterns = manager.load_fp_patterns()
                        
                        if index_to_delete < len(patterns):
                            removed_p = patterns.pop(index_to_delete)
                            manager.save_fp_patterns(patterns)
                            await ctx.send(f"✅ Pattern #{choice} deleted successfully.", delete_after=10)
                        else:
                            await ctx.send("❌ Synchronization error. Try again.", delete_after=5)
                    else:
                        await ctx.send("❌ Invalid number.", delete_after=5)

                except asyncio.TimeoutError:
                    await ctx.send("⌛ Timeout.", delete_after=5)
                finally:
                    try: await prompt_msg.delete()
                    except: pass
            return

        elif action == "add" and len(parts) == 2:
            message_id_str = parts[1]

            if message_id_str not in manager.history:
                await ctx.send(f"❌ ID `{message_id_str}` not found in history.", delete_after=15)
                return
                
            history_entry = manager.history[message_id_str]
            embed_data = history_entry.get("embed_data") or {}

            p_title = (embed_data.get("title") or "").lower().strip()
            p_author = (embed_data.get("author", {}).get("name") or "").lower().strip()
            p_footer = (embed_data.get("footer", {}).get("text") or "").lower().strip()
            
            raw_content = history_entry.get("message_content", "").lower().strip()
            p_content = raw_content[:80] if raw_content else ""

            raw_desc = (embed_data.get("description") or "").lower().strip()
            p_description = raw_desc[:80] if raw_desc else ""

            raw_buttons = history_entry.get("button_labels", [])
            p_buttons_list = [btn.lower().strip() for btn in raw_buttons if btn]

            p_field_names = []
            if "fields" in embed_data:
                for f in embed_data["fields"]:
                    fname = (f.get("name") or "").lower().strip()
                    if fname: p_field_names.append(fname)

            p_bot_id = history_entry.get("bot_id", "")

            if not any([p_title, p_author, p_footer, p_content, p_description, p_buttons_list, p_field_names]):
                await ctx.send(f"❌ The message does not have enough data.", delete_after=10)
                return

            new_pattern = {
                "bot_id": p_bot_id,
                "title": p_title, 
                "author_name": p_author, 
                "footer_text": p_footer,
                "content_match": p_content,
                "description_match": p_description,
                "buttons_list": p_buttons_list,
                "field_names": p_field_names
            }
            
            patterns = manager.load_fp_patterns()
            if new_pattern in patterns:
                await ctx.send(f"This pattern already exists.", delete_after=10); return
            
            patterns.append(new_pattern)
            manager.save_fp_patterns(patterns)
            
            msg = f"FP Saved for Bot `{p_bot_id}`."
            if p_title: msg += f"\nTitle: `{p_title}`"
            if p_author: msg += f"\nAuthor: `{p_author}`"
            if p_footer: msg += f"\nFooter: `{p_footer}`"
            if p_content: msg += f"\nContent: `{p_content}`"
            if p_description: msg += f"\nDescription: `{p_description}`"
            if p_buttons_list: msg += f"\nButtons: `{', '.join(p_buttons_list)}`"
            if p_field_names: msg += f"\nFields: `{', '.join(p_field_names)}`"
            
            await ctx.send(msg, delete_after=20)
        else:
            await ctx.send("Invalid command. Use `gw add <id>`, `gw remove <bot_id>`, `gw list` or `gw undo`", delete_after=15)

giveaway_Joiner()