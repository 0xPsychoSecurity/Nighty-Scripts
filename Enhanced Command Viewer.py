#Sorry nes for the 3k line script but cheers if this gets approved
#IMPORTANT: Dm me at boredom420 to get import of all the current nighty script commands or let it run passively to collect commands for you
#Script isnt fully tested and unable to do so extensively so please DM me for any bugs or issues!
#The ratelimit feature isnt tested you should leave this off. But it does (shoould) allow protection against a accidental rogue script from spamming channels it does this by restarting your bot.
@nightyScript(
    name="Enhanced Command Viewer",
    author="Original: Boredom, Enhanced: Claude",
    description="Advanced command management with aliases, templates, statistics, sharing, and rate limiting.",
    usage="""<p>help - Show all available commands with descriptions
<p>help <feature> - Get help on a specific feature (e.g., alias, group, template)
<p>tutorial - Show a beginner's guide to using this script
<p>helpcommands - List all saved commands
<p>savecommand <cmd1>, <cmd2>, ... - Save commands manually
<p>delcommand <cmd> - Delete a saved command
<p>clearcommands - Clear all saved commands
<p>movecommand <cmd> <category> - Move a command to a different category
<p>setprefix <char> - Change the prefix the script detects
<p>adddesc <cmd> <description> - Add description to a command
<p>search <term> - Search for commands
<p>validate - Review and validate pending commands
<p>alias add <alias> <command> - Add a command alias
<p>alias remove <alias> - Remove a command alias
<p>alias list - List all aliases
<p>stats [cmd] - View usage statistics (optional: for specific command)
<p>export [category] - Export commands (optional: specific category)
<p>import <code> - Import commands from export code
<p>group create <name> <cmd1> <cmd2> ... - Create a command group
<p>group add <name> <cmd> - Add command to group
<p>group remove <name> <cmd> - Remove command from group
<p>group run <name> - Run all commands in a group
<p>group list - List all command groups
<p>template create <name> <template> - Create a command template
<p>template use <name> <params> - Use a template
<p>template list - List all templates
<p>suggest - Get command suggestions based on usage
<p>docs [format] - Generate command documentation
<p>favorite <command> - Add a command to favorites
<p>unfavorite <command> - Remove a command from favorites
<p>ratelimit - Configure rate limit protection
<p>ratelimit on/off - Enable or disable rate protection
<p>ratelimit threshold <type> <value> - Set rate limit threshold
<p>ratelimit pattern add <regex> - Add error pattern for detection
<p>ratelimit servers <num> - Set multi-server threshold
<p>ratelogs - View rate limit event logs
<p>emergency - Activate emergency cleanup and restart"""
)
def command_viewer():
    """
    ENHANCED COMMAND VIEWER
    ----------------------
    
    Save and view your commands organized by script with descriptions.
    Automatically saves VALID commands when you use them with your prefix.
    Includes advanced features like aliases, templates, statistics, sharing, and rate limiting.
    
    CORE COMMANDS:
    <p>helpcommands - List all saved commands
    <p>savecommand <cmd1>, <cmd2>, ... - Save commands manually
    <p>delcommand <cmd> - Delete a saved command
    <p>clearcommands - Clear all saved commands
    <p>movecommand <cmd> <category> - Move a command to a different category
    <p>setprefix <char> - Change the prefix the script detects (default: .)
    <p>adddesc <cmd> <description> - Add description to a command
    <p>search <term> - Search commands and descriptions
    <p>validate - Review pending commands waiting for validation
    
    ALIAS COMMANDS:
    <p>alias add <alias> <command> - Create a shortcut for a command
    <p>alias remove <alias> - Delete an alias
    <p>alias list - View all aliases
    
    FAVORITES COMMANDS:
    <p>favorite <command> - Add a command to favorites
    <p>unfavorite <command> - Remove a command from favorites
    
    STATISTICS COMMANDS:
    <p>stats [cmd] - View usage statistics and visualization
    
    IMPORT/EXPORT COMMANDS:
    <p>export [category] - Export commands as a shareable code
    <p>import <code> - Import commands from an export code
    
    GROUP COMMANDS:
    <p>group create <name> <cmd1> <cmd2> ... - Create a command group
    <p>group add <name> <cmd> - Add command to an existing group
    <p>group remove <name> <cmd> - Remove command from a group
    <p>group run <name> - Execute all commands in a group
    <p>group list - List all command groups
    
    TEMPLATE COMMANDS:
    <p>template create <name> <template> - Create a command template
    <p>template use <name> <params> - Use a template with parameters
    <p>template list - List all templates
    
    RATE LIMIT PROTECTION:
    <p>ratelimit - View and configure rate limit protection
    <p>ratelimit on/off - Enable or disable protection
    <p>ratelimit threshold <type> <value> - Set rate thresholds
    <p>ratelimit pattern add <regex> - Add error detection pattern
    <p>ratelimit servers <num> - Configure multi-server detection
    <p>ratelogs - View rate limit event logs
    <p>emergency - Trigger immediate message cleanup and restart
    
    ADVANCED COMMANDS:
    <p>suggest - Get command suggestions based on usage patterns
    <p>docs [format] - Generate formatted command documentation
    
    NOTES:
    - <p> in this documentation represents your actual prefix (default: .)
    - Only valid commands are automatically saved
    - Commands go through a validation process to filter out typos
    - Messages automatically clean up after a short delay
    - Commands are organized into meaningful categories
    - Rate limit protection prevents accidental Discord API bans
    - Error detection identifies problematic scripts and restarts automatically
    """
    import json
    import re
    from pathlib import Path
    import time
    import asyncio
    import datetime
    import base64
    import zlib
    import random
    import string
    from collections import Counter
    import os
    import sys
    import logging
    import functools
    
    # Setup storage
    BASE_DIR = Path(getScriptsPath()) / "json"
    COMMANDS_FILE = BASE_DIR / "saved_commands.json"
    DESCRIPTIONS_FILE = BASE_DIR / "command_descriptions.json"
    STATS_FILE = BASE_DIR / "command_stats.json"
    PENDING_FILE = BASE_DIR / "pending_commands.json"  # For commands waiting validation
    ALIASES_FILE = BASE_DIR / "command_aliases.json"  # For command aliases
    GROUPS_FILE = BASE_DIR / "command_groups.json"  # For command groups
    TEMPLATES_FILE = BASE_DIR / "command_templates.json"  # For command templates
    
    # === RATE LIMIT PROTECTION SYSTEM ===
    
    # Configuration keys
    PREFIX_KEY = "command_viewer_prefix"
    RATE_LIMIT_ENABLED_KEY = "rate_limit_protection_enabled"
    RATE_MONITOR_THRESHOLD_KEY = "rate_monitor_thresholds"
    RATE_LIMIT_ACTION_KEY = "rate_limit_action"
    
    # Setup logging
    LOG_DIR = Path(getScriptsPath()) / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE = LOG_DIR / "ratelimit_events.log"
    
    # Configure logger
    rate_logger = logging.getLogger("rate_limit_protection")
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    rate_logger.addHandler(handler)
    rate_logger.setLevel(logging.INFO)
    
    # Auto-delete timeouts (in seconds)
    SHORT_TIMEOUT = 5   # For simple confirmations
    LONG_TIMEOUT = 60   # For informative outputs
    
    # Rate monitoring data structure
    RATE_MONITOR = {
        "enabled": False,
        "message_count": 0,
        "command_count": 0,
        "api_calls": 0,
        "recent_messages": [],  # Store recent message data for analysis
        "server_activity": {},  # Track messages per server
        "last_reset": time.time(),
        "reset_interval": 60,  # Reset counters every 60 seconds
        "restart_triggered": False,
        "error_patterns": [     # Patterns that might indicate error messages
            r"error",
            r"exception",
            r"traceback",
            r"stack trace",
            r"failed",
            r"\w+Error:",       # NameError:, TypeError:, etc.
            r"undefined",
            r"NullPointerException"
        ],
        "message_threshold_per_server": 5,  # Max messages to a single server in short period
        "unique_servers_threshold": 3,      # Max number of different servers to message in short period
        "similar_content_threshold": 3      # Number of similar messages that trigger alert
    }
    
    # Initialize default settings if not set
    if getConfigData().get(PREFIX_KEY) is None:
        updateConfigData(PREFIX_KEY, ".")  # Default to period
    
    if getConfigData().get(RATE_LIMIT_ENABLED_KEY) is None:
        updateConfigData(RATE_LIMIT_ENABLED_KEY, False)  # Off by default
    
    if getConfigData().get(RATE_MONITOR_THRESHOLD_KEY) is None:
        # Default thresholds
        updateConfigData(RATE_MONITOR_THRESHOLD_KEY, {
            "messages_per_minute": 100,
            "commands_per_minute": 180,
            "api_calls_per_minute": 45
        })
    
    if getConfigData().get(RATE_LIMIT_ACTION_KEY) is None:
        updateConfigData(RATE_LIMIT_ACTION_KEY, "restart")  # Default to restart
    
    # Load settings into runtime variables
    RATE_MONITOR["enabled"] = getConfigData().get(RATE_LIMIT_ENABLED_KEY, False)
    
    # List of our own commands to ignore
    OWN_COMMANDS = [
        "help", "helpcommands", "savecommand", "delcommand", "clearcommands", 
        "movecommand", "setprefix", "adddesc", "search", "validate",
        "alias", "stats", "export", "import", "group", "template", 
        "suggest", "docs", "tutorial", "favorite", "unfavorite",
        "ratelimit", "ratelogs", "emergency"
    ]
    
    # Error patterns to detect invalid commands
    ERROR_PATTERNS = [
        r"(command|cmd)(\s+not\s+|\s+)found",
        r"unknown(\s+)command",
        r"invalid(\s+)command",
        r"no(\s+such\s+)command",
        r"error.*command",
        r"undefined(\s+)command",
        r"not(\s+a\s+valid\s+)command",
        r"command.*doesn't exist",
        r"invalid usage",
        r"usage:.*",
        r"error:.*"
    ]
    
    # Command pattern detection - COMPREHENSIVE LIST
    COMMAND_PATTERNS = {
        # Scheduler/Task Commands
        "Scheduler": [r"^cmd", r"^hook", r"^schedule", r"^repeat", r"^cron", r"^task", r"^job", r"^timer"],
        
        # Utility Commands
        "Utility": [r"^ping", r"^avatar", r"^user", r"^server", r"^info", r"^help", r"^about",
                   r"^stats", r"^uptime", r"^time", r"^weather", r"^calc", r"^math", r"^convert"],
        
        # Moderation Commands
        "Moderation": [r"^ban", r"^kick", r"^mute", r"^warn", r"^clear", r"^purge", r"^delete",
                      r"^timeout", r"^restrict", r"^slow", r"^lock", r"^unlock", r"^perms"],
        
        # Fun Commands
        "Fun": [r"^8ball", r"^roll", r"^flip", r"^joke", r"^meme", r"^game", r"^afk", r"^quote",
               r"^emote", r"^react", r"^play", r"^random", r"^fortune", r"^hug", r"^pet"],
        
        # Ghost/Stealth Commands
        "Ghost": [r"^ghost", r"^lurk", r"^clean", r"^invisible", r"^hide", r"^vanish", r"^stealth"],
        
        # Music Commands
        "Music": [r"^play", r"^skip", r"^queue", r"^song", r"^music", r"^volume", r"^pause",
                 r"^resume", r"^stop", r"^next", r"^previous", r"^lyrics", r"^shuffle"],
        
        # Economy Commands
        "Economy": [r"^bal", r"^economy", r"^money", r"^coin", r"^daily", r"^work", r"^shop",
                   r"^buy", r"^sell", r"^bank", r"^pay", r"^give", r"^rob", r"^gamble"],
        
        # Settings Commands
        "Settings": [r"^config", r"^setting", r"^set", r"^toggle", r"^enable", r"^disable",
                    r"^prefix", r"^lang", r"^option", r"^setup", r"^reset"],
        
        # Message Management
        "Message Management": [r"^(b)?savedmsgs", r"^(b)?clearmsgs", r"^(b)?editmsg", r"savecommands", r"^savecommand",
                             r"^quote", r"^reply", r"^forward", r"^dm", r"^say", r"^embed", r"transfer"],
        
        # Navigation Commands
        "Navigation": [r"^jumpto", r"^goto", r"^channel", r"^move", r"^join", r"^leave", r"^follow"],
        
        # Image/Media Commands
        "Media": [r"^img", r"^image", r"^gif", r"^meme", r"^video", r"^youtube", r"^yt", 
                r"^screen", r"^capture", r"^record", r"^logo", r"^banner", r"^avatar"],
        
        # Emoji Commands
        "Emoji": [r"^emoji", r"^transferemoji", r"^addemoji", r"^delemoji", r"^steal", r"^react"],
        
        # Information Commands
        "Information": [r"^server", r"^user", r"^channel", r"^role", r"^whois", r"^who", r"^lookup",
                      r"^profile", r"^check", r"^search", r"^find", r"^id", r"^I2G"],
    }
    
    # Ensure directory exists
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize files if they don't exist
    if not COMMANDS_FILE.exists():
        with open(COMMANDS_FILE, "w") as f:
            json.dump({"Manually Added": [], "Favorites": []}, f, indent=4)
            
    if not DESCRIPTIONS_FILE.exists():
        with open(DESCRIPTIONS_FILE, "w") as f:
            json.dump({}, f, indent=4)
            
    if not STATS_FILE.exists():
        with open(STATS_FILE, "w") as f:
            json.dump({"usage_counts": {}, "last_used": {}, "usage_history": {}}, f, indent=4)
            
    if not PENDING_FILE.exists():
        with open(PENDING_FILE, "w") as f:
            json.dump({"pending": {}, "rejected": []}, f, indent=4)
            
    if not ALIASES_FILE.exists():
        with open(ALIASES_FILE, "w") as f:
            json.dump({}, f, indent=4)
            
    if not GROUPS_FILE.exists():
        with open(GROUPS_FILE, "w") as f:
            json.dump({}, f, indent=4)
            
    if not TEMPLATES_FILE.exists():
        with open(TEMPLATES_FILE, "w") as f:
            json.dump({}, f, indent=4)
    
    # Helper functions for JSON storage
    def load_commands():
        try:
            with open(COMMANDS_FILE, "r") as f:
                data = json.load(f)
                # Ensure required categories exist
                if "Manually Added" not in data:
                    data["Manually Added"] = []
                if "Favorites" not in data:
                    data["Favorites"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"Manually Added": [], "Favorites": []}
    
    def save_commands(commands):
        with open(COMMANDS_FILE, "w") as f:
            json.dump(commands, f, indent=4)
    
    def load_descriptions():
        try:
            with open(DESCRIPTIONS_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_descriptions(descriptions):
        with open(DESCRIPTIONS_FILE, "w") as f:
            json.dump(descriptions, f, indent=4)
    
    def load_stats():
        try:
            with open(STATS_FILE, "r") as f:
                data = json.load(f)
                if "usage_counts" not in data:
                    data["usage_counts"] = {}
                if "last_used" not in data:
                    data["last_used"] = {}
                if "usage_history" not in data:
                    data["usage_history"] = {}
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"usage_counts": {}, "last_used": {}, "usage_history": {}}
    
    def save_stats(stats):
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=4)
            
    def load_pending():
        try:
            with open(PENDING_FILE, "r") as f:
                data = json.load(f)
                if "pending" not in data:
                    data["pending"] = {}
                if "rejected" not in data:
                    data["rejected"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"pending": {}, "rejected": []}
    
    def save_pending(pending_data):
        with open(PENDING_FILE, "w") as f:
            json.dump(pending_data, f, indent=4)
    
    def load_aliases():
        try:
            with open(ALIASES_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_aliases(aliases):
        with open(ALIASES_FILE, "w") as f:
            json.dump(aliases, f, indent=4)
    
    def load_groups():
        try:
            with open(GROUPS_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_groups(groups):
        with open(GROUPS_FILE, "w") as f:
            json.dump(groups, f, indent=4)
    
    def load_templates():
        try:
            with open(TEMPLATES_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_templates(templates):
        with open(TEMPLATES_FILE, "w") as f:
            json.dump(templates, f, indent=4)
    
    # Get current prefix
    def get_prefix():
        return getConfigData().get(PREFIX_KEY, ".")
    
    # Helper function to auto-delete messages after a delay
    async def auto_delete_message(message, timeout):
        try:
            await asyncio.sleep(timeout)
            await message.delete()
        except Exception:
            pass  # Ignore errors if message already deleted
    
    # Enhanced send function with auto-delete (short timeout by default)
    async def send_message(ctx, content, long_timeout=False):
        message = await ctx.send(content)
        timeout = LONG_TIMEOUT if long_timeout else SHORT_TIMEOUT
        asyncio.create_task(auto_delete_message(message, timeout))
        return message
    
    # Function to track command execution for rate limiting
    def track_command_execution():
        """Track each command execution for rate limiting"""
        if not RATE_MONITOR["enabled"]:
            return
            
        RATE_MONITOR["command_count"] += 1
        
        # Check rate limits after incrementing
        asyncio.create_task(check_rate_limits())
    
    # Error decorator for command handlers
    def handle_errors(func):
        """Decorator to add error handling to commands"""
        @functools.wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            try:
                # Track command execution for rate limiting
                track_command_execution()
                
                # Execute the original command
                return await func(ctx, *args, **kwargs)
            except Exception as e:
                prefix = get_prefix()
                
                # Log error
                print(f"Error in {func.__name__}: {str(e)}", type_="ERROR")
                
                # Get command name for better error messages
                command_name = func.__name__
                if command_name.endswith("_command"):
                    command_name = command_name[:-8]  # Remove _command suffix
                
                # Format user-friendly error message
                error_msg = f"❌ **Error executing `{prefix}{command_name}`**\n\n"
                
                # Different error messages based on error type
                if isinstance(e, ValueError):
                    error_msg += f"Invalid value: {str(e)}\n\n"
                    error_msg += f"Try `{prefix}help {command_name}` for correct usage."
                elif isinstance(e, KeyError):
                    error_msg += f"Missing key or item: {str(e)}\n\n"
                    error_msg += f"This might be a configuration issue or missing data."
                elif isinstance(e, FileNotFoundError):
                    error_msg += f"File not found: {str(e)}\n\n"
                    error_msg += "This might be due to missing or corrupted data files."
                elif isinstance(e, json.JSONDecodeError):
                    error_msg += "Error reading data file. File might be corrupted.\n\n"
                    error_msg += "Try using a backup or reset the configuration."
                else:
                    error_msg += f"Unexpected error: {str(e)}\n\n"
                    error_msg += "This is likely a bug. Please report it to the developer."
                
                await send_message(ctx, error_msg, long_timeout=True)
        
        return wrapper
    
    # Rate Limit Protection Systems
    async def check_rate_limits(channel=None):
        """Check if we're approaching rate limits and take action if needed"""
        if not RATE_MONITOR["enabled"] or RATE_MONITOR["restart_triggered"]:
            return  # Skip if disabled or already triggered
            
        thresholds = getConfigData().get(RATE_MONITOR_THRESHOLD_KEY)
        
        is_critical = (
            RATE_MONITOR["message_count"] >= thresholds["messages_per_minute"] or
            RATE_MONITOR["command_count"] >= thresholds["commands_per_minute"] or
            RATE_MONITOR["api_calls"] >= thresholds["api_calls_per_minute"]
        )
        
        # Also check for error message patterns
        error_detected = await check_for_error_spam()
        
        if is_critical or error_detected:
            RATE_MONITOR["restart_triggered"] = True
            
            # Log the event
            reason = "Rate limit exceeded" if is_critical else "Error message spam detected"
            details = f"Messages: {RATE_MONITOR['message_count']}, Commands: {RATE_MONITOR['command_count']}"
            
            log_path = await log_rate_limit_event(reason, details)
            
            # Send warning message if possible
            if channel:
                try:
                    await channel.send(f"⚠️ **{reason.upper()}!** sorry for the spam ima go touch grass")
                except:
                    pass  # Failed to send message, continue with restart
            
            # Clean up error messages if detected
            if error_detected:
                await emergency_message_analysis()
            
            # Execute restart
            await restart_bot()
    
    async def check_for_error_spam():
        """Analyze patterns to detect error message spam across servers"""
        current_time = time.time()
        recent_msgs = RATE_MONITOR["recent_messages"]
        
        # Skip if too few messages to analyze
        if len(recent_msgs) < 3:
            return False
        
        # 1. Check for error patterns in messages
        error_messages = []
        for msg in recent_msgs:
            content = msg["content"].lower()
            
            # Check against error patterns
            is_error = any(re.search(pattern, content, re.IGNORECASE) 
                        for pattern in RATE_MONITOR["error_patterns"])
            
            if is_error:
                error_messages.append(msg)
        
        # 2. Check if sending to multiple servers rapidly
        active_servers = set()
        for msg in recent_msgs:
            if msg["server_id"]:
                active_servers.add(msg["server_id"])
        
        # 3. Check for similar content being sent repeatedly
        content_counter = Counter([msg["content"] for msg in recent_msgs])
        repeated_content = [content for content, count in content_counter.items() 
                        if count >= RATE_MONITOR["similar_content_threshold"]]
        
        # Detect problematic patterns
        is_critical = (
            # Too many error messages
            (len(error_messages) >= 3) or
            
            # Active on too many servers simultaneously
            (len(active_servers) >= RATE_MONITOR["unique_servers_threshold"] and 
            len(recent_msgs) >= 5) or
            
            # Same message sent repeatedly
            repeated_content
        )
        
        return is_critical
    
    async def analyze_message_content(content):
        """Advanced analysis of message content for error detection"""
        # Convert to lowercase for comparison
        content_lower = content.lower()
        
        # Basic flags
        flags = {
            "is_long": len(content) > 200,
            "has_error_keyword": any(kw in content_lower for kw in ["error", "exception", "failed"]),
            "has_code_block": "```" in content,
            "has_stack_trace": bool(re.search(r"at\s+[\w\.]+\([\w\.]+:\d+\)", content)),
            "has_url": bool(re.search(r"https?://\S+", content)),
        }
        
        # Additional analysis
        line_count = content.count('\n') + 1
        flags["is_multiline"] = line_count > 3
        
        # Calculate error probability based on flags
        error_score = 0
        if flags["is_long"]: error_score += 1
        if flags["has_error_keyword"]: error_score += 2
        if flags["has_code_block"]: error_score += 1
        if flags["has_stack_trace"]: error_score += 3
        if flags["is_multiline"]: error_score += 1
        
        return {
            "flags": flags,
            "error_score": error_score,
            "line_count": line_count,
            "is_likely_error": error_score >= 3
        }
    
    async def emergency_message_analysis():
        """Last-minute analysis before restart to catch all error messages"""
        error_messages = []
        normal_messages = []
        
        # Analyze all recent messages
        for msg_data in RATE_MONITOR["recent_messages"]:
            content = msg_data["content"]
            analysis = await analyze_message_content(content)
            
            if analysis["is_likely_error"]:
                error_messages.append(msg_data)
            else:
                normal_messages.append(msg_data)
        
        # Prioritize deleting detected error messages
        print(f"Emergency analysis found {len(error_messages)} likely error messages", type_="INFO")
        
        deleted_count = 0
        if error_messages:
            deleted_count = await delete_recent_messages(error_messages)
        else:
            # If no clear error messages, delete most recent messages as fallback
            most_recent = sorted(RATE_MONITOR["recent_messages"], 
                                key=lambda x: x["timestamp"], 
                                reverse=True)[:10]
            deleted_count = await delete_recent_messages(most_recent)
        
        return deleted_count
    
    async def delete_recent_messages(messages_to_delete):
        """Attempt to delete recent messages before restart"""
        print(f"Attempting to delete {len(messages_to_delete)} messages before restart", type_="INFO")
        
        delete_count = 0
        for msg_data in messages_to_delete:
            try:
                # Get the channel
                channel = bot.get_channel(msg_data["channel_id"])
                if not channel:
                    continue
                    
                # Get and delete the message
                try:
                    message = await channel.fetch_message(msg_data["message_id"])
                    await message.delete()
                    delete_count += 1
                    
                    # Brief delay to avoid rate limits on deletion
                    await asyncio.sleep(0.1)
                except:
                    continue
            except:
                continue
        
        print(f"Successfully deleted {delete_count}/{len(messages_to_delete)} messages", type_="INFO")
        return delete_count
    
    async def log_rate_limit_event(reason, details):
        """Log rate limit detection and actions taken"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Count deleted messages (if any)
        deleted_count = 0
        if RATE_MONITOR["recent_messages"]:
            deleted_count = await emergency_message_analysis()
        
        # Create the log entry
        log_entry = f"=== RATE LIMIT EVENT: {timestamp} ===\n"
        log_entry += f"Reason: {reason}\n"
        log_entry += f"Details: {details}\n"
        
        # Log message counts
        log_entry += f"Message count: {RATE_MONITOR['message_count']}\n"
        log_entry += f"Command count: {RATE_MONITOR['command_count']}\n"
        
        # Log active servers
        active_servers = len(RATE_MONITOR["server_activity"])
        log_entry += f"Active servers: {active_servers}\n"
        
        # Log action taken
        log_entry += f"Action: Deleted {deleted_count} messages before restart\n"
        log_entry += "==========================================\n\n"
        
        # Write to log file
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
        
        # Also log to standard logger
        rate_logger.warning(f"Rate limit triggered: {reason}")
        
        # Return path to log file for user information
        return str(LOG_FILE)
    
    # Reset counters periodically
    async def rate_monitor_reset_task():
        while True:
            await asyncio.sleep(RATE_MONITOR["reset_interval"])
            
            current_time = time.time()
            if current_time - RATE_MONITOR["last_reset"] >= RATE_MONITOR["reset_interval"]:
                # Reset counters
                RATE_MONITOR["message_count"] = 0
                RATE_MONITOR["command_count"] = 0
                RATE_MONITOR["api_calls"] = 0
                RATE_MONITOR["last_reset"] = current_time
                RATE_MONITOR["restart_triggered"] = False
                
                # Log reset if any counts were high
                if RATE_MONITOR["message_count"] > 50 or RATE_MONITOR["command_count"] > 50:
                    print(f"Rate monitor counters reset. Previous values - Messages: {RATE_MONITOR['message_count']}, Commands: {RATE_MONITOR['command_count']}", type_="DEBUG")
    
    # Start reset task
    @bot.listen("on_ready")
    async def start_rate_monitor():
        """Start the rate monitor reset task when bot is ready"""
        asyncio.create_task(rate_monitor_reset_task())
        print("Rate limit monitoring system initialized", type_="INFO")
    
    # Restart function - this will use the user's existing restart implementation
    async def restart_bot():
        """Execute the bot restart using the provided restart function"""
        try:
            print("Executing bot restart via os.execv", type_="WARNING")
            
            # Call the existing restart function that was provided
            os.execv(sys.executable, ["python"] + sys.argv)
            
        except Exception as e:
            print(f"Failed to restart bot: {str(e)}", type_="ERROR")
    
    # Check if a command appears to be invalid based on error patterns
    def is_error_message(message_content):
        if not message_content:
            return False
            
        # Convert to lowercase for case-insensitive matching
        message_lower = message_content.lower()
        
        # Check against error patterns
        for pattern in ERROR_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True
                
        return False
    
    # Add command to pending validation list
    def add_command_to_pending(command_name):
        # Skip our own commands
        if command_name in OWN_COMMANDS:
            return False
            
        # Skip if already in rejected list
        pending_data = load_pending()
        if command_name in pending_data["rejected"]:
            return False
            
        # Skip if already in confirmed commands
        commands = load_commands()
        for category, cmds in commands.items():
            if command_name in cmds:
                return False
                
        # Add to pending with timestamp
        pending_data["pending"][command_name] = {
            "timestamp": time.time(),
            "seen_count": 1,
            "validation_attempts": 0
        }
        
        save_pending(pending_data)
        return True
    
    # Increment seen count for pending command
    def increment_pending_seen(command_name):
        pending_data = load_pending()
        if command_name in pending_data["pending"]:
            pending_data["pending"][command_name]["seen_count"] += 1
            pending_data["pending"][command_name]["timestamp"] = time.time()  # Update timestamp
            save_pending(pending_data)
    
    # Validate a pending command
    def validate_pending_command(command_name):
        pending_data = load_pending()
        
        # Skip if not in pending
        if command_name not in pending_data["pending"]:
            return False
            
        # Get command data and remove from pending
        command_data = pending_data["pending"].pop(command_name)
        save_pending(pending_data)
        
        # Add to appropriate category
        category = identify_category_for_command(command_name)
        commands = load_commands()
        
        if category not in commands:
            commands[category] = []
            
        if command_name not in commands[category]:
            commands[category].append(command_name)
            save_commands(commands)
            
        return True
    
    # Reject a pending command
    def reject_pending_command(command_name):
        pending_data = load_pending()
        
        # Skip if not in pending
        if command_name not in pending_data["pending"]:
            return False
            
        # Remove from pending and add to rejected
        pending_data["pending"].pop(command_name)
        if command_name not in pending_data["rejected"]:
            pending_data["rejected"].append(command_name)
            
        save_pending(pending_data)
        return True
    
    # Auto-validate based on usage count and time
    def auto_validate_commands():
        pending_data = load_pending()
        current_time = time.time()
        
        # Commands to validate
        to_validate = []
        
        for command, data in list(pending_data["pending"].items()):
            # If seen multiple times without errors, consider it valid
            if data["seen_count"] >= 3:
                to_validate.append(command)
            # If it's been around for over 3 days, validate it
            elif current_time - data["timestamp"] > 259200:  # 3 days in seconds
                if data["seen_count"] >= 2:
                    to_validate.append(command)
        
        # Validate commands
        for command in to_validate:
            validate_pending_command(command)
            
        # Clean up old pending commands (over 7 days)
        for command, data in list(pending_data["pending"].items()):
            if current_time - data["timestamp"] > 604800:  # 7 days in seconds
                pending_data["pending"].pop(command)
                
        save_pending(pending_data)
    
    # Mark command as failed validation
    def mark_command_failed(command_name):
        pending_data = load_pending()
        
        if command_name in pending_data["pending"]:
            # Increment validation attempts
            pending_data["pending"][command_name]["validation_attempts"] += 1
            
            # If too many failed attempts, reject it
            if pending_data["pending"][command_name]["validation_attempts"] >= 3:
                reject_pending_command(command_name)
            else:
                save_pending(pending_data)
    
    # Track command usage with enhanced history
    def track_command_usage(command_name):
        stats = load_stats()
        current_time = time.time()
        today = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d')
        
        # Update usage count
        if command_name not in stats["usage_counts"]:
            stats["usage_counts"][command_name] = 1
        else:
            stats["usage_counts"][command_name] += 1
            
        # Update last used timestamp
        stats["last_used"][command_name] = current_time
        
        # Update usage history
        if command_name not in stats["usage_history"]:
            stats["usage_history"][command_name] = {}
        
        if today not in stats["usage_history"][command_name]:
            stats["usage_history"][command_name][today] = 1
        else:
            stats["usage_history"][command_name][today] += 1
        
        # Clean up old history (keep last 30 days)
        for cmd, history in stats["usage_history"].items():
            cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            for date in list(history.keys()):
                if date < cutoff_date:
                    history.pop(date)
        
        save_stats(stats)
    
    # Identify which category a command belongs to
    def identify_category_for_command(command_name):
        # Check against known patterns first
        for category, patterns in COMMAND_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, command_name.lower()):
                    return category
        
        # If no pattern match, check existing categories
        scripts = load_commands()
        
        # Check if the command matches an existing category name
        for script in scripts.keys():
            if script.lower() in command_name.lower() or command_name.lower() in script.lower():
                return script
                
        # Return Uncategorized if no match found
        return "Uncategorized"
    
    # Helper to find which categories a command is in
    def find_command_categories(command_name):
        categories = []
        commands = load_commands()
        for category, cmds in commands.items():
            if command_name in cmds:
                categories.append(category)
        return categories
    
    # Format timestamp
    def format_timestamp(timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        now = datetime.datetime.now()
        
        delta = now - dt
        
        if delta.days == 0:
            if delta.seconds < 60:
                return "just now"
            elif delta.seconds < 3600:
                minutes = delta.seconds // 60
                return f"{minutes}m ago"
            else:
                hours = delta.seconds // 3600
                return f"{hours}h ago"
        elif delta.days == 1:
            return "yesterday"
        elif delta.days < 7:
            return f"{delta.days}d ago"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks}w ago"
        elif delta.days < 365:
            months = delta.days // 30
            return f"{months}mo ago"
        else:
            years = delta.days // 365
            return f"{years}y ago"
    
    # Generate ASCII bar chart for visualization
    def generate_bar_chart(data, max_width=20):
        if not data:
            return "No data to display"
            
        max_value = max(data.values())
        max_label_length = max(len(label) for label in data.keys())
        
        chart = []
        for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
            if max_value > 0:
                bar_width = int((value / max_value) * max_width)
            else:
                bar_width = 0
            bar = "█" * bar_width
            chart.append(f"{label.ljust(max_label_length)} | {bar} {value}")
            
        return "\n".join(chart)
    
    # Generate unique export code
    def generate_export_code(data):
        # Convert data to JSON and compress
        json_data = json.dumps(data)
        compressed = zlib.compress(json_data.encode('utf-8'))
        b64_data = base64.b64encode(compressed).decode('utf-8')
        
        # Add prefix for identification
        return f"CMD-{b64_data}"
    
    # Parse export code
    def parse_export_code(code):
        try:
            # Strip prefix and decode
            if code.startswith("CMD-"):
                b64_data = code[4:]
            else:
                b64_data = code
                
            compressed = base64.b64decode(b64_data)
            json_data = zlib.decompress(compressed).decode('utf-8')
            return json.loads(json_data)
        except Exception as e:
            return None
    
    # Process template with parameters
    def process_template(template, params):
        # Extract parameter values
        param_dict = {}
        
        # Parse params format: key1="value1" key2="value2"
        param_pattern = r'(\w+)="([^"]*)"'
        matches = re.findall(param_pattern, params)
        
        for key, value in matches:
            param_dict[key] = value
            
        # Replace placeholders in template
        result = template
        for key, value in param_dict.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, value)
            
        # Check if all placeholders were replaced
        if re.search(r"{[^{}]+}", result):
            return None  # Missing parameters
            
        return result
    
    # Generate command suggestions based on usage patterns
    def generate_suggestions():
        stats = load_stats()
        commands = load_commands()
        aliases = load_aliases()
        
        suggestions = []
        
        # Flatten all commands into a single list
        all_commands = set()
        for category, cmds in commands.items():
            all_commands.update(cmds)
            
        # Find most used commands without aliases
        most_used = []
        for cmd, count in sorted(stats["usage_counts"].items(), key=lambda x: x[1], reverse=True):
            if cmd in all_commands and cmd not in aliases.values():
                most_used.append((cmd, count))
                if len(most_used) >= 5:
                    break
                    
        # Suggest aliases for long, frequently used commands
        for cmd, count in most_used:
            if len(cmd) > 5 and count > 3:
                alias_suggestion = cmd[:3]
                if alias_suggestion not in aliases:
                    suggestions.append({
                        "type": "alias",
                        "command": cmd,
                        "suggestion": alias_suggestion,
                        "message": f"Create alias '{alias_suggestion}' for frequently used command '{cmd}'"
                    })
                    
        # Suggest moving commands to appropriate categories
        for cmd in all_commands:
            categories = find_command_categories(cmd)
            if len(categories) == 1 and categories[0] not in ["Manually Added", "Favorites", "Uncategorized"]:
                continue
                
            suggested_category = identify_category_for_command(cmd)
            if suggested_category not in categories and suggested_category not in ["Uncategorized", "Manually Added"]:
                suggestions.append({
                    "type": "category",
                    "command": cmd,
                    "suggestion": suggested_category,
                    "message": f"Move command '{cmd}' to '{suggested_category}' category"
                })
                
        return suggestions
    
    # Generate documentation
    def generate_documentation(format_type="markdown"):
        commands = load_commands()
        descriptions = load_descriptions()
        aliases = load_aliases()
        templates = load_templates()
        groups = load_groups()
        
        prefix = get_prefix()
        
        if format_type == "markdown":
            doc = "# Command Documentation\n\n"
            
            # Add overview
            doc += "## Overview\n\n"
            
            # Count total commands
            total_count = sum(len(cmds) for script, cmds in commands.items())
            unique_count = len(set(cmd for script, cmds in commands.items() for cmd in cmds))
            
            doc += f"- Total Commands: {unique_count}\n"
            doc += f"- Prefix: `{prefix}`\n"
            doc += f"- Aliases: {len(aliases)}\n"
            doc += f"- Templates: {len(templates)}\n"
            doc += f"- Groups: {len(groups)}\n\n"
            
            # Add commands by category
            doc += "## Commands by Category\n\n"
            
            for category, cmds in sorted(commands.items()):
                if cmds:  # Only show categories with commands
                    doc += f"### {category}\n\n"
                    for cmd in sorted(cmds):
                        desc = descriptions.get(cmd, "No description")
                        doc += f"- `{prefix}{cmd}` - {desc}\n"
                    doc += "\n"
                    
            # Add aliases section
            if aliases:
                doc += "## Aliases\n\n"
                for alias, cmd in sorted(aliases.items()):
                    doc += f"- `{prefix}{alias}` → `{prefix}{cmd}`\n"
                doc += "\n"
                
            # Add templates section
            if templates:
                doc += "## Templates\n\n"
                for name, template in sorted(templates.items()):
                    doc += f"### {name}\n\n"
                    doc += f"Template: `{template}`\n\n"
                    
                    # Extract parameters
                    params = re.findall(r"{([^{}]+)}", template)
                    if params:
                        doc += "Parameters:\n"
                        for param in params:
                            doc += f"- `{param}`\n"
                    doc += "\n"
                    
            # Add groups section
            if groups:
                doc += "## Groups\n\n"
                for name, cmds in sorted(groups.items()):
                    doc += f"### {name}\n\n"
                    for cmd in cmds:
                        desc = descriptions.get(cmd, "No description")
                        doc += f"- `{prefix}{cmd}` - {desc}\n"
                    doc += "\n"
                    
            return doc
        
        elif format_type == "plain":
            # Plain text format for Discord messages
            doc = "📖 COMMAND DOCUMENTATION\n\n"
            
            # Count total commands
            total_count = sum(len(cmds) for script, cmds in commands.items())
            unique_count = len(set(cmd for script, cmds in commands.items() for cmd in cmds))
            
            doc += f"Total Commands: {unique_count}\n"
            doc += f"Prefix: {prefix}\n"
            doc += f"Aliases: {len(aliases)}\n"
            doc += f"Templates: {len(templates)}\n"
            doc += f"Groups: {len(groups)}\n\n"
            
            # Add commands by category
            doc += "COMMANDS BY CATEGORY:\n\n"
            
            for category, cmds in sorted(commands.items()):
                if cmds:  # Only show categories with commands
                    doc += f"-- {category} --\n"
                    for cmd in sorted(cmds):
                        desc = descriptions.get(cmd, "No description")
                        doc += f"{prefix}{cmd} - {desc}\n"
                    doc += "\n"
                    
            # Add aliases section
            if aliases:
                doc += "ALIASES:\n\n"
                for alias, cmd in sorted(aliases.items()):
                    doc += f"{prefix}{alias} → {prefix}{cmd}\n"
                doc += "\n"
                    
            return doc
        
        else:
            return "Unsupported format type. Use 'markdown' or 'plain'."
            
    # Storage and helper functions for command examples
    EXAMPLES_FILE = BASE_DIR / "command_examples.json"
    
    def load_command_examples():
        try:
            with open(EXAMPLES_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_command_examples(examples):
        with open(EXAMPLES_FILE, "w") as f:
            json.dump(examples, f, indent=4)
    
    def get_command_examples(command_name):
        examples = load_command_examples()
        return examples.get(command_name, [])
    
    def add_command_example(command_name, full_command):
        examples = load_command_examples()
        
        # Initialize if not exists
        if command_name not in examples:
            examples[command_name] = []
            
        # Add example if it's not already in the list
        if full_command not in examples[command_name]:
            examples[command_name].append(full_command)
            # Keep only the most recent 5 examples
            examples[command_name] = examples[command_name][-5:]
            save_command_examples(examples)
            return True
        return False
    
    # Process command validation or rejection based on message content
    async def process_command_validation(message, command_name):
        # Check if it's an error message
        if is_error_message(message.content):
            # Mark the command as failed
            mark_command_failed(command_name)
            return False
            
        # If not an error, increment seen counter
        increment_pending_seen(command_name)
        
        # Try to detect a description if we don't have one yet
        descriptions = load_descriptions()
        if command_name not in descriptions:
            # Look for description patterns in response
            if message.author.id == bot.user.id:
                try_detect_description(command_name, message.content)
            
        return True
        
    # Generate a help message for a specific feature
    def generate_help_message(feature=None):
        prefix = get_prefix()
        
        if not feature:
            # General help
            help_msg = "**📚 Command Viewer Help**\n\n"
            help_msg += f"Current Prefix: `{prefix}`\n\n"
            
             # Add notice about slash command transition
            help_msg += "**⚠️ IMPORTANT NOTICE ⚠️**\n"
            help_msg += "Nighty has transitioned to slash commands (/). For slash command help, please use Nighty's built-in help system using (/help).\n"
            help_msg += "This script works with traditional prefix commands as shown below.\n\n"
        
            help_msg += "**Core Features:**\n"
            help_msg += f"• `{prefix}help <feature>` - Get detailed help on a specific feature\n"
            help_msg += f"• `{prefix}tutorial` - Show a beginner's guide\n"
            help_msg += f"• `{prefix}helpcommands` - List all saved commands\n"
            help_msg += f"• `{prefix}savecommand <cmd>` - Save commands manually\n"
            help_msg += f"• `{prefix}search <term>` - Search for commands\n\n"
            
            help_msg += "**Available Features:**\n"
            help_msg += f"• **Aliases** - Create shortcuts for commands (`{prefix}help alias`)\n"
            help_msg += f"• **Groups** - Run multiple commands with one command (`{prefix}help group`)\n"
            help_msg += f"• **Templates** - Create command patterns with placeholders (`{prefix}help template`)\n"
            help_msg += f"• **Stats** - View command usage statistics (`{prefix}help stats`)\n"
            help_msg += f"• **Export/Import** - Share command setups (`{prefix}help export`)\n"
            help_msg += f"• **Rate Protection** - Prevent Discord API bans (`{prefix}help ratelimit`)\n\n"
            
            help_msg += f"Use `{prefix}help <feature>` for detailed help on each feature."
            
            return help_msg
        
        # Check if feature is a command name first - this fixes the issue with help (cmd) showing unknown feature
        commands = load_commands()
        descriptions = load_descriptions()
        all_commands = set()
        
        # Collect all commands into a single set
        for category, cmds in commands.items():
            all_commands.update(cmds)
            
        # If feature exactly matches a command name, show info about that command
        if feature in all_commands:
            command_name = feature
            command_desc = descriptions.get(command_name, "No description available")
            
            # Find categories where command appears
            categories = find_command_categories(command_name)
            categories_str = ", ".join(categories) if categories else "None"
            
            # Get command usage stats
            stats = load_stats()
            usage_count = stats["usage_counts"].get(command_name, 0)
            last_used = "Never" 
            if command_name in stats["last_used"]:
                last_used = format_timestamp(stats["last_used"][command_name])
            
            # Try to get examples of full command usage from previous auto-description tracking
            command_examples = get_command_examples(command_name)
            
            help_msg = f"**Command: `{prefix}{command_name}`**\n\n"
            help_msg += f"**Description:** {command_desc}\n\n"
            
            if command_examples:
                help_msg += "**Usage Examples:**\n"
                for example in command_examples[:3]:  # Show up to 3 examples
                    help_msg += f"• `{prefix}{example}`\n"
                help_msg += "\n"
            
            help_msg += f"**Categories:** {categories_str}\n"
            help_msg += f"**Times Used:** {usage_count}\n"
            help_msg += f"**Last Used:** {last_used}\n\n"
            
            # Check if command has aliases pointing to it
            aliases = load_aliases()
            pointing_aliases = []
            for alias_name, alias_target in aliases.items():
                if alias_target == command_name:
                    pointing_aliases.append(alias_name)
            
            if pointing_aliases:
                help_msg += f"**Aliases:** {', '.join([f'`{prefix}{a}`' for a in pointing_aliases])}\n\n"
            
            help_msg += f"**Related Commands:**\n"
            help_msg += f"• `{prefix}stats {command_name}` - View detailed usage statistics\n"
            help_msg += f"• `{prefix}adddesc {command_name} <description>` - Update description\n"
            
            return help_msg
            
        # Feature-specific help
        feature = feature.lower()
        
        if feature == "alias" or feature == "aliases":
            help_msg = "**🔄 Alias System Help**\n\n"
            help_msg += "Aliases are shortcuts to longer commands. For example, create an alias 'pm' for 'purgemessages'.\n\n"
            
            help_msg += "**Commands:**\n"
            help_msg += f"• `{prefix}alias add <alias> <command>` - Create a new alias\n"
            help_msg += f"• `{prefix}alias remove <alias>` - Delete an existing alias\n"
            help_msg += f"• `{prefix}alias list` - Show all aliases\n\n"
            
            help_msg += "**Examples:**\n"
            help_msg += f"• `{prefix}alias add pm purgemessages` - Creates alias 'pm' for 'purgemessages'\n"
            help_msg += f"• `{prefix}pm 10` - Would execute '{prefix}purgemessages 10'\n"
            help_msg += f"• `{prefix}alias remove pm` - Removes the 'pm' alias\n\n"
            
            help_msg += "**Notes:**\n"
            help_msg += "• Aliases support passing arguments to the target command\n"
            help_msg += "• You cannot create an alias that points to another alias\n"
            help_msg += "• Alias names must contain only letters, numbers, and underscores"
            
            return help_msg
            
        elif feature == "group" or feature == "groups":
            help_msg = "**👥 Command Groups Help**\n\n"
            help_msg += "Groups let you organize related commands and run them all with a single command.\n\n"
            
            help_msg += "**Commands:**\n"
            help_msg += f"• `{prefix}group create <n> <cmd1> <cmd2> ...` - Create a new group\n"
            help_msg += f"• `{prefix}group add <n> <cmd>` - Add a command to a group\n"
            help_msg += f"• `{prefix}group remove <n> <cmd>` - Remove a command from a group\n"
            help_msg += f"• `{prefix}group run <n>` - Run all commands in a group\n"
            help_msg += f"• `{prefix}group list` - Show all groups\n\n"
            
            help_msg += "**Examples:**\n"
            help_msg += f"• `{prefix}group create mod ban kick mute` - Creates 'mod' group with 3 commands\n"
            help_msg += f"• `{prefix}group add mod warn` - Adds 'warn' command to 'mod' group\n"
            help_msg += f"• `{prefix}group run mod` - Runs all commands in the 'mod' group\n\n"
            
            help_msg += "**Notes:**\n"
            help_msg += "• Commands run in the order they were added to the group\n"
            help_msg += "• There's a small delay between commands to avoid rate limiting\n"
            help_msg += "• Use groups for related commands that you often use together"
            
            return help_msg
            
        elif feature == "template" or feature == "templates":
            help_msg = "**📝 Command Templates Help**\n\n"
            help_msg += "Templates let you create command patterns with placeholders that can be filled in later.\n\n"
            
            help_msg += "**Commands:**\n"
            help_msg += f"• `{prefix}template create <n> <template>` - Create a new template\n"
            help_msg += f"• `{prefix}template use <n> <params>` - Use a template with parameters\n"
            help_msg += f"• `{prefix}template list` - Show all templates\n"
            help_msg += f"• `{prefix}template remove <n>` - Delete a template\n\n"
            
            help_msg += "**Creating Templates:**\n"
            help_msg += f"• `{prefix}template create announce say {{message}} in {{channel}}`\n"
            help_msg += "• Parameters are defined using curly braces: `{parameter_name}`\n\n"
            
            help_msg += "**Using Templates (Two Methods):**\n"
            help_msg += "Method 1: Named parameters\n"
            help_msg += f"• `{prefix}template use announce message=\"Hello everyone\" channel=\"#general\"`\n"
            help_msg += "Method 2: Positional parameters (simpler, in parameter order)\n"
            help_msg += f"• `{prefix}template use announce \"Hello everyone\" \"#general\"`\n\n"
            
            help_msg += "**Examples:**\n"
            help_msg += "Example 1: Message announcement\n"
            help_msg += f"• Create: `{prefix}template create msg {{text}} @everyone`\n"
            help_msg += f"• Use: `{prefix}template use msg \"Server maintenance in 10 minutes\"`\n\n"
            
            help_msg += "Example 2: Role assignment\n"
            help_msg += f"• Create: `{prefix}template create role addrole {{user}} {{role}}`\n"
            help_msg += f"• Use (Method 1): `{prefix}template use role user=\"@john\" role=\"Member\"`\n"
            help_msg += f"• Use (Method 2): `{prefix}template use role \"@john\" \"Member\"`\n\n"
            
            help_msg += "**Removing Templates:**\n"
            help_msg += f"• `{prefix}template remove announce` - Removes the 'announce' template\n\n"
            
            help_msg += "**Notes:**\n"
            help_msg += "• All parameters must be provided when using a template\n"
            help_msg += "• Templates can dramatically simplify complex commands\n"
            help_msg += "• Use Method 2 (positional parameters) for simpler, quicker usage"
            
            return help_msg
            
        elif feature == "stats" or feature == "statistics":
            help_msg = "**📊 Command Statistics Help**\n\n"
            help_msg += "The stats system tracks how you use commands and visualizes usage patterns.\n\n"
            
            help_msg += "**Commands:**\n"
            help_msg += f"• `{prefix}stats` - Show overall command usage statistics\n"
            help_msg += f"• `{prefix}stats <command>` - Show detailed stats for a specific command\n\n"
            
            help_msg += "**Examples:**\n"
            help_msg += f"• `{prefix}stats` - Shows your most used commands with a chart\n"
            help_msg += f"• `{prefix}stats purgemessages` - Shows detailed usage history for 'purgemessages'\n\n"
            
            help_msg += "**Notes:**\n"
            help_msg += "• The system tracks command usage count and timestamps\n"
            help_msg += "• Usage history for the last 30 days is maintained\n"
            help_msg += "• Statistics are used to generate command suggestions"
            
            return help_msg
            
        elif feature == "export" or feature == "import":
            help_msg = "**📤 Export/Import System Help**\n\n"
            help_msg += "This system lets you share your command setup with others or back it up.\n\n"
            
            help_msg += "**Commands:**\n"
            help_msg += f"• `{prefix}export` - Export all commands as a shareable code\n"
            help_msg += f"• `{prefix}export <category>` - Export commands from a specific category\n"
            help_msg += f"• `{prefix}import <code>` - Import commands from an export code\n\n"
            
            help_msg += "**Examples:**\n"
            help_msg += f"• `{prefix}export` - Generates a code containing all your commands\n"
            help_msg += f"• `{prefix}export Utility` - Exports only commands in the 'Utility' category\n"
            help_msg += f"• `{prefix}import CMD-abc123...` - Imports commands from the given code\n\n"
            
            help_msg += "**Notes:**\n"
            help_msg += "• Export codes include commands, descriptions, and categories\n"
            help_msg += "• When importing, existing commands are not overwritten\n"
            help_msg += "• Export codes are compressed and encoded for efficient sharing"
            
            return help_msg
            
        elif feature == "search":
            help_msg = "**🔍 Search System Help**\n\n"
            help_msg += "Search helps you find commands by name or description.\n\n"
            
            help_msg += "**Command:**\n"
            help_msg += f"• `{prefix}search <term>` - Search for commands matching the term\n\n"
            
            help_msg += "**Examples:**\n"
            help_msg += f"• `{prefix}search message` - Find commands related to messages\n"
            help_msg += f"• `{prefix}search role` - Find commands related to roles\n\n"
            
            help_msg += "**Notes:**\n"
            help_msg += "• Search looks for the term in command names and descriptions\n"
            help_msg += "• Results are grouped into confirmed and pending commands\n"
            help_msg += "• Search is case-insensitive"
            
            return help_msg
            
        elif feature == "suggest" or feature == "suggestions":
            help_msg = "**💡 Command Suggestions Help**\n\n"
            help_msg += "The suggestion system analyzes your command usage and offers optimization tips.\n\n"
            
            help_msg += "**Command:**\n"
            help_msg += f"• `{prefix}suggest` - Get personalized command suggestions\n\n"
            
            help_msg += "**Suggestion Types:**\n"
            help_msg += "• **Alias Suggestions** - Recommends shortcuts for frequently used commands\n"
            help_msg += "• **Category Suggestions** - Suggests better organization for your commands\n\n"
            
            help_msg += "**Notes:**\n"
            help_msg += "• Suggestions are based on your actual command usage patterns\n"
            help_msg += "• The system needs some usage data to make good suggestions\n"
            help_msg += "• Each suggestion includes the command to implement it"
            
            return help_msg
            
        elif feature == "docs" or feature == "documentation":
            help_msg = "**📖 Documentation Generator Help**\n\n"
            help_msg += "Generate comprehensive documentation of all your commands.\n\n"
            
            help_msg += "**Commands:**\n"
            help_msg += f"• `{prefix}docs` - Generate plain text documentation\n"
            help_msg += f"• `{prefix}docs markdown` - Generate documentation in Markdown format\n\n"
            
            help_msg += "**Notes:**\n"
            help_msg += "• Documentation includes all commands, aliases, templates, and groups\n"
            help_msg += "• Markdown format is more suitable for sharing outside Discord\n"
            help_msg += "• Plain text format is optimized for Discord messages\n"
            help_msg += "• Documentation is automatically truncated if too long for Discord"
            
            return help_msg
        
        elif feature == "ratelimit" or feature == "rate":
            help_msg = "**⚡ Rate Limit Protection Help**\n\n"
            help_msg += "Rate limit protection monitors your Discord activity and prevents accidental API bans by detecting excessive messages, commands, or error spam.\n\n"
            
            help_msg += "**Key Features:**\n"
            help_msg += "• **Usage Monitoring** - Tracks message and command frequency\n"
            help_msg += "• **Error Detection** - Identifies error messages being sent to channels\n"
            help_msg += "• **Multi-Server Protection** - Detects spam across multiple servers\n"
            help_msg += "• **Smart Pre-Restart Cleanup** - Deletes error messages before restarting\n"
            help_msg += "• **Comprehensive Logging** - Records all protection events\n\n"
            
            help_msg += "**Commands:**\n"
            help_msg += f"• `{prefix}ratelimit` - View current status and configuration\n"
            help_msg += f"• `{prefix}ratelimit on` - Enable protection\n"
            help_msg += f"• `{prefix}ratelimit off` - Disable protection\n"
            help_msg += f"• `{prefix}ratelimit threshold <type> <value>` - Set thresholds\n"
            help_msg += f"• `{prefix}ratelimit pattern add <regex>` - Add error pattern\n"
            help_msg += f"• `{prefix}ratelimit pattern list` - View error patterns\n"
            help_msg += f"• `{prefix}ratelimit servers <num>` - Set server threshold\n"
            help_msg += f"• `{prefix}ratelogs` - View event history\n"
            help_msg += f"• `{prefix}emergency` - Trigger immediate cleanup and restart\n\n"
            
            help_msg += "**Thresholds:**\n"
            help_msg += "• **messages_per_minute** - Max messages allowed per minute\n"
            help_msg += "• **commands_per_minute** - Max commands allowed per minute\n"
            help_msg += "• **api_calls_per_minute** - Max API calls allowed per minute\n\n"
            
            help_msg += "**Error Detection:**\n"
            help_msg += "The system automatically detects common error patterns like stack traces, exceptions, and error messages. When detected across multiple servers or channels, it will trigger a protective restart.\n\n"
            
            help_msg += "**Example Usage:**\n"
            help_msg += f"• `{prefix}ratelimit on` - Enable protection\n"
            help_msg += f"• `{prefix}ratelimit threshold messages_per_minute 120` - Set message threshold\n"
            help_msg += f"• `{prefix}ratelimit pattern add TypeError:` - Add specific error pattern\n"
            
            return help_msg
            
        else:
            # Unknown feature - we'll check if it might be a command that's not in the database
            # This is a more friendly error message
            return f"Feature '{feature}' not found in help system. Use `{prefix}help` to see all available features. If you're looking for a command, try `{prefix}search {feature}` to find it."
    
    # Generate a beginner's tutorial
    def generate_tutorial():
        prefix = get_prefix()
        
        tutorial = "**🔰 Beginner's Guide to Command Viewer**\n\n"
        
        tutorial += "Welcome to the Enhanced Command Viewer! This guide will help you get started.\n\n"
        
        tutorial += "**Step 1: Understanding How It Works**\n"
        tutorial += "This script automatically saves valid commands when you use them with your prefix. It organizes them by category and lets you add descriptions, aliases, and more.\n\n"
        
        tutorial += "**Step 2: Viewing Your Commands**\n"
        tutorial += f"Type `{prefix}helpcommands` to see all your saved commands organized by category.\n\n"
        
        tutorial += "**Step 3: Adding Commands Manually**\n"
        tutorial += f"If a command isn't automatically saved, add it manually with:\n"
        tutorial += f"`{prefix}savecommand yourcommand`\n\n"
        
        tutorial += "**Step 4: Adding Descriptions**\n"
        tutorial += f"Make commands easier to understand by adding descriptions:\n"
        tutorial += f"`{prefix}adddesc yourcommand This command does something useful`\n\n"
        
        tutorial += "**Step 5: Creating Aliases (Shortcuts)**\n"
        tutorial += f"Create shortcuts for commands you use often:\n"
        tutorial += f"`{prefix}alias add ym yourcommand` (now you can use `{prefix}ym` instead)\n\n"
        
        tutorial += "**Step 6: Creating Command Groups**\n"
        tutorial += f"Group related commands to run them all at once:\n"
        tutorial += f"`{prefix}group create daily cmd1 cmd2 cmd3`\n"
        tutorial += f"`{prefix}group run daily` (runs all commands in the group)\n\n"
        
        tutorial += "**Step 7: Using Templates**\n"
        tutorial += f"Create templates for commands you use with different parameters:\n"
        tutorial += f"`{prefix}template create greet say Hello {{name}} in {{channel}}`\n"
        tutorial += f"`{prefix}template use greet name=\"John\" channel=\"#general\"`\n\n"
        
        tutorial += "**Step 8: Rate Limit Protection**\n"
        tutorial += f"Enable protection against accidental API bans:\n"
        tutorial += f"`{prefix}ratelimit on`\n"
        tutorial += f"This protects your account by detecting excessive activity and error messages.\n\n"
        
        tutorial += "**Step 9: Getting Help**\n"
        tutorial += f"If you need help with any feature, use:\n"
        tutorial += f"`{prefix}help <feature>` (e.g., `{prefix}help alias`)\n\n"
        
        tutorial += "**Recommended commands for beginners:**\n"
        tutorial += f"• `{prefix}help` - Show all available commands\n"
        tutorial += f"• `{prefix}helpcommands` - List your saved commands\n"
        tutorial += f"• `{prefix}search <term>` - Find commands\n"
        tutorial += f"• `{prefix}alias list` - Show your shortcuts\n"
        tutorial += f"• `{prefix}ratelimit` - Configure rate limit protection\n\n"
        
        tutorial += "Remember, you can always type `{prefix}help` to see all available commands!"
        
        return tutorial
    
    # Try to detect description from command response
    def try_detect_description(command_name, content):
        if not content:
            return
            
        descriptions = load_descriptions()
        if command_name in descriptions:
            return  # Already has description
            
        # Look for help text patterns
        help_match = re.search(rf"{command_name}\s*-\s*([^\n]+)", content)
        if help_match:
            desc = help_match.group(1).strip()
            if desc:
                descriptions[command_name] = desc
                save_descriptions(descriptions)
                return
                
        # Look for usage patterns
        usage_match = re.search(r"Usage:\s*[^\n]*\s+-\s+([^\n]+)", content)
        if usage_match:
            desc = usage_match.group(1).strip()
            if desc:
                descriptions[command_name] = desc
                save_descriptions(descriptions)
                return
    
    # Track last seen commands
    last_commands = {}
    
    # New help command
    @bot.command(name="help", description="Show help for all commands or a specific feature.")
    @handle_errors
    async def help_command(ctx, *, feature: str = None):
        await ctx.message.delete()
        
        # Handle special cases with parentheses and other special characters
        if feature:
            # Strip any special characters and parentheses
            feature = re.sub(r'[()]', '', feature.strip())
        
        # Generate help message based on the feature
        help_message = generate_help_message(feature)
        
        # Send as informative message with longer timeout
        await send_message(ctx, help_message, long_timeout=True)
    
    # Tutorial command
    @bot.command(name="tutorial", description="Show a beginner's guide to using this script.")
    @handle_errors
    async def tutorial_command(ctx):
        await ctx.message.delete()
        
        # Generate tutorial
        tutorial = generate_tutorial()
        
        # Send as informative message with longer timeout
        await send_message(ctx, tutorial, long_timeout=True)
    
    # Base command handlers
    @bot.command(name="helpcommands", description="List all saved commands.")
    @handle_errors
    async def help_commands(ctx):
        await ctx.message.delete()
        
        commands = load_commands()
        prefix = get_prefix()
        descriptions = load_descriptions()
        
        # Check for auto-validation
        auto_validate_commands()
        
        if not any(cmds for script, cmds in commands.items()):
            await send_message(ctx, f"No commands saved yet. Use `{prefix}savecommand` or run any command to automatically add it after validation.\n\nTip: Try `{prefix}tutorial` for a beginner's guide.")
            return
        
        # Format the commands by script
        formatted = "**📋 Command Viewer**\n\n"
        
        # Count total commands
        total_count = 0
        command_set = set()
        for script, cmds in commands.items():
            for cmd in cmds:
                command_set.add(cmd)
        total_count = len(command_set)
        
        formatted += f"Total Unique Commands: {total_count}\n"
        formatted += f"Current Prefix: `{prefix}`\n\n"
        
        # Show favorites first if they exist
        if "Favorites" in commands and commands["Favorites"]:
            formatted += f"**⭐ Favorites** ({len(commands['Favorites'])})\n"
            for cmd in sorted(commands["Favorites"]):
                desc = descriptions.get(cmd, "")
                if desc:
                    formatted += f"• `{prefix}{cmd}` - {desc}\n"
                else:
                    formatted += f"• `{prefix}{cmd}`\n"
            formatted += "\n"
            
        # Display commands by script
        for script, cmds in sorted(commands.items()):
            if script != "Favorites" and cmds:  # Only show scripts with commands
                formatted += f"**{script}** ({len(cmds)})\n"
                for cmd in sorted(cmds):
                    # Get description
                    desc = descriptions.get(cmd, "")
                    
                    # Check if command is in multiple categories
                    categories = find_command_categories(cmd)
                    if len(categories) > 1:
                        other_cats = [c for c in categories if c != script and c != "Favorites"]
                        if other_cats:
                            if desc:
                                formatted += f"• `{prefix}{cmd}` - {desc} (also in: {', '.join(other_cats)})\n"
                            else:
                                formatted += f"• `{prefix}{cmd}` (also in: {', '.join(other_cats)})\n"
                        else:
                            if desc:
                                formatted += f"• `{prefix}{cmd}` - {desc}\n"
                            else:
                                formatted += f"• `{prefix}{cmd}`\n"
                    else:
                        if desc:
                            formatted += f"• `{prefix}{cmd}` - {desc}\n"
                        else:
                            formatted += f"• `{prefix}{cmd}`\n"
                formatted += "\n"
        
        # Check if aliases exist
        aliases = load_aliases()
        if aliases:
            formatted += f"**🔄 Aliases** ({len(aliases)})\n"
            for alias, cmd in sorted(aliases.items()):
                formatted += f"• `{prefix}{alias}` → `{prefix}{cmd}`\n"
            formatted += "\n"
        
        # Add footer with help info
        formatted += "ℹ️ **Available Commands:**\n"
        formatted += f"• `{prefix}help` - Show comprehensive help\n"
        formatted += f"• `{prefix}savecommand <cmd1>, <cmd2>, ...` - Add commands manually\n"
        formatted += f"• `{prefix}delcommand <cmd>` - Remove a command\n"
        formatted += f"• `{prefix}adddesc <cmd> <description>` - Add description\n"
        formatted += f"• `{prefix}search <term>` - Search commands\n"
        formatted += f"• `{prefix}alias list` - View command aliases\n"
        formatted += f"• `{prefix}stats` - View usage statistics\n"
        formatted += f"• `{prefix}export` - Export your commands\n"
        formatted += f"• `{prefix}ratelimit` - Configure rate limit protection\n"
        formatted += f"• `{prefix}tutorial` - Show a beginner's guide\n"
        
        # This is a long informative message, use long timeout
        await send_message(ctx, formatted, long_timeout=True)
    
    @bot.command(name="savecommand", description="Save commands manually.")
    @handle_errors
    async def save_command(ctx, *, args: str = None):
        await ctx.message.delete()
        prefix = get_prefix()
        
        if not args:
            await send_message(ctx, f"**How to Save Commands**\n\nUsage: `{prefix}savecommand <cmd1>, <cmd2>, ...`\n\nExample: `{prefix}savecommand ping, avatar, serverinfo`\n\nTip: Commands are also saved automatically when you use them.")
            return
        
        # Parse comma-separated commands
        cmd_list = [cmd.strip() for cmd in args.split(",") if cmd.strip()]
        
        if not cmd_list:
            await send_message(ctx, "No valid commands provided. Please provide command names separated by commas.")
            return
        
        commands = load_commands()
        added = []
        updated = []
        skipped = []
        
        for cmd in cmd_list:
            # Skip if in rejected list
            pending_data = load_pending()
            if cmd in pending_data["rejected"]:
                skipped.append(f"{cmd} (previously rejected)")
                continue
                
            # Check if command exists in any category
            categories = find_command_categories(cmd)
            
            if not categories:
                # Command is new, add to a category
                category = identify_category_for_command(cmd)
                
                # Create category if needed
                if category not in commands:
                    commands[category] = []
                    
                commands[category].append(cmd)
                added.append(f"{cmd} → {category}")
            else:
                # Command exists, but might need to be moved to Manually Added
                if "Manually Added" not in categories:
                    if "Manually Added" not in commands:
                        commands["Manually Added"] = []
                    commands["Manually Added"].append(cmd)
                    updated.append(cmd)
        
        save_commands(commands)
        
        response = []
        if added:
            response.append(f"✅ Added {len(added)} new command(s): {', '.join(added)}")
        if updated:
            response.append(f"📝 Updated {len(updated)} existing command(s): {', '.join(updated)}")
        if skipped:
            response.append(f"⚠️ Skipped {len(skipped)} command(s): {', '.join(skipped)}")
        
        if response:
            response_text = "\n".join(response)
            response_text += f"\n\nTip: Add a description with `{prefix}adddesc <command> <description>`"
            await send_message(ctx, response_text)
        else:
            await send_message(ctx, "No changes made. All commands were already saved in the requested categories.")
    
    @bot.command(name="delcommand", description="Delete a saved command.")
    @handle_errors
    async def del_command(ctx, *, command_name: str):
        await ctx.message.delete()
        prefix = get_prefix()
        
        if not command_name:
            await send_message(ctx, f"Usage: `{prefix}delcommand <command_name>`")
            return
        
        command_name = command_name.strip()
        commands = load_commands()
        descriptions = load_descriptions()
        stats = load_stats()
        
        # Also check pending
        pending_data = load_pending()
        
        # Check aliases
        aliases = load_aliases()
        alias_to_remove = None
        for alias, cmd in aliases.items():
            if cmd == command_name:
                alias_to_remove = alias
                
        found = False
        # Check saved commands
        for script, cmds in list(commands.items()):
            if command_name in cmds:
                cmds.remove(command_name)
                found = True
                
                # Remove empty script categories (except special ones)
                if not cmds and script not in ["Manually Added", "Favorites"]:
                    commands.pop(script)
        
        # Check pending commands
        if command_name in pending_data["pending"]:
            pending_data["pending"].pop(command_name)
            found = True
            
        # Check rejected commands
        if command_name in pending_data["rejected"]:
            pending_data["rejected"].remove(command_name)
            found = True
            
        # Check groups
        groups = load_groups()
        for group_name, cmds in groups.items():
            if command_name in cmds:
                cmds.remove(command_name)
                found = True
        
        if found:
            save_commands(commands)
            save_pending(pending_data)
            save_groups(groups)
            
            # Remove description if it exists
            if command_name in descriptions:
                descriptions.pop(command_name)
                save_descriptions(descriptions)
                
            # Remove stats if they exist
            if command_name in stats["usage_counts"]:
                stats["usage_counts"].pop(command_name)
            if command_name in stats["last_used"]:
                stats["last_used"].pop(command_name)
            if command_name in stats["usage_history"]:
                stats["usage_history"].pop(command_name)
            save_stats(stats)
            
            # Remove aliases pointing to this command
            if alias_to_remove:
                aliases.pop(alias_to_remove)
                save_aliases(aliases)
                await send_message(ctx, f"Removed command `{prefix}{command_name}` from all categories and its alias `{prefix}{alias_to_remove}`.")
            else:
                await send_message(ctx, f"Removed command `{prefix}{command_name}` from all categories.")
        else:
            await send_message(ctx, f"Command `{prefix}{command_name}` not found in saved commands.")
    
    @bot.command(name="clearcommands", description="Clear all saved commands.")
    @handle_errors
    async def clear_commands(ctx):
        await ctx.message.delete()
        
        confirmation_msg = await ctx.send("Are you sure you want to clear all saved commands? Reply with 'yes' to confirm.")
        
        # Set a timeout for the confirmation message
        asyncio.create_task(auto_delete_message(confirmation_msg, LONG_TIMEOUT))
        
        # Listen for confirmation
        try:
            response_msg = await bot.wait_for(
                'message',
                check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() == 'yes',
                timeout=20.0
            )
            
            # Try to delete the confirmation message and response
            try:
                await confirmation_msg.delete()
                await response_msg.delete()
            except:
                pass  # Ignore errors if messages already deleted
            
            # Clear commands but keep structure
            save_commands({"Manually Added": [], "Favorites": []})
            save_descriptions({})
            save_stats({"usage_counts": {}, "last_used": {}, "usage_history": {}})
            save_pending({"pending": {}, "rejected": []})
            save_aliases({})
            save_groups({})
            save_templates({})
            
            await send_message(ctx, "All saved commands, descriptions, and stats have been cleared.")
            
        except asyncio.TimeoutError:  # Timeout
            try:
                await confirmation_msg.delete()
            except:
                pass
            await send_message(ctx, "Command clear cancelled.")
        except Exception as e:  # Other error
            try:
                await confirmation_msg.delete()
            except:
                pass
            await send_message(ctx, f"Error: {str(e)}")
    
    @bot.command(name="movecommand", description="Move a command to a different category.")
    @handle_errors
    async def move_command(ctx, *, args: str):
        await ctx.message.delete()
        prefix = get_prefix()
        
        # Parse arguments
        parts = args.split(None, 1)
        if len(parts) != 2:
            await send_message(ctx, f"Usage: `{prefix}movecommand <command_name> <category_name>`")
            return
            
        command_name, category = parts
        command_name = command_name.strip()
        category = category.strip()
        
        commands = load_commands()
        
        # Find categories command is in
        categories = find_command_categories(command_name)
        
        if not categories:
            await send_message(ctx, f"Command `{prefix}{command_name}` not found in any category.")
            return
            
        # Special handling for Favorites
        if category.lower() == "favorites":
            if "Favorites" not in commands:
                commands["Favorites"] = []
                
            if command_name not in commands["Favorites"]:
                commands["Favorites"].append(command_name)
                save_commands(commands)
                await send_message(ctx, f"Added command `{prefix}{command_name}` to Favorites.")
            else:
                await send_message(ctx, f"Command `{prefix}{command_name}` is already in Favorites.")
                
            return
            
        # Remove from all categories except Favorites
        for cat in categories:
            if cat != "Favorites" and command_name in commands[cat]:
                commands[cat].remove(command_name)
                
            # Remove empty categories (except special ones)
            if not commands[cat] and cat not in ["Manually Added", "Favorites"]:
                commands.pop(cat)
        
        # Add to new category
        if category not in commands:
            commands[category] = []
            
        commands[category].append(command_name)
        save_commands(commands)
        
        await send_message(ctx, f"Moved command `{prefix}{command_name}` to `{category}`.")
    
    @bot.command(name="setprefix", description="Set the prefix for command detection.")
    @handle_errors
    async def set_prefix(ctx, *, prefix: str):
        await ctx.message.delete()
        old_prefix = get_prefix()
        
        if not prefix:
            await send_message(ctx, f"Usage: `{old_prefix}setprefix <character>`")
            return
            
        # Get first character only
        new_prefix = prefix.strip()[0]
        
        # Update config
        updateConfigData(PREFIX_KEY, new_prefix)
        
        await send_message(ctx, f"Prefix changed from `{old_prefix}` to `{new_prefix}`.\nCommands will now be detected when they start with `{new_prefix}`.")
    
    @bot.command(name="adddesc", description="Add description to a command.")
    @handle_errors
    async def add_description(ctx, *, args: str):
        await ctx.message.delete()
        prefix = get_prefix()
        
        # Parse arguments
        parts = args.split(None, 1)
        if len(parts) != 2:
            await send_message(ctx, f"Usage: `{prefix}adddesc <command_name> <description>`")
            return
            
        command_name, description = parts
        command_name = command_name.strip()
        description = description.strip()
        
        # Validate command exists or is pending
        categories = find_command_categories(command_name)
        pending_data = load_pending()
        
        if not categories and command_name not in pending_data["pending"]:
            await send_message(ctx, f"Command `{prefix}{command_name}` not found. Save it first with `{prefix}savecommand`.")
            return
            
        # Save description
        descriptions = load_descriptions()
        descriptions[command_name] = description
        save_descriptions(descriptions)
        
        # If command is pending, validate it now
        if command_name in pending_data["pending"]:
            validate_pending_command(command_name)
            await send_message(ctx, f"Added description to `{prefix}{command_name}` and validated command:\n\"{description}\"")
        else:
            await send_message(ctx, f"Added description to `{prefix}{command_name}`:\n\"{description}\"")
    
    # Favorites commands
    @bot.command(name="favorite", description="Add a command to favorites.")
    @handle_errors
    async def favorite_command(ctx, *, command_name: str = None):
        await ctx.message.delete()
        prefix = get_prefix()
        
        commands = load_commands()
        
        # Ensure Favorites category exists
        if "Favorites" not in commands:
            commands["Favorites"] = []
        
        if not command_name:
            # List favorites
            if not commands["Favorites"]:
                await send_message(ctx, f"No favorite commands yet. Add with `{prefix}favorite <command>`")
                return
            
            formatted = "**⭐ Favorite Commands**\n\n"
            descriptions = load_descriptions()
            
            for cmd in sorted(commands["Favorites"]):
                desc = descriptions.get(cmd, "")
                if desc:
                    formatted += f"• `{prefix}{cmd}` - {desc}\n"
                else:
                    formatted += f"• `{prefix}{cmd}`\n"
            
            formatted += f"\nTip: Remove a favorite with `{prefix}unfavorite <command>`"
            await send_message(ctx, formatted, long_timeout=True)
            return
        
        command_name = command_name.strip()
        
        # Check if command exists in any category
        found = False
        for category, cmds in commands.items():
            if command_name in cmds:
                found = True
                break
        
        if not found:
            await send_message(ctx, f"Command `{prefix}{command_name}` not found. Save it first with `{prefix}savecommand`.")
            return
        
        # Add to favorites if not already there
        if command_name in commands["Favorites"]:
            await send_message(ctx, f"Command `{prefix}{command_name}` is already in favorites.")
        else:
            commands["Favorites"].append(command_name)
            save_commands(commands)
            await send_message(ctx, f"Added `{prefix}{command_name}` to favorites. Access with `{prefix}helpcommands`.")

    @bot.command(name="unfavorite", description="Remove a command from favorites.")
    @handle_errors
    async def unfavorite_command(ctx, *, command_name: str):
        await ctx.message.delete()
        prefix = get_prefix()
        
        if not command_name:
            await send_message(ctx, f"Usage: `{prefix}unfavorite <command_name>`")
            return
        
        command_name = command_name.strip()
        commands = load_commands()
        
        if "Favorites" not in commands:
            commands["Favorites"] = []
            save_commands(commands)
            await send_message(ctx, f"Command `{prefix}{command_name}` is not in favorites.")
            return
        
        if command_name in commands["Favorites"]:
            commands["Favorites"].remove(command_name)
            save_commands(commands)
            await send_message(ctx, f"Removed `{prefix}{command_name}` from favorites.")
        else:
            await send_message(ctx, f"Command `{prefix}{command_name}` is not in favorites.")
    
    @bot.command(name="search", description="Search for commands.")
    @handle_errors
    async def search_commands(ctx, *, search_term: str):
        await ctx.message.delete()
        prefix = get_prefix()
        
        if not search_term:
            await send_message(ctx, f"Usage: `{prefix}search <term>`")
            return
            
        search_term = search_term.lower().strip()
        
        # Load data
        commands = load_commands()
        descriptions = load_descriptions()
        pending_data = load_pending()
        aliases = load_aliases()
        
        # Collect all unique commands
        all_commands = set()
        for category, cmd_list in commands.items():
            all_commands.update(cmd_list)
            
        # Include pending commands
        pending_commands = set(pending_data["pending"].keys())
            
        # Search for matches
        matches = []
        
        # Search in confirmed commands
        for cmd in all_commands:
            # Check command name
            if search_term in cmd.lower():
                matches.append((cmd, "name", "confirmed"))
                continue
                
            # Check description
            desc = descriptions.get(cmd, "")
            if desc and search_term in desc.lower():
                matches.append((cmd, "description", "confirmed"))
        
        # Search in pending commands        
        for cmd in pending_commands:
            # Check command name
            if search_term in cmd.lower():
                matches.append((cmd, "name", "pending"))
                continue
                
            # Check description
            desc = descriptions.get(cmd, "")
            if desc and search_term in desc.lower():
                matches.append((cmd, "description", "pending"))
                
        # Search in aliases
        for alias, cmd in aliases.items():
            if search_term in alias.lower():
                matches.append((alias, "alias", "alias"))
                
        if not matches:
            await send_message(ctx, f"No commands found matching '{search_term}'.")
            return
            
        # Format results
        formatted = f"**🔍 Search Results for '{search_term}'**\n\n"
        
        # Group by match type and status
        confirmed_matches = [cmd for cmd, match_type, status in matches if status == "confirmed"]
        pending_matches = [cmd for cmd, match_type, status in matches if status == "pending"]
        alias_matches = [cmd for cmd, match_type, status in matches if status == "alias"]
        
        if confirmed_matches:
            formatted += "**Confirmed Commands:**\n"
            for cmd in sorted(confirmed_matches):
                # Get categories
                cats = find_command_categories(cmd)
                # Get description
                desc = descriptions.get(cmd, "")
                
                if desc:
                    formatted += f"• `{prefix}{cmd}` - {desc} ({', '.join(cats)})\n"
                else:
                    formatted += f"• `{prefix}{cmd}` ({', '.join(cats)})\n"
            formatted += "\n"
            
        if alias_matches:
            formatted += "**Aliases:**\n"
            for alias in sorted(alias_matches):
                cmd = aliases[alias]
                formatted += f"• `{prefix}{alias}` → `{prefix}{cmd}`\n"
            formatted += "\n"
            
        if pending_matches:
            formatted += "**Pending Commands:**\n"
            for cmd in sorted(pending_matches):
                # Get description
                desc = descriptions.get(cmd, "")
                # Get seen count
                seen_count = pending_data["pending"][cmd]["seen_count"]
                
                if desc:
                    formatted += f"• `{prefix}{cmd}` - {desc} (seen {seen_count} times)\n"
                else:
                    formatted += f"• `{prefix}{cmd}` (seen {seen_count} times)\n"
            formatted += "\n"
            
        # This is a longer, informative message
        await send_message(ctx, formatted, long_timeout=True)
        
    @bot.command(name="validate", description="Review and validate pending commands.")
    @handle_errors
    async def validate_commands(ctx, *, args: str = None):
        await ctx.message.delete()
        prefix = get_prefix()
        
        try:
            # Load pending commands
            pending_data = load_pending()
            
            # Handle no pending commands
            if not isinstance(pending_data, dict) or "pending" not in pending_data or not pending_data["pending"]:
                await send_message(ctx, "No commands waiting for validation.")
                return
            
            # Handle special validate operations
            if args:
                args = args.strip().lower()
                
                # Validate all pending commands at once
                if args == "all":
                    count = 0
                    for cmd_name in list(pending_data["pending"].keys()):
                        if validate_pending_command(cmd_name):
                            count += 1
                    
                    await send_message(ctx, f"✅ Successfully validated {count} pending commands.")
                    return
                
                # Clear/reject all pending commands
                elif args == "clear":
                    count = 0
                    for cmd_name in list(pending_data["pending"].keys()):
                        if reject_pending_command(cmd_name):
                            count += 1
                    
                    await send_message(ctx, f"🗑️ Rejected {count} pending commands.")
                    return
                
                # Validate specific commands with # notation
                elif '#' in args:
                    # Extract commands marked with # (e.g., #cmd1 #cmd2)
                    marked_commands = re.findall(r'#(\w+)', args)
                    
                    if not marked_commands:
                        await send_message(ctx, f"❌ No valid commands found. Use format: `{prefix}validate #cmd1 #cmd2`")
                        return
                    
                    valid_count = 0
                    invalid_count = 0
                    validated = []
                    not_found = []
                    
                    for cmd_name in marked_commands:
                        if cmd_name in pending_data["pending"]:
                            if validate_pending_command(cmd_name):
                                valid_count += 1
                                validated.append(cmd_name)
                        else:
                            invalid_count += 1
                            not_found.append(cmd_name)
                    
                    # Prepare response message
                    result = []
                    if valid_count > 0:
                        result.append(f"✅ Validated {valid_count} commands: {', '.join(validated)}")
                    if invalid_count > 0:
                        result.append(f"❌ Not found in pending: {', '.join(not_found)}")
                    
                    await send_message(ctx, "\n".join(result))
                    return
            
            # Default behavior: Format and display pending commands
            formatted = "**🔄 Pending Commands**\n\n"
            
            # Use a simple approach without sorting first - we'll sort later if needed
            pending_list = []
            
            # Convert to a simple list regardless of the original structure
            if isinstance(pending_data["pending"], dict):
                # If it's a dictionary, extract names and info
                for cmd_name, cmd_info in pending_data["pending"].items():
                    if isinstance(cmd_info, dict):
                        # Normal case - this is what we expect
                        seen_count = cmd_info.get("seen_count", 0)
                        timestamp = cmd_info.get("timestamp", 0)
                    else:
                        # Fallback if cmd_info isn't a dict
                        seen_count = 0
                        timestamp = 0
                    
                    pending_list.append({
                        "name": str(cmd_name),
                        "seen_count": seen_count,
                        "timestamp": timestamp
                    })
            elif isinstance(pending_data["pending"], list):
                # If it's already a list, extract items carefully
                for item in pending_data["pending"]:
                    if isinstance(item, dict) and "name" in item:
                        # If items are already in our expected format
                        pending_list.append(item)
                    elif isinstance(item, tuple) and len(item) >= 2:
                        # If items are in (name, info) format
                        name, info = item[0], item[1]
                        if isinstance(info, dict):
                            seen_count = info.get("seen_count", 0)
                            timestamp = info.get("timestamp", 0)
                        else:
                            seen_count = 0
                            timestamp = 0
                        
                        pending_list.append({
                            "name": str(name),
                            "seen_count": seen_count,
                            "timestamp": timestamp
                        })
            
            # If we didn't find any valid items
            if not pending_list:
                await send_message(ctx, "No valid commands waiting for validation.")
                return
            
            # Now sort our simplified list (no complex nested access)
            pending_list.sort(key=lambda x: x.get("seen_count", 0), reverse=True)
            
            # Generate output
            for cmd_info in pending_list:
                cmd_name = cmd_info["name"]
                seen_count = cmd_info.get("seen_count", 0)
                timestamp = cmd_info.get("timestamp", 0)
                last_seen = format_timestamp(timestamp) if timestamp else "unknown"
                desc = load_descriptions().get(cmd_name, "No description")
                
                formatted += f"• `{prefix}{cmd_name}` - Seen {seen_count} times, last used {last_seen}\n"
                formatted += f"  Description: {desc}\n"
                formatted += f"  Validate: `{prefix}savecommand {cmd_name}` | Reject: `{prefix}delcommand {cmd_name}`\n\n"
            
            # Add note about auto-validation
            formatted += "**Auto-Validation Rules:**\n"
            formatted += "• Commands are automatically validated after being seen 3+ times without errors\n"
            formatted += "• Commands seen 2+ times AND older than 3 days are also auto-validated\n\n"
            
            formatted += "**Quick Actions:**\n"
            formatted += f"• `{prefix}validate all` - Validate all pending commands\n"
            formatted += f"• `{prefix}validate clear` - Reject all pending commands\n"
            formatted += f"• `{prefix}validate #cmd1 #cmd2` - Validate specific commands\n\n"
            
            formatted += f"Currently pending: {len(pending_list)} command(s)\n"
            
            # This is an informative list, use longer timeout
            await send_message(ctx, formatted, long_timeout=True)
            
        except Exception as e:
            import traceback
            # Get full error traceback
            error_trace = traceback.format_exc()
            
            # Log the full error for debugging
            print(f"Error in validate command: {error_trace}", type_="ERROR")
            
            # Send a user-friendly error message
            error_msg = f"❌ **Error in validate command:**\n```\n{str(e)}\n```\n"
            error_msg += "Please report this error to the developer."
            await send_message(ctx, error_msg)

    # Command handling for aliases
    @bot.command(name="alias", description="Manage command aliases.")
    @handle_errors
    async def alias_command(ctx, *, args: str):
        await ctx.message.delete()
        prefix = get_prefix()
        
        if not args:
            await send_message(ctx, f"Usage:\n`{prefix}alias add <alias> <command>` - Create an alias\n`{prefix}alias remove <alias>` - Remove an alias\n`{prefix}alias list` - List all aliases")
            return
            
        parts = args.split(None, 1)
        subcommand = parts[0].lower()
        
        if subcommand == "list":
            # List all aliases
            aliases = load_aliases()
            
            if not aliases:
                await send_message(ctx, "No aliases defined yet.")
                return
                
            formatted = "**🔄 Command Aliases**\n\n"
            
            for alias, cmd in sorted(aliases.items()):
                desc = load_descriptions().get(cmd, "")
                if desc:
                    formatted += f"• `{prefix}{alias}` → `{prefix}{cmd}` - {desc}\n"
                else:
                    formatted += f"• `{prefix}{alias}` → `{prefix}{cmd}`\n"
                    
            await send_message(ctx, formatted, long_timeout=True)
            
        elif subcommand == "add" and len(parts) > 1:
            # Add new alias
            alias_args = parts[1].split(None, 1)
            
            if len(alias_args) != 2:
                await send_message(ctx, f"Usage: `{prefix}alias add <alias> <command>`")
                return
                
            alias_name = alias_args[0].strip()
            command_name = alias_args[1].strip()
            
            # Validate alias name
            if not re.match(r'^[a-zA-Z0-9_]+$', alias_name):
                await send_message(ctx, "Alias name must contain only letters, numbers, and underscores.")
                return
                
            # Prevent recursive aliases
            aliases = load_aliases()
            if command_name in aliases:
                await send_message(ctx, f"Cannot create alias to another alias. Target must be a real command.")
                return
                
            # Check if alias already exists
            if alias_name in aliases:
                await send_message(ctx, f"Alias `{alias_name}` already exists for command `{aliases[alias_name]}`. Remove it first.")
                return
                
            # Save the alias
            aliases[alias_name] = command_name
            save_aliases(aliases)
            
            await send_message(ctx, f"Created alias: `{prefix}{alias_name}` → `{prefix}{command_name}`")
            
        elif subcommand == "remove" and len(parts) > 1:
            # Remove alias
            alias_name = parts[1].strip()
            aliases = load_aliases()
            
            if alias_name in aliases:
                cmd = aliases.pop(alias_name)
                save_aliases(aliases)
                await send_message(ctx, f"Removed alias: `{prefix}{alias_name}` → `{prefix}{cmd}`")
            else:
                await send_message(ctx, f"Alias `{alias_name}` not found.")
                
        else:
            await send_message(ctx, f"Unknown subcommand. Usage:\n`{prefix}alias add <alias> <command>`\n`{prefix}alias remove <alias>`\n`{prefix}alias list`")
    
    # Command Usage Statistics
    @bot.command(name="stats", description="View command usage statistics.")
    @handle_errors
    async def command_stats(ctx, *, command_name: str = None):
        await ctx.message.delete()
        prefix = get_prefix()
        
        # Load stats
        stats = load_stats()
        
        if not stats["usage_counts"]:
            await send_message(ctx, "No command usage data available yet.")
            return
            
        if command_name:
            # Stats for specific command
            command_name = command_name.strip()
            
            if command_name not in stats["usage_counts"]:
                await send_message(ctx, f"No usage data for command `{prefix}{command_name}`.")
                return
                
            # Get command info
            usage_count = stats["usage_counts"].get(command_name, 0)
            last_used = stats["last_used"].get(command_name, 0)
            last_used_formatted = format_timestamp(last_used) if last_used else "never"
            history = stats["usage_history"].get(command_name, {})
            
            # Get description
            descriptions = load_descriptions()
            desc = descriptions.get(command_name, "No description")
            
            # Format response
            formatted = f"**📊 Stats for `{prefix}{command_name}`**\n\n"
            formatted += f"Description: {desc}\n"
            formatted += f"Usage Count: {usage_count}\n"
            formatted += f"Last Used: {last_used_formatted}\n\n"
            
            # Show usage history if available
            if history:
                formatted += "**Usage History (Last 30 Days):**\n"
                
                # Sort by date
                history_sorted = sorted(history.items())
                
                # Generate simplified chart
                chart = ""
                for date, count in history_sorted[-7:]:  # Last 7 days
                    chart += f"{date[-5:]}: {'■' * min(count, 20)} ({count})\n"
                    
                formatted += f"```\n{chart}```\n"
                
            # Find related commands
            # This is a simple implementation - a real one would use more sophisticated analysis
            related = []
            for cmd, count in stats["usage_counts"].items():
                if cmd != command_name and cmd.startswith(command_name[:3]):
                    related.append((cmd, count))
                    
            if related:
                formatted += "**Related Commands:**\n"
                for cmd, count in sorted(related, key=lambda x: x[1], reverse=True)[:3]:
                    formatted += f"• `{prefix}{cmd}` (used {count} times)\n"
                    
            await send_message(ctx, formatted, long_timeout=True)
            
        else:
            # Overall stats
            formatted = "**📊 Command Usage Statistics**\n\n"
            
            # Total usage
            total_usage = sum(stats["usage_counts"].values())
            unique_commands = len(stats["usage_counts"])
            
            formatted += f"Total Command Usage: {total_usage}\n"
            formatted += f"Unique Commands Used: {unique_commands}\n\n"
            
            # Top commands
            formatted += "**Most Used Commands:**\n"
            
            # Sort by usage count
            top_commands = sorted(
                stats["usage_counts"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:8]  # Top 8
            
            # Generate chart
            chart_data = {cmd: count for cmd, count in top_commands}
            chart = generate_bar_chart(chart_data)
            
            formatted += f"```\n{chart}\n```\n"
            
            # Recent activity
            formatted += "**Recent Activity:**\n"
            
            # Get most recently used commands
            recent_commands = sorted(
                stats["last_used"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5
            
            for cmd, timestamp in recent_commands:
                formatted += f"• `{prefix}{cmd}` - {format_timestamp(timestamp)}\n"
                
            await send_message(ctx, formatted, long_timeout=True)
     
    # Command Export/Import System
    @bot.command(name="export", description="Export commands as a shareable code.")
    @handle_errors
    async def export_commands(ctx, *, category: str = None):
        await ctx.message.delete()
        prefix = get_prefix()
        
        # Load data
        commands = load_commands()
        descriptions = load_descriptions()
        
        if not any(cmds for script, cmds in commands.items()):
            await send_message(ctx, "No commands to export.")
            return
            
        # Prepare export data
        export_data = {
            "version": 1,
            "commands": {},
            "descriptions": {}
        }
        
        if category:
            # Export specific category
            category = category.strip()
            if category not in commands or not commands[category]:
                await send_message(ctx, f"Category '{category}' not found or empty.")
                return
                
            # Add commands from the specified category
            export_data["commands"] = {category: commands[category]}
            
            # Add descriptions for those commands
            for cmd in commands[category]:
                if cmd in descriptions:
                    export_data["descriptions"][cmd] = descriptions[cmd]
                    
            export_code = generate_export_code(export_data)
            
            await send_message(ctx, f"**Export Code for Category '{category}'**\n```\n{export_code}\n```\nShare this code with others or save it for backup.\nTo import: `{prefix}import <code>`", long_timeout=True)
            
        else:
            # Export all commands
            export_data["commands"] = commands
            export_data["descriptions"] = descriptions
            
            export_code = generate_export_code(export_data)
            
            await send_message(ctx, f"**Export Code for All Commands**\n```\n{export_code}\n```\nShare this code with others or save it for backup.\nTo import: `{prefix}import <code>`", long_timeout=True)
    
    @bot.command(name="import", description="Import commands from an export code.")
    @handle_errors
    async def import_commands(ctx, *, code: str):
        await ctx.message.delete()
        prefix = get_prefix()
        
        if not code:
            await send_message(ctx, f"Usage: `{prefix}import <code>`")
            return
            
        # Parse the code
        import_data = parse_export_code(code.strip())
        
        if not import_data:
            await send_message(ctx, "Invalid import code. Please check the code and try again.")
            return
            
        # Validate import data format
        if "version" not in import_data or "commands" not in import_data:
            await send_message(ctx, "Invalid import data format.")
            return
            
        # Load current data
        current_commands = load_commands()
        current_descriptions = load_descriptions()
        
        # Track changes
        added_commands = 0
        updated_commands = 0
        added_categories = 0
        
        # Merge commands
        for category, cmds in import_data["commands"].items():
            if category not in current_commands:
                current_commands[category] = []
                added_categories += 1
                
            for cmd in cmds:
                if cmd not in current_commands[category]:
                    current_commands[category].append(cmd)
                    added_commands += 1
                    
        # Merge descriptions
        for cmd, desc in import_data.get("descriptions", {}).items():
            if cmd not in current_descriptions:
                current_descriptions[cmd] = desc
                updated_commands += 1
                
        # Save changes
        save_commands(current_commands)
        save_descriptions(current_descriptions)
        
        # Report results
        result = f"Import complete: {added_commands} commands added, {updated_commands} descriptions updated"
        if added_categories > 0:
            result += f", {added_categories} new categories created"
            
        await send_message(ctx, result)
    
    # Command Groups System
    @bot.command(name="group", description="Manage command groups.")
    @handle_errors
    async def group_command(ctx, *, args: str):
        await ctx.message.delete()
        prefix = get_prefix()
        
        if not args:
            await send_message(ctx, f"Usage:\n`{prefix}group create <name> <cmd1> <cmd2> ...` - Create a group\n`{prefix}group add <name> <cmd>` - Add to group\n`{prefix}group remove <name> <cmd>` - Remove from group\n`{prefix}group run <name>` - Run all commands in group\n`{prefix}group list` - List all groups")
            return
            
        parts = args.split(None, 1)
        subcommand = parts[0].lower()
        
        if subcommand == "list":
            # List all groups
            groups = load_groups()
            
            if not groups:
                await send_message(ctx, "No command groups defined yet.")
                return
                
            formatted = "**👥 Command Groups**\n\n"
            
            for name, cmds in sorted(groups.items()):
                formatted += f"**{name}** ({len(cmds)} commands)\n"
                for cmd in sorted(cmds):
                    desc = load_descriptions().get(cmd, "")
                    if desc:
                        formatted += f"• `{prefix}{cmd}` - {desc}\n"
                    else:
                        formatted += f"• `{prefix}{cmd}`\n"
                formatted += "\n"
                    
            await send_message(ctx, formatted, long_timeout=True)
            
        elif subcommand == "create" and len(parts) > 1:
            # Create new group
            group_args = parts[1].split(None, 1)
            
            if len(group_args) != 2:
                await send_message(ctx, f"Usage: `{prefix}group create <name> <cmd1> <cmd2> ...`")
                return
                
            group_name = group_args[0].strip()
            commands_str = group_args[1].strip()
            
            # Parse command list
            cmd_list = [cmd.strip() for cmd in commands_str.split() if cmd.strip()]
            
            if not cmd_list:
                await send_message(ctx, "No valid commands provided for the group.")
                return
                
            # Create or update group
            groups = load_groups()
            groups[group_name] = cmd_list
            save_groups(groups)
            
            await send_message(ctx, f"Created command group '{group_name}' with {len(cmd_list)} commands.")
            
        elif subcommand == "add" and len(parts) > 1:
            # Add command to group
            group_args = parts[1].split(None, 1)
            
            if len(group_args) != 2:
                await send_message(ctx, f"Usage: `{prefix}group add <name> <command>`")
                return
                
            group_name = group_args[0].strip()
            command_name = group_args[1].strip()
            
            # Check if group exists
            groups = load_groups()
            if group_name not in groups:
                await send_message(ctx, f"Group '{group_name}' not found.")
                return
                
            # Add command to group
            if command_name not in groups[group_name]:
                groups[group_name].append(command_name)
                save_groups(groups)
                await send_message(ctx, f"Added command `{prefix}{command_name}` to group '{group_name}'.")
            else:
                await send_message(ctx, f"Command `{prefix}{command_name}` is already in group '{group_name}'.")
                
        elif subcommand == "remove" and len(parts) > 1:
            # Remove command from group
            group_args = parts[1].split(None, 1)
            
            if len(group_args) != 2:
                await send_message(ctx, f"Usage: `{prefix}group remove <name> <command>`")
                return
                
            group_name = group_args[0].strip()
            command_name = group_args[1].strip()
            
            # Check if group exists
            groups = load_groups()
            if group_name not in groups:
                await send_message(ctx, f"Group '{group_name}' not found.")
                return
                
            # Remove command from group
            if command_name in groups[group_name]:
                groups[group_name].remove(command_name)
                
                # Remove empty group
                if not groups[group_name]:
                    groups.pop(group_name)
                    
                save_groups(groups)
                await send_message(ctx, f"Removed command `{prefix}{command_name}` from group '{group_name}'.")
            else:
                await send_message(ctx, f"Command `{prefix}{command_name}` not found in group '{group_name}'.")
                
        elif subcommand == "run" and len(parts) > 1:
            # Run all commands in a group
            group_name = parts[1].strip()
            
            # Check if group exists
            groups = load_groups()
            if group_name not in groups or not groups[group_name]:
                await send_message(ctx, f"Group '{group_name}' not found or empty.")
                return
                
            # Run each command
            prefix = get_prefix()
            cmd_count = len(groups[group_name])
            
            await send_message(ctx, f"Running {cmd_count} commands from group '{group_name}'...")
            
            # For each command in the group
            for cmd in groups[group_name]:
                try:
                    # Create and send the command message
                    await ctx.send(f"{prefix}{cmd}")
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(1)
                except Exception as e:
                    await send_message(ctx, f"Error running command `{prefix}{cmd}`: {str(e)}")
                    
            await send_message(ctx, f"Finished running {cmd_count} commands from group '{group_name}'.")
                
        else:
            await send_message(ctx, f"Unknown subcommand. Usage:\n`{prefix}group create <name> <cmd1> <cmd2> ...`\n`{prefix}group add <name> <cmd>`\n`{prefix}group remove <name> <cmd>`\n`{prefix}group run <name>`\n`{prefix}group list`")
    
    # Command Templates System
    @bot.command(name="template", description="Manage command templates.")
    @handle_errors
    async def template_command(ctx, *, args: str):
        await ctx.message.delete()
        prefix = get_prefix()
        
        if not args:
            await send_message(ctx, f"Usage:\n`{prefix}template create <name> <template>` - Create a template\n`{prefix}template use <name> <params>` - Use a template\n`{prefix}template list` - List all templates")
            return
            
        parts = args.split(None, 1)
        subcommand = parts[0].lower()
        
        if subcommand == "list":
            # List all templates
            templates = load_templates()
            
            if not templates:
                await send_message(ctx, "No command templates defined yet.")
                return
                
            formatted = "**📝 Command Templates**\n\n"
            
            for name, template in sorted(templates.items()):
                formatted += f"**{name}**\n"
                formatted += f"Template: `{template}`\n"
                
                # Extract parameters
                params = re.findall(r"{([^{}]+)}", template)
                if params:
                    formatted += "Parameters: " + ", ".join(f"`{p}`" for p in params) + "\n"
                    
                formatted += f"Usage: `{prefix}template use {name} param1=\"value1\" param2=\"value2\"`\n\n"
                    
            await send_message(ctx, formatted, long_timeout=True)
            
        elif subcommand == "create" and len(parts) > 1:
            # Create new template
            template_args = parts[1].split(None, 1)
            
            if len(template_args) != 2:
                await send_message(ctx, f"Usage: `{prefix}template create <name> <template>`")
                return
                
            template_name = template_args[0].strip()
            template_text = template_args[1].strip()
            
            # Check if template has valid placeholders
            placeholders = re.findall(r"{([^{}]+)}", template_text)
            if not placeholders:
                await send_message(ctx, "Template must contain at least one parameter in {param} format.")
                return
                
            # Save template
            templates = load_templates()
            templates[template_name] = template_text
            save_templates(templates)
            
            formatted = f"Created template '{template_name}':\n`{template_text}`\n\n"
            formatted += "Parameters: " + ", ".join(f"`{p}`" for p in placeholders) + "\n"
            formatted += f"Usage: `{prefix}template use {template_name} " + " ".join(f'{p}="value"' for p in placeholders) + "`"
            
            await send_message(ctx, formatted)
            
        elif subcommand == "use" and len(parts) > 1:
            # Use a template
            template_args = parts[1].split(None, 1)
            
            if len(template_args) < 1:
                await send_message(ctx, f"Usage: `{prefix}template use <name> <params>`")
                return
                
            template_name = template_args[0].strip()
            params_text = template_args[1].strip() if len(template_args) > 1 else ""
            
            # Check if template exists
            templates = load_templates()
            if template_name not in templates:
                await send_message(ctx, f"Template '{template_name}' not found.")
                return
                
            # Process template
            template_text = templates[template_name]
            processed = process_template(template_text, params_text)
            
            if processed is None:
                # Find missing parameters
                required_params = re.findall(r"{([^{}]+)}", template_text)
                provided_params = re.findall(r'(\w+)="([^"]*)"', params_text)
                provided_keys = [p[0] for p in provided_params]
                
                missing = [p for p in required_params if p not in provided_keys]
                
                await send_message(ctx, f"Missing parameters: {', '.join(missing)}\nUsage: `{prefix}template use {template_name} " + " ".join(f'{p}="value"' for p in required_params) + "`")
                return
                
            # Execute the processed command
            prefix_char = get_prefix()
            await ctx.send(f"{prefix_char}{processed}")
            
        else:
            await send_message(ctx, f"Unknown subcommand. Usage:\n`{prefix}template create <name> <template>`\n`{prefix}template use <name> <params>`\n`{prefix}template list`")
            
    # Command Suggestion System
    @bot.command(name="suggest", description="Get command suggestions based on usage patterns.")
    @handle_errors
    async def suggest_commands(ctx):
        await ctx.message.delete()
        prefix = get_prefix()
        
        # Generate suggestions
        suggestions = generate_suggestions()
        
        if not suggestions:
            await send_message(ctx, "No suggestions available yet. Use more commands to get personalized suggestions.")
            return
            
        # Format suggestions
        formatted = "**💡 Command Suggestions**\n\n"
        
        # Group by suggestion type
        alias_suggestions = [s for s in suggestions if s["type"] == "alias"]
        category_suggestions = [s for s in suggestions if s["type"] == "category"]
        
        if alias_suggestions:
            formatted += "**Suggested Aliases:**\n"
            for suggestion in alias_suggestions[:3]:  # Limit to 3
                cmd = suggestion["command"]
                alias = suggestion["suggestion"]
                formatted += f"• Create alias `{prefix}{alias}` for `{prefix}{cmd}`\n"
                formatted += f"  Command: `{prefix}alias add {alias} {cmd}`\n"
            formatted += "\n"
            
        if category_suggestions:
            formatted += "**Category Suggestions:**\n"
            for suggestion in category_suggestions[:3]:  # Limit to 3
                cmd = suggestion["command"]
                category = suggestion["suggestion"]
                formatted += f"• Move `{prefix}{cmd}` to '{category}' category\n"
                formatted += f"  Command: `{prefix}movecommand {cmd} {category}`\n"
            formatted += "\n"
            
        # Add footer
        formatted += "These suggestions are based on your command usage patterns."
        
        await send_message(ctx, formatted, long_timeout=True)
        
    # Command Documentation Generator
    @bot.command(name="docs", description="Generate command documentation.")
    @handle_errors
    async def generate_docs(ctx, *, format_type: str = "plain"):
        await ctx.message.delete()
        prefix = get_prefix()
        
        format_type = format_type.strip().lower()
        
        if format_type not in ["plain", "markdown"]:
            await send_message(ctx, f"Unsupported format type. Use 'plain' or 'markdown'.")
            return
            
        # Generate documentation
        docs = generate_documentation(format_type)
        
        if format_type == "markdown":
            # For markdown, provide a preview
            preview = docs[:500] + "...\n\n[Documentation truncated for preview]"
            await send_message(ctx, f"**Generated Markdown Documentation Preview:**\n```md\n{preview}\n```\n\nThe full documentation is too long to display here.", long_timeout=True)
        else:
            # For plain text, send as is (with length limit)
            if len(docs) > 1950:  # Discord message limit with some buffer
                docs = docs[:1950] + "...\n\n[Documentation truncated]"
                
            await send_message(ctx, docs, long_timeout=True)

    # Rate limit protection commands
    @bot.command(name="ratelimit", description="Configure rate limit protection.")
    @handle_errors
    async def rate_limit_command(ctx, *, args: str = None):
        await ctx.message.delete()
        prefix = get_prefix()
        
        if not args:
            # Show current status
            enabled = RATE_MONITOR["enabled"]
            thresholds = getConfigData().get(RATE_MONITOR_THRESHOLD_KEY)
            
            formatted = "**⚡ Rate Limit Protection**\n\n"
            formatted += f"Status: {'✅ Enabled' if enabled else '❌ Disabled'}\n\n"
            
            formatted += "**Current Thresholds:**\n"
            for key, value in thresholds.items():
                formatted += f"• {key}: {value}\n"
            
            formatted += f"\n**Current Usage:**\n"
            formatted += f"• Messages: {RATE_MONITOR['message_count']}/{thresholds['messages_per_minute']}\n"
            formatted += f"• Commands: {RATE_MONITOR['command_count']}/{thresholds['commands_per_minute']}\n"
            
            formatted += f"\n**Error Detection:**\n"
            formatted += f"• Error patterns: {len(RATE_MONITOR['error_patterns'])}\n"
            formatted += f"• Server threshold: {RATE_MONITOR['unique_servers_threshold']} servers\n"
            formatted += f"• Similar message threshold: {RATE_MONITOR['similar_content_threshold']} messages\n"
            
            formatted += f"\n**Commands:**\n"
            formatted += f"• `{prefix}ratelimit on` - Enable protection\n"
            formatted += f"• `{prefix}ratelimit off` - Disable protection\n"
            formatted += f"• `{prefix}ratelimit threshold <type> <value>` - Set threshold\n"
            formatted += f"• `{prefix}ratelimit servers <num>` - Set server threshold\n"
            formatted += f"• `{prefix}ratelimit pattern add <pattern>` - Add error pattern\n"
            formatted += f"• `{prefix}ratelimit pattern list` - List error patterns\n"
            formatted += f"• `{prefix}ratelogs` - View rate limit event logs\n"
            
            await send_message(ctx, formatted, long_timeout=True)
            return
        
        parts = args.strip().split(None, 1)
        subcommand = parts[0].lower()
        
        if subcommand == "on":
            RATE_MONITOR["enabled"] = True
            updateConfigData(RATE_LIMIT_ENABLED_KEY, True)
            await send_message(ctx, "✅ Rate limit protection enabled.")
            
        elif subcommand == "off":
            RATE_MONITOR["enabled"] = False
            updateConfigData(RATE_LIMIT_ENABLED_KEY, False)
            await send_message(ctx, "❌ Rate limit protection disabled.")
            
        elif subcommand == "threshold" and len(parts) > 1:
            # Parse threshold settings
            threshold_args = parts[1].strip().split(None, 1)
            
            if len(threshold_args) != 2:
                await send_message(ctx, f"Usage: `{prefix}ratelimit threshold <type> <value>`\nValid types: messages_per_minute, commands_per_minute, api_calls_per_minute")
                return
                
            threshold_type = threshold_args[0].strip()
            try:
                threshold_value = int(threshold_args[1].strip())
            except ValueError:
                await send_message(ctx, "Threshold value must be a number.")
                return
                
            thresholds = getConfigData().get(RATE_MONITOR_THRESHOLD_KEY)
            
            if threshold_type not in thresholds:
                await send_message(ctx, f"Invalid threshold type. Valid types: {', '.join(thresholds.keys())}")
                return
                
            thresholds[threshold_type] = threshold_value
            updateConfigData(RATE_MONITOR_THRESHOLD_KEY, thresholds)
            
            await send_message(ctx, f"✅ {threshold_type} threshold set to {threshold_value}")
            
        elif subcommand == "servers" and len(parts) > 1:
            try:
                value = int(parts[1].strip())
                if value < 1:
                    await send_message(ctx, "❌ Value must be at least 1.")
                    return
                    
                RATE_MONITOR["unique_servers_threshold"] = value
                await send_message(ctx, f"✅ Set max server threshold to {value}")
            except ValueError:
                await send_message(ctx, "❌ Value must be a number.")
        
        elif subcommand == "pattern" and len(parts) > 1:
            pattern_args = parts[1].strip().split(None, 1)
            pattern_cmd = pattern_args[0].lower()
            
            if pattern_cmd == "list":
                # List current error patterns
                formatted = "**Error Detection Patterns:**\n\n"
                for i, pattern in enumerate(RATE_MONITOR["error_patterns"], 1):
                    formatted += f"{i}. `{pattern}`\n"
                    
                formatted += f"\nAdd new patterns with: `{prefix}ratelimit pattern add <regex_pattern>`"
                await send_message(ctx, formatted, long_timeout=True)
                
            elif pattern_cmd == "add" and len(pattern_args) > 1:
                # Add new error pattern
                new_pattern = pattern_args[1].strip()
                
                # Validate regex pattern
                try:
                    re.compile(new_pattern)
                    RATE_MONITOR["error_patterns"].append(new_pattern)
                    await send_message(ctx, f"✅ Added error pattern: `{new_pattern}`")
                except re.error:
                    await send_message(ctx, f"❌ Invalid regex pattern. Please check your syntax.")
                    
        else:
            await send_message(ctx, f"Unknown subcommand. Use `{prefix}ratelimit` for help.")
    
    @bot.command(name="ratelogs", description="View recent rate limit events.")
    @handle_errors
    async def rate_logs_command(ctx):
        await ctx.message.delete()
        
        if not LOG_FILE.exists():
            await send_message(ctx, "No rate limit logs found.")
            return
        
        # Read last 10 events (or fewer if file is smaller)
        with open(LOG_FILE, "r") as f:
            logs = f.read()
        
        # Format for Discord
        formatted = "**📊 Recent Rate Limit Events**\n\n"
        
        # If logs are too long, show most recent events
        if len(logs) > 1900:
            logs = "...[older logs truncated]...\n" + logs[-1900:]
            formatted += f"```\n{logs}\n```"
        else:
            formatted += f"```\n{logs}\n```"
        
        formatted += f"\nLog file location: `{LOG_FILE}`"
        
        await send_message(ctx, formatted, long_timeout=True)
    
    @bot.command(name="emergency", description="Delete recent messages and restart immediately.")
    @handle_errors
    async def emergency_command(ctx):
        await ctx.message.delete()
        
        # Set restart triggered flag
        RATE_MONITOR["restart_triggered"] = True
        
        # Send confirmation
        msg = await ctx.send("🚨 **EMERGENCY MODE ACTIVATED!** sorry for the spam ima go touch grass")
        
        # Log the event
        await log_rate_limit_event("Manual emergency activation", "User triggered emergency restart")
        
        # Run emergency message analysis and deletion
        deleted_count = await emergency_message_analysis()
        
        # Add brief delay so user can see confirmation
        await asyncio.sleep(2)
        
        # Execute restart
        await restart_bot()
    
    # Track messages for rate limit detection
    @bot.listen("on_message")
    async def track_message_rate(message):
        if not RATE_MONITOR["enabled"] or message.author.id != bot.user.id:
            return
        
        # Increment message counter
        RATE_MONITOR["message_count"] += 1
        current_time = time.time()
        
        # Store message data (limited history)
        RATE_MONITOR["recent_messages"].append({
            "content": message.content,
            "server_id": message.guild.id if message.guild else None,
            "channel_id": message.channel.id,
            "message_id": message.id,
            "timestamp": current_time
        })
        
        # Keep only messages from last 30 seconds
        RATE_MONITOR["recent_messages"] = [
            m for m in RATE_MONITOR["recent_messages"] 
            if current_time - m["timestamp"] < 30
        ]
        
        # Update server activity counter
        if message.guild:
            server_id = str(message.guild.id)
            if server_id not in RATE_MONITOR["server_activity"]:
                RATE_MONITOR["server_activity"] = {}
                RATE_MONITOR["server_activity"][server_id] = []
            
            RATE_MONITOR["server_activity"][server_id].append(current_time)
            
            # Keep only recent activity
            RATE_MONITOR["server_activity"][server_id] = [
                t for t in RATE_MONITOR["server_activity"][server_id] 
                if current_time - t < 60
            ]
        
        # Check rate limits after updating counters
        await check_rate_limits(message.channel)

    # Auto-save any commands used with the configured prefix
    @bot.listen("on_message")
    async def auto_detect_commands(message):
        # Only track user's own messages
        if message.author.id != bot.user.id:
            return
        
        # Get current prefix
        prefix = get_prefix()
        
        # Check if the message starts with the configured prefix
        if not message.content.startswith(prefix):
            return
            
        # Extract the command name and full command
        match = re.match(f'^\\{prefix}(\\w+)(.*)', message.content)
        if not match:
            return
            
        command_name = match.group(1).lower()
        full_command = command_name + match.group(2)
        
        # Save the full command example
        add_command_example(command_name, full_command)
        
        # Check if it's an alias
        aliases = load_aliases()
        if command_name in aliases:
            target_command = aliases[command_name]
            # Track usage for the target command
            track_command_usage(target_command)
            return
        
        # Skip our own commands from this script
        if command_name in OWN_COMMANDS:
            return
            
        # Record the command and timestamp
        last_commands[command_name] = {
            "timestamp": time.time(),
            "channel_id": message.channel.id,
            "message_id": message.id,
            "full_command": full_command
        }
        
        # Check if command exists in confirmed list
        categories = find_command_categories(command_name)
        if categories:
            # Track usage for confirmed commands
            track_command_usage(command_name)
            return
            
        # Check if command is in rejected list
        pending_data = load_pending()
        if command_name in pending_data["rejected"]:
            return
            
        # Add to pending list
        add_command_to_pending(command_name)
    
    # Listen for responses to check for command validation
    @bot.listen("on_message")
    async def validate_command_responses(message):
        # Need a slight delay to make sure this is a response
        await asyncio.sleep(0.5)
        
        current_time = time.time()
        
        # Process each recent command
        for command_name, data in list(last_commands.items()):
            # Only process commands within the last 5 seconds
            if current_time - data["timestamp"] > 5:
                last_commands.pop(command_name)
                continue
                
            # Check if this message seems like a response to the command
            if message.channel.id == data["channel_id"] and message.id != data["message_id"]:
                # Process the command for validation
                await process_command_validation(message, command_name)
                
    # Command aliases handling
    @bot.listen("on_message")
    async def handle_aliases(message):
        # Only handle user's own messages
        if message.author.id != bot.user.id:
            return
            
        # Get current prefix
        prefix = get_prefix()
        
        # Check if the message starts with the configured prefix
        if not message.content.startswith(prefix):
            return
            
        # Extract the command name
        match = re.match(f'^\\{prefix}(\\w+)(.*)', message.content)
        if not match:
            return
            
        command_name = match.group(1).lower()
        args = match.group(2)
        
        # Skip if not an alias
        aliases = load_aliases()
        if command_name not in aliases:
            return
            
        # Get the target command
        target_command = aliases[command_name]
        
        # Delete the original message
        try:
            await message.delete()
        except:
            pass
            
        # Send the expanded command
        await message.channel.send(f"{prefix}{target_command}{args}")
    
command_viewer()  # Call to activate!

#CONGRATS you made it through all the lines!!! that or u just skipped through BORING!
#But ello there! anyways thanks for downloading
#reason for this script was because i see users try using the old features .help well that brings it back into action
#providing extensive commands and possibilites already there to have at play!