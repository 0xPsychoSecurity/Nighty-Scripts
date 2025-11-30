@nightyScript(
    name="Timed Message Repeater",
    author="Syn",
    description="Sends custom messages at specified time intervals",
    usage=".timedrepeat <time> <message>"
)
def timed_repeat_message():
    import json
    import time
    import asyncio
    import re
    from pathlib import Path
    
    BASE_DIR = Path(getScriptsPath()) / "json"
    CONFIG_FILE = BASE_DIR / "timedrepeat_config.json"
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    loop_status = {"running": False, "task": None}
    
    def get_config():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return {
                "enabled": False,
                "channel_id": "",
                "interval_seconds": 1800,  # 30 minutes default
                "message": "",
                "next_send": 0
            }
    
    def save_config(config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    
    def parse_time_string(time_str):
        """Parse time strings like '30m', '2h', '1h30m', '45s' into seconds"""
        pattern = r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        match = re.fullmatch(pattern, time_str.lower())
        
        if not match:
            return None
        
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0
        
        total_seconds = (hours * 3600) + (minutes * 60) + seconds
        
        return total_seconds if total_seconds > 0 else None
    
    def format_time(timestamp):
        """Format timestamp for display"""
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
    
    async def start_repeat_loop():
        if loop_status["running"]:
            if loop_status["task"] and not loop_status["task"].done():
                loop_status["task"].cancel()
            loop_status["running"] = False
        
        loop_status["running"] = True
        loop_status["task"] = asyncio.create_task(run_repeat_loop())
    
    async def run_repeat_loop():
        try:
            while loop_status["running"]:
                config = get_config()
                
                if not config["enabled"]:
                    loop_status["running"] = False
                    break
                
                if not config["channel_id"] or not config["message"]:
                    await asyncio.sleep(30)
                    continue
                
                current_time = time.time()
                
                if config["next_send"] == 0:
                    config["next_send"] = current_time + config["interval_seconds"]
                    save_config(config)
                    await asyncio.sleep(30)
                    continue
                
                time_left = config["next_send"] - current_time
                
                if time_left <= 0:
                    try:
                        channel = await bot.fetch_channel(int(config["channel_id"]))
                        await channel.send(config["message"])
                        
                        config["next_send"] = current_time + config["interval_seconds"]
                        save_config(config)
                        
                    except Exception as e:
                        # If sending fails, try again in 5 minutes
                        config["next_send"] = current_time + 300
                        save_config(config)
                
                await asyncio.sleep(30)
        except Exception as e:
            pass
        finally:
            loop_status["running"] = False
    
    @bot.command()
    async def timedrepeat(ctx, time_str=None, channel_id=None, *, message=None):
        """Set up timed message repetition"""
        await ctx.message.delete()
        
        # Handle management commands first
        if time_str and time_str.lower() in ["stop", "status", "start"]:
            if time_str.lower() == "stop":
                if loop_status["task"] and not loop_status["task"].done():
                    loop_status["task"].cancel()
                loop_status["running"] = False
                
                config = get_config()
                config["enabled"] = False
                save_config(config)
                
                stop_msg = await ctx.send("⚠️ Timed repeater stopped")
                await asyncio.sleep(5)
                await stop_msg.delete()
                return
            
            if time_str.lower() == "status":
                config = get_config()
                status_text = "✅ Active" if config["enabled"] else "❌ Inactive"
                next_time = format_time(config["next_send"])
                
                # Get channel info
                channel_info = "Not set"
                if config["channel_id"]:
                    try:
                        channel = await bot.fetch_channel(int(config["channel_id"]))
                        channel_info = f"{channel.mention} ({config['channel_id']})"
                    except:
                        channel_info = config["channel_id"]
                
                # Format interval
                interval_seconds = config["interval_seconds"]
                hours = interval_seconds // 3600
                minutes = (interval_seconds % 3600) // 60
                if hours > 0:
                    interval_str = f"{hours}h {minutes}m"
                elif minutes > 0:
                    interval_str = f"{minutes}m"
                else:
                    interval_str = f"{interval_seconds}s"
                
                status_msg = await ctx.send(f"""```
📊 Timed Repeater Status:
========================
Status: {status_text}
Channel: {channel_info}
Interval: {interval_str}
Next send: {next_time}
Message: {config['message'] or 'Not set'}
========================
```""")
                await asyncio.sleep(10)
                await status_msg.delete()
                return
            
            if time_str.lower() == "start":
                config = get_config()
                config["enabled"] = True
                save_config(config)
                
                if not loop_status["running"]:
                    bot.loop.create_task(start_repeat_loop())
                
                start_msg = await ctx.send("✅ Timed repeater started")
                await asyncio.sleep(5)
                await start_msg.delete()
                return
        
        if not time_str or not message:
            help_msg = await ctx.send("""```
🔧 Timed Message Repeater Commands:
==================================

📝 Usage:
   .timedrepeat <time> [channel_id] <message>

📝 Time Formats:
   30m    = 30 minutes
   2h     = 2 hours
   1h30m  = 1 hour 30 minutes
   45s    = 45 seconds

📝 Examples:
   .timedrepeat 30m Hello everyone!
   .timedrepeat 2h 123456789012345678 Don't forget to check announcements!
   .timedrepeat 1h30m Weekly reminder here!

📝 Channel ID:
   • Optional - if not specified, uses current channel
   • Specify to send messages to a different channel

📝 Management Commands:
   .timedrepeat stop    - Stop the repeater
   .timedrepeat status  - Show current status
   .timedrepeat start   - Start the repeater
==================================
```""")
            await asyncio.sleep(10)
            await help_msg.delete()
            return
        
        # Handle channel ID - check if second argument is channel ID or part of message
        target_channel_id = None
        target_message = None
        
        if channel_id:
            # Check if channel_id is actually a channel ID (numeric)
            try:
                int(channel_id)
                target_channel_id = channel_id
                target_message = message
            except ValueError:
                # channel_id is not numeric, so it's part of the message
                target_channel_id = str(ctx.channel.id)
                target_message = f"{channel_id} {message}" if message else channel_id
        else:
            # No channel ID specified, use current channel
            target_channel_id = str(ctx.channel.id)
            target_message = message
        
        interval_seconds = parse_time_string(time_str)
        
        if interval_seconds is None:
            error_msg = await ctx.send("⚠️ Invalid time format")
            await asyncio.sleep(5)
            await error_msg.delete()
            return
        
        # Update config
        config = get_config()
        config["enabled"] = True
        config["channel_id"] = target_channel_id
        config["interval_seconds"] = interval_seconds
        config["message"] = target_message
        config["next_send"] = time.time() + interval_seconds
        save_config(config)
        
        # Start the loop if not running
        if not loop_status["running"]:
            bot.loop.create_task(start_repeat_loop())
        
        # Format interval for display
        hours = interval_seconds // 3600
        minutes = (interval_seconds % 3600) // 60
        
        if hours > 0:
            interval_str = f"{hours}h {minutes}m"
        elif minutes > 0:
            interval_str = f"{minutes}m"
        else:
            interval_str = f"{interval_seconds}s"
        
        channel_info = f" in channel {target_channel_id}" if target_channel_id != str(ctx.channel.id) else " in this channel"
        confirm_msg = await ctx.send(f"✅ Will repeat message every {interval_str}{channel_info}")
        await asyncio.sleep(5)
        await confirm_msg.delete()
    
    @bot.listen('on_ready')
    async def auto_start_repeat_loop():
        config = get_config()
        
        if config["enabled"] and config["channel_id"] and config["message"]:
            bot.loop.create_task(start_repeat_loop())

timed_repeat_message()