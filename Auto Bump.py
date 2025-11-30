@nightyScript(
    name="Auto Bump",
    author="jealousy",
    description="Auto bumps server with Disboard",
    usage="UI tab!"
)
def auto_bump():
    import json
    import time
    import asyncio
    import random
    from pathlib import Path
    
    BASE_DIR = Path(getScriptsPath()) / "json"
    CONFIG_FILE = BASE_DIR / "bumper_config.json"
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    DISBOARD_ID = 302050872383242240
    
    loop_status = {"running": False, "task": None}
    
    def migrate_config():
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    old_config = json.load(f)
                

                if "random_minutes" in old_config and "randomize" not in old_config:

                    new_config = {
                        "enabled": old_config.get("enabled", False),
                        "channel_id": old_config.get("channel_id", ""),
                        "hours": old_config.get("hours", 2),
                        "minutes": old_config.get("minutes", 0),
                        "randomize": old_config.get("random_minutes", 5) > 0,
                        "next_bump": old_config.get("next_bump", 0)
                    }
                    
                    with open(CONFIG_FILE, "w") as f:
                        json.dump(new_config, f, indent=4)
                    
                    return new_config
            except:
                pass

        default_config = {
            "enabled": False,
            "channel_id": "",
            "hours": 2,
            "minutes": 0,
            "randomize": True,
            "next_bump": 0
        }
        
        if not CONFIG_FILE.exists():
            with open(CONFIG_FILE, "w") as f:
                json.dump(default_config, f, indent=4)
        
        return default_config
    
    migrate_config()
    
    def get_config():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                
                if "randomize" not in config:
                    config["randomize"] = True
                
                return config
        except:
            return {
                "enabled": False, 
                "channel_id": "",
                "hours": 2,
                "minutes": 0,
                "randomize": True,
                "next_bump": 0
            }
    
    def save_config(config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    
    tab = Tab(name="Auto Bump", title="Disboard", icon="calc")
    container = tab.create_container(type="rows", gap=2)
    card = container.create_card(gap=3)
    
    status_group = card.create_group(type="rows", gap=1)
    next_bump_text = status_group.create_ui_element(
        UI.Text,
        content="",
        size="sm",
        color="#a1a1aa"
    )
    status_text = status_group.create_ui_element(
        UI.Text,
        content="❌ Inactive",
        size="lg",
        color="#f87171"
    )
    
    settings_group = card.create_group(type="rows", gap=2)
    
    async def start_bump_loop():
        if loop_status["running"]:
            if loop_status["task"] and not loop_status["task"].done():
                loop_status["task"].cancel()
            loop_status["running"] = False
            
        loop_status["running"] = True
        loop_status["task"] = asyncio.create_task(run_bump_loop())
    
    async def run_bump_loop():
        try:
            while loop_status["running"]:
                config = get_config()
                
                if not config["enabled"]:
                    loop_status["running"] = False
                    break
                
                if not config["channel_id"]:
                    await asyncio.sleep(30)
                    continue
                
                current_time = time.time()
                
                if config["next_bump"] == 0:
                    base_delay = (config["hours"] * 3600) + (config["minutes"] * 60)
                    random_delay = random.randint(2 * 60, 5 * 60) if config.get("randomize", True) else 0
                    config["next_bump"] = current_time + base_delay + random_delay
                    save_config(config)
                    update_display()
                    await asyncio.sleep(30)
                    continue
                
                time_left = config["next_bump"] - current_time
                
                if time_left <= 0:
                    try:
                        channel = await bot.fetch_channel(int(config["channel_id"]))
                        slash_cmd = await fetchSlashCommand(channel, DISBOARD_ID, "bump")
                        await execSlashCommand(channel, slash_cmd)
                        
                        base_delay = (config["hours"] * 3600) + (config["minutes"] * 60)
                        random_delay = random.randint(2 * 60, 5 * 60) if config.get("randomize", True) else 0
                        config["next_bump"] = current_time + base_delay + random_delay
                        
                        save_config(config)
                        update_display()
                        tab.toast(type="SUCCESS", title="Success", description="Auto-bumped!")
                    except Exception as e:
                        base_delay = (config["hours"] * 3600) + (config["minutes"] * 60)
                        config["next_bump"] = current_time + base_delay
                        save_config(config)
                
                await asyncio.sleep(30)
        except Exception as e:
            pass
        finally:
            loop_status["running"] = False
    
    def toggle_enabled(checked):
        config = get_config()
        config["enabled"] = checked
        
        if checked and not config["channel_id"]:
            status_text.content = "⚠️ Set channel ID first"
            status_text.color = "#facc15"
            save_config(config)
            update_display()
            return
        
        if checked and config["next_bump"] == 0:
            base_delay = (config["hours"] * 3600) + (config["minutes"] * 60)
            random_delay = random.randint(2 * 60, 5 * 60) if config.get("randomize", True) else 0
            config["next_bump"] = time.time() + base_delay + random_delay
        
        save_config(config)
        update_display()
        
        if checked:
            bot.loop.create_task(start_bump_loop())
        else:
            if loop_status["task"] and not loop_status["task"].done():
                loop_status["task"].cancel()
            loop_status["running"] = False
    
    enabled_toggle = settings_group.create_ui_element(
        UI.Toggle,
        label="Enable",
        onChange=toggle_enabled
    )
    
    def update_channel(value):
        if not value:
            channel_input.invalid = True
            channel_input.error_message = "Required"
            return
        
        try:
            int(value)
            channel_input.invalid = False
            channel_input.error_message = None
            
            config = get_config()
            config["channel_id"] = value
            save_config(config)
            update_display()
        except:
            channel_input.invalid = True
            channel_input.error_message = "Numbers only"
    
    channel_input = settings_group.create_ui_element(
        UI.Input,
        label="Channel ID",
        placeholder="Where to bump",
        onInput=update_channel,
        full_width=True
    )
    
    timing_group = settings_group.create_group(type="columns", gap=2)
    
    def update_hours(value):
        if not value:
            hours_input.invalid = True
            hours_input.error_message = "Required"
            return
            
        try:
            h = float(value)
            if h < 2:
                hours_input.invalid = True
                hours_input.error_message = "Min 2"
                return
                
            hours_input.invalid = False
            hours_input.error_message = None
            
            config = get_config()
            config["hours"] = h
            save_config(config)
        except:
            hours_input.invalid = True
            hours_input.error_message = "Numbers"
    
    hours_input = timing_group.create_ui_element(
        UI.Input,
        label="Hours",
        placeholder="2",
        onInput=update_hours
    )
    
    def update_minutes(value):
        if not value and value != "0":
            minutes_input.invalid = False
            config = get_config()
            config["minutes"] = 0
            save_config(config)
            return
            
        try:
            m = int(value)
            if m < 0 or m > 59:
                minutes_input.invalid = True
                minutes_input.error_message = "0-59"
                return
                
            minutes_input.invalid = False
            minutes_input.error_message = None
            
            config = get_config()
            config["minutes"] = m
            save_config(config)
        except:
            minutes_input.invalid = True
            minutes_input.error_message = "Numbers"
    
    minutes_input = timing_group.create_ui_element(
        UI.Input,
        label="Minutes",
        placeholder="0",
        onInput=update_minutes
    )
    
    def toggle_randomize(checked):
        config = get_config()
        config["randomize"] = checked
        save_config(config)
    
    randomize_toggle = timing_group.create_ui_element(
        UI.Toggle,
        label="Add 2-5 random mins",
        onChange=toggle_randomize
    )
    
    buttons_group = card.create_group(type="columns", gap=2)
    
    async def on_bump_now():
        config = get_config()
        if not config["channel_id"]:
            tab.toast(type="ERROR", title="Error", description="Set channel ID first")
            return
        
        config["enabled"] = True
        save_config(config)
        update_display()
            
        try:
            channel = await bot.fetch_channel(int(config["channel_id"]))
            slash_cmd = await fetchSlashCommand(channel, DISBOARD_ID, "bump")
            await execSlashCommand(channel, slash_cmd)
            
            base_delay = (config["hours"] * 3600) + (config["minutes"] * 60)
            random_delay = random.randint(2 * 60, 5 * 60) if config.get("randomize", True) else 0
            config["next_bump"] = time.time() + base_delay + random_delay
            save_config(config)
            
            update_display()
            
            if not loop_status["running"]:
                bot.loop.create_task(start_bump_loop())
                
            tab.toast(type="SUCCESS", title="Success", description="Bumped!")
        except Exception as e:
            tab.toast(type="ERROR", title="Error", description="Failed to bump")
    
    bump_now_button = buttons_group.create_ui_element(
        UI.Button,
        label="Bump Now",
        variant="solid",
        onClick=on_bump_now
    )
    
    async def on_stop():
        if loop_status["task"] and not loop_status["task"].done():
            loop_status["task"].cancel()
        
        loop_status["running"] = False
        
        config = get_config()
        config["enabled"] = False
        save_config(config)
        
        update_display()
        
        tab.toast(type="INFO", title="Stopped", description="Bumper stopped")
    
    stop_button = buttons_group.create_ui_element(
        UI.Button,
        label="Stop",
        variant="light",
        onClick=on_stop
    )
    
    def format_time(timestamp):
        if timestamp == 0:
            return "Never"
        
        seconds = int(timestamp - time.time())
        
        if seconds <= 0:
            return "Now"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"in {hours}h {minutes}m"
        else:
            return f"in {minutes}m"
    
    def update_display():
        config = get_config()
        
        enabled_toggle.checked = config["enabled"]
        channel_input.value = config["channel_id"]
        hours_input.value = str(config["hours"])
        minutes_input.value = str(config["minutes"]) if config["minutes"] > 0 else ""
        randomize_toggle.checked = config.get("randomize", True)
        
        next_time = format_time(config["next_bump"])
        next_bump_text.content = f"Next bump: {next_time}"
        
        if not config["enabled"]:
            status_text.content = "❌ Inactive"
            status_text.color = "#f87171"
        elif not config["channel_id"]:
            status_text.content = "⚠️ Need channel ID"
            status_text.color = "#facc15"
        else:
            status_text.content = "✅ Active"
            status_text.color = "#4ade80"
    
    @bot.command(name="bump")
    async def bump_cmd(ctx, cmd: str=""):
        await ctx.message.delete()
        cmd = cmd.lower() if cmd else ""
        
        if cmd == "now":
            config = get_config()
            if not config["channel_id"]:
                msg = await ctx.send("❌ Set channel ID first")
                await asyncio.sleep(5)
                await msg.delete()
                return
            
            config["enabled"] = True
            save_config(config)
            update_display()
                
            status_msg = await ctx.send("Bumping...")
            
            try:
                channel = await bot.fetch_channel(int(config["channel_id"]))
                slash_cmd = await fetchSlashCommand(channel, DISBOARD_ID, "bump")
                await execSlashCommand(channel, slash_cmd)
                
                base_delay = (config["hours"] * 3600) + (config["minutes"] * 60)
                random_delay = random.randint(2 * 60, 5 * 60) if config.get("randomize", True) else 0
                config["next_bump"] = time.time() + base_delay + random_delay
                save_config(config)
                
                if not loop_status["running"]:
                    bot.loop.create_task(start_bump_loop())
                
                update_display()
                await status_msg.edit(content="✅ Bumped!")
                await asyncio.sleep(5)
                await status_msg.delete()
            except Exception as e:
                await status_msg.edit(content="❌ Failed")
                await asyncio.sleep(5)
                await status_msg.delete()
        elif cmd == "stop":
            if loop_status["task"] and not loop_status["task"].done():
                loop_status["task"].cancel()
            
            loop_status["running"] = False
            
            config = get_config()
            config["enabled"] = False
            save_config(config)
            
            update_display()
            
            msg = await ctx.send("⚠️ Bumper stopped")
            await asyncio.sleep(5)
            await msg.delete()
        elif cmd == "start":
            config = get_config()
            config["enabled"] = True
            save_config(config)
            
            if loop_status["task"] and not loop_status["task"].done():
                loop_status["task"].cancel()
                
            loop_status["running"] = False
            bot.loop.create_task(start_bump_loop())
            
            update_display()
            
            msg = await ctx.send("✅ Bumper started")
            await asyncio.sleep(5)
            await msg.delete()
        else:
            msg = await ctx.send("Commands: .bump now, .bump start, .bump stop")
            await asyncio.sleep(5)
            await msg.delete()
    
    @bot.listen('on_ready')
    async def auto_start_bump_loop():
        config = get_config()
        
        if config["enabled"] and config["channel_id"]:
            bot.loop.create_task(start_bump_loop())
    
    async def refresh_display():
        while True:
            update_display()
            await asyncio.sleep(30)
    
    bot.loop.create_task(refresh_display())
    update_display()
    tab.render()

auto_bump()