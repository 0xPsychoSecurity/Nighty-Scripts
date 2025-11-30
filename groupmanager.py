@nightyScript(
    name="Group Chat Manager",
    author="Krispcode",
    description="Manage Discord group chats with nojoin, noleave, and lockdown features",
    usage="<p>gm <subcommand> [args] - See <p>gm help for details"
)
def script_function():
    """
    GROUP CHAT MANAGER
    ------------------

    A comprehensive tool for managing Discord group chats (group DMs) with advanced control features.
    Allows you to prevent users from joining/leaving and implement lockdown mode.

    COMMANDS:
    <p>gm nojoin <user_id> - Prevent a user from joining this group chat
    <p>gm noleave <user_id> - Prevent a user from leaving this group chat
    <p>gm allowjoin <user_id> - Remove user from nojoin list
    <p>gm allowleave <user_id> - Remove user from noleave list
    <p>gm lockdown - Enable lockdown mode
    <p>gm unlock - Disable lockdown mode
    <p>gm whitelist <user_id> - Add user to lockdown whitelist (authorized users)
    <p>gm unwhitelist <user_id> - Remove user from lockdown whitelist
    <p>gm status - Show current group chat management status
    <p>gm clear nojoin - Clear all nojoin restrictions
    <p>gm clear noleave - Clear all noleave restrictions
    <p>gm help - Show detailed help information

    EXAMPLES:
    <p>gm nojoin 123456789012345678 - Prevent user from joining (by ID)
    <p>gm nojoin @username - Prevent user from joining (by mention)
    <p>gm nojoin username - Prevent user from joining (by username)
    <p>gm allowjoin 123456789012345678 - Remove user from nojoin list
    <p>gm lockdown - Enable lockdown mode
    <p>gm status - Check current restrictions
    <p>gm whitelist @someone - Add user to lockdown whitelist

    NOTES:
    - Only works in Discord group chats (group DMs), not servers
    - All restrictions are group chat specific (not global)
    - Lockdown prevents new users from joining unless they're whitelisted
    - Lockdown also prevents whitelisted users from leaving
    - Lockdown auto-generates whitelist from current members
    - During lockdown, nojoin/noleave lists are disabled
    - Data is stored in JSON files for persistence
    - Use user IDs, usernames, or mentions - works even if user isn't in the group chat
    - Enhanced error handling alerts users to permission issues and failures
    """
    
    import json
    from pathlib import Path
    import asyncio
    
    # JSON file setup
    BASE_DIR = Path(getScriptsPath()) / "json"
    GC_DATA_FILE = BASE_DIR / "gc_manager_data.json"
    
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    def script_log(message, level="INFO"):
        """Log messages with script context."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [GC Manager] [{level}] {message}", type_=level)
    
    async def send_embed_safely(channel_id, title, description):
        """
        Sends an embed while temporarily disabling private mode.
        Automatically restores the original private mode setting afterward.
        """
        # Save the current private mode setting
        current_private = getConfigData().get("private")
        
        # Temporarily disable private mode
        updateConfigData("private", False)
        
        try:
            # Send the embed
            await forwardEmbedMethod(
                channel_id=channel_id,
                title=title,
                content=description
            )
        except Exception as e:
            script_log(f"Failed to send embed: {e}", level="ERROR")
        finally:
            # ALWAYS restore the original private setting
            updateConfigData("private", current_private)
    
    def load_gc_data():
        """Load group chat management data from JSON file."""
        try:
            if not GC_DATA_FILE.exists():
                default_data = {
                    "group_chats": {}
                }
                with open(GC_DATA_FILE, "w") as f:
                    json.dump(default_data, f, indent=4)
                return default_data
            
            with open(GC_DATA_FILE, "r") as f:
                data = json.load(f)
                # Migrate old "allow_list" to "whitelist" if needed
                for channel_id, gc_data in data.get("group_chats", {}).items():
                    if "allow_list" in gc_data and "whitelist" not in gc_data:
                        gc_data["whitelist"] = gc_data.pop("allow_list")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            script_log(f"Error loading GC data: {e}", level="ERROR")
            return {"group_chats": {}}
    
    def save_gc_data(data):
        """Save group chat management data to JSON file."""
        try:
            with open(GC_DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except IOError as e:
            script_log(f"Error saving GC data: {e}", level="ERROR")
            return False
    
    def get_gc_data(channel_id):
        """Get data for a specific group chat."""
        data = load_gc_data()
        channel_str = str(channel_id)
        
        if channel_str not in data["group_chats"]:
            data["group_chats"][channel_str] = {
                "nojoin": [],
                "noleave": [],
                "lockdown": False,
                "whitelist": []
            }
            save_gc_data(data)
        
        return data["group_chats"][channel_str]
    
    def update_gc_data(channel_id, gc_data):
        """Update data for a specific group chat."""
        data = load_gc_data()
        data["group_chats"][str(channel_id)] = gc_data
        return save_gc_data(data)
    
    def is_group_chat(channel):
        """Check if the channel is a group chat (group DM)."""
        # Group chats have type 3 and no guild
        return channel.type.value == 3 if hasattr(channel.type, 'value') else str(channel.type) == "3"
    
    async def generate_whitelist(channel):
        """Generate whitelist from current recipients (members) of the group chat."""
        whitelist = set()
        
        # Add all current recipients (members) of the group chat
        if channel and hasattr(channel, 'recipients'):
            for recipient in channel.recipients:
                whitelist.add(str(recipient.id))
        
        # Add the bot user itself
        if bot.user:
            whitelist.add(str(bot.user.id))
        
        return list(whitelist)
    
    async def resolve_user(ctx, user_input):
        """
        Resolve user input (ID, username, or mention) to a user object and ID.
        Returns tuple of (user_object, user_id_string) or (None, None) if not found.
        """
        if not user_input:
            return None, None
        
        user = None
        
        # Try to parse as mention first (<@!123> or <@123>)
        if user_input.startswith('<@') and user_input.endswith('>'):
            # Extract ID from mention
            user_id = user_input.replace('<@!', '').replace('<@', '').replace('>', '')
            try:
                user_id = int(user_id)
                user = bot.get_user(user_id)
                if not user:
                    # Try to fetch user if not in cache
                    try:
                        user = await bot.fetch_user(user_id)
                    except:
                        pass
                return user, str(user_id)
            except ValueError:
                pass
        
        # Try to parse as raw user ID
        try:
            user_id = int(user_input)
            user = bot.get_user(user_id)
            if not user:
                # Try to fetch user if not in cache
                try:
                    user = await bot.fetch_user(user_id)
                except:
                    pass
            return user, str(user_id)
        except ValueError:
            pass
        
        # Try to find by username (with or without discriminator)
        # First check current group chat recipients
        if hasattr(ctx.channel, 'recipients'):
            for recipient in ctx.channel.recipients:
                # Check full username#discriminator format
                if user_input.lower() == f"{recipient.name.lower()}#{recipient.discriminator}":
                    return recipient, str(recipient.id)
                # Check just username (case insensitive)
                elif user_input.lower() == recipient.name.lower():
                    return recipient, str(recipient.id)
                # Check display name if different
                elif hasattr(recipient, 'display_name') and user_input.lower() == recipient.display_name.lower():
                    return recipient, str(recipient.id)
        
        # Check bot's cached users
        for cached_user in bot.users:
            # Check full username#discriminator format
            if user_input.lower() == f"{cached_user.name.lower()}#{cached_user.discriminator}":
                return cached_user, str(cached_user.id)
            # Check just username (case insensitive)
            elif user_input.lower() == cached_user.name.lower():
                return cached_user, str(cached_user.id)
            # Check display name if different
            elif hasattr(cached_user, 'display_name') and user_input.lower() == cached_user.display_name.lower():
                return cached_user, str(cached_user.id)
        
        return None, None
    
    def format_user_display(user, user_id):
        """Format user for display in messages."""
        if user:
            if hasattr(user, 'discriminator') and user.discriminator != '0':
                return f"{user.name}#{user.discriminator} (`{user_id}`)"
            else:
                return f"{user.name} (`{user_id}`)"
        else:
            return f"`{user_id}` (user not found)"
    
    async def safe_remove_recipient(channel, user, context="operation"):
        """
        Safely attempt to remove a user from a group chat with error handling.
        Returns tuple of (success: bool, error_message: str or None)
        """
        try:
            await channel.remove_recipients(user)
            return True, None
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for specific Discord API errors
            if "missing permissions" in error_msg or "insufficient permissions" in error_msg:
                return False, f"❌ **Permission Error:** Cannot remove user from group chat. You may not have the necessary permissions to remove members."
            elif "unknown user" in error_msg or "user not found" in error_msg:
                return False, f"❌ **User Error:** User not found or no longer exists."
            elif "cannot remove" in error_msg or "invalid recipient" in error_msg:
                return False, f"❌ **Removal Error:** Cannot remove this user. They may have already left or cannot be removed from this group chat."
            elif "rate limit" in error_msg:
                return False, f"❌ **Rate Limited:** Too many actions too quickly. Please wait a moment and try again."
            else:
                script_log(f"Unexpected error removing user during {context}: {e}", level="ERROR")
                return False, f"❌ **Unexpected Error:** Failed to remove user from group chat. Error: {str(e)[:100]}"
    
    async def safe_add_recipient(channel, user, context="operation"):
        """
        Safely attempt to add a user to a group chat with error handling.
        Returns tuple of (success: bool, error_message: str or None)
        """
        try:
            await channel.add_recipients(user)
            return True, None
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for specific Discord API errors
            if "missing permissions" in error_msg or "insufficient permissions" in error_msg:
                return False, f"❌ **Permission Error:** Cannot add user to group chat. You may not have the necessary permissions to add members."
            elif "unknown user" in error_msg or "user not found" in error_msg:
                return False, f"❌ **User Error:** User not found or no longer exists."
            elif "cannot add" in error_msg or "invalid recipient" in error_msg:
                return False, f"❌ **Add Error:** Cannot add this user to the group chat. They may have privacy settings that prevent being added to group chats, or the group chat may be at maximum capacity."
            elif "already in" in error_msg or "duplicate" in error_msg:
                return False, f"❌ **Already Present:** User is already in the group chat."
            elif "rate limit" in error_msg:
                return False, f"❌ **Rate Limited:** Too many actions too quickly. Please wait a moment and try again."
            elif "send messages" in error_msg:
                return False, f"❌ **Messaging Error:** User cannot be added because they have blocked you or have privacy settings that prevent them from being added to group chats."
            elif "blocked" in error_msg or "privacy" in error_msg:
                return False, f"❌ **Privacy Error:** User's privacy settings prevent them from being added to group chats, or they have blocked someone in this group."
            else:
                script_log(f"Unexpected error adding user during {context}: {e}", level="ERROR")
                return False, f"❌ **Unexpected Error:** Failed to add user to group chat. Error: {str(e)[:100]}"
    
    @bot.command(
        name="gm",
        usage="<subcommand> [args]",
        description="Manage group chat restrictions and lockdown features"
    )
    async def gc_manage(ctx, *, args: str=None):
        await ctx.message.delete()
        
        # Check if we're in a group chat (group DM)
        if not is_group_chat(ctx.channel):
            await send_embed_safely(
                ctx.channel.id,
                "❌ Invalid Channel Type",
                "This command only works in Discord group chats (group DMs), not servers or regular DMs."
            )
            return
        
        if not args:
            await show_help(ctx)
            return
        
        parts = args.strip().split()
        subcommand = parts[0].lower()
        subargs = parts[1:] if len(parts) > 1 else []
        
        if subcommand == "nojoin":
            await handle_nojoin(ctx, subargs)
        elif subcommand == "noleave":
            await handle_noleave(ctx, subargs)
        elif subcommand == "allowjoin":
            await handle_allowjoin(ctx, subargs)
        elif subcommand == "allowleave":
            await handle_allowleave(ctx, subargs)
        elif subcommand == "lockdown":
            await handle_lockdown(ctx)
        elif subcommand == "unlock":
            await handle_unlock(ctx)
        elif subcommand == "whitelist":
            await handle_whitelist(ctx, subargs)
        elif subcommand == "unwhitelist":
            await handle_unwhitelist(ctx, subargs)
        elif subcommand == "status":
            await handle_status(ctx)
        elif subcommand == "clear":
            await handle_clear(ctx, subargs)
        elif subcommand in ["help", "?"]:
            await show_help(ctx)
        else:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Unknown Command",
                f"Unknown subcommand: `{subcommand}`. Use `{getConfigData().get('prefix', '<p>')}gm help` for available commands."
            )
    
    async def handle_nojoin(ctx, args):
        """Handle nojoin command."""
        gc_data = get_gc_data(ctx.channel.id)
        
        # Check if lockdown is active
        if gc_data["lockdown"]:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Lockdown Active",
                "Cannot modify nojoin list while lockdown is active. Use `gm unlock` first or manage the lockdown whitelist instead."
            )
            return
        
        if not args:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Invalid Usage",
                "**Usage:** `gm nojoin <user_id|username|@mention>`"
            )
            return
        
        user_input = ' '.join(args)  # Join all args in case username has spaces
        user, user_id = await resolve_user(ctx, user_input)
        
        if not user_id:
            await send_embed_safely(
                ctx.channel.id,
                "❌ User Not Found",
                f"Could not find user: `{user_input}`. Try using their user ID, exact username, or mention."
            )
            return
        
        if user_id in gc_data["nojoin"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Already Restricted",
                f"User {format_user_display(user, user_id)} is already in the nojoin list."
            )
            return
        
        # Check if user is in noleave list
        if user_id in gc_data["noleave"]:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Conflict Error",
                f"Cannot add {format_user_display(user, user_id)} to nojoin list - they are already in the noleave list. A user cannot be in both lists."
            )
            return
        
        gc_data["nojoin"].append(user_id)
        
        if update_gc_data(ctx.channel.id, gc_data):
            await send_embed_safely(
                ctx.channel.id,
                "✅ Success",
                f"User {format_user_display(user, user_id)} added to nojoin list."
            )
            script_log(f"Added user {user_id} to nojoin list in group chat {ctx.channel.id}")
        else:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Database Error",
                "Failed to save nojoin data. Please try again."
            )
    
    async def handle_noleave(ctx, args):
        """Handle noleave command."""
        gc_data = get_gc_data(ctx.channel.id)
        
        # Check if lockdown is active
        if gc_data["lockdown"]:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Lockdown Active",
                "Cannot modify noleave list while lockdown is active. Use `gm unlock` first or manage the lockdown whitelist instead."
            )
            return
        
        if not args:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Invalid Usage",
                "**Usage:** `gm noleave <user_id|username|@mention>`"
            )
            return
        
        user_input = ' '.join(args)  # Join all args in case username has spaces
        user, user_id = await resolve_user(ctx, user_input)
        
        if not user_id:
            await send_embed_safely(
                ctx.channel.id,
                "❌ User Not Found",
                f"Could not find user: `{user_input}`. Try using their user ID, exact username, or mention."
            )
            return
        
        if user_id in gc_data["noleave"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Already Restricted",
                f"User {format_user_display(user, user_id)} is already in the noleave list."
            )
            return
        
        # Check if user is in nojoin list
        if user_id in gc_data["nojoin"]:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Conflict Error",
                f"Cannot add {format_user_display(user, user_id)} to noleave list - they are already in the nojoin list. A user cannot be in both lists."
            )
            return
        
        gc_data["noleave"].append(user_id)
        
        if update_gc_data(ctx.channel.id, gc_data):
            await send_embed_safely(
                ctx.channel.id,
                "✅ Success",
                f"User {format_user_display(user, user_id)} added to noleave list."
            )
            script_log(f"Added user {user_id} to noleave list in group chat {ctx.channel.id}")
        else:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Database Error",
                "Failed to save noleave data. Please try again."
            )
    
    async def handle_allowjoin(ctx, args):
        """Handle allowjoin command."""
        gc_data = get_gc_data(ctx.channel.id)
        
        # Check if lockdown is active
        if gc_data["lockdown"]:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Lockdown Active",
                "Cannot modify nojoin list while lockdown is active. Use `gm unlock` first or manage the lockdown whitelist instead."
            )
            return
        
        if not args:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Invalid Usage",
                "**Usage:** `gm allowjoin <user_id|username|@mention>`"
            )
            return
        
        user_input = ' '.join(args)  # Join all args in case username has spaces
        user, user_id = await resolve_user(ctx, user_input)
        
        if not user_id:
            await send_embed_safely(
                ctx.channel.id,
                "❌ User Not Found",
                f"Could not find user: `{user_input}`. Try using their user ID, exact username, or mention."
            )
            return
        
        if user_id not in gc_data["nojoin"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Not Restricted",
                f"User {format_user_display(user, user_id)} is not in the nojoin list."
            )
            return
        
        gc_data["nojoin"].remove(user_id)
        
        if update_gc_data(ctx.channel.id, gc_data):
            await send_embed_safely(
                ctx.channel.id,
                "✅ Success",
                f"User {format_user_display(user, user_id)} removed from nojoin list."
            )
            script_log(f"Removed user {user_id} from nojoin list in group chat {ctx.channel.id}")
        else:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Database Error",
                "Failed to save nojoin data. Please try again."
            )
    
    async def handle_allowleave(ctx, args):
        """Handle allowleave command."""
        gc_data = get_gc_data(ctx.channel.id)
        
        # Check if lockdown is active
        if gc_data["lockdown"]:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Lockdown Active",
                "Cannot modify noleave list while lockdown is active. Use `gm unlock` first or manage the lockdown whitelist instead."
            )
            return
        
        if not args:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Invalid Usage",
                "**Usage:** `gm allowleave <user_id|username|@mention>`"
            )
            return
        
        user_input = ' '.join(args)  # Join all args in case username has spaces
        user, user_id = await resolve_user(ctx, user_input)
        
        if not user_id:
            await send_embed_safely(
                ctx.channel.id,
                "❌ User Not Found",
                f"Could not find user: `{user_input}`. Try using their user ID, exact username, or mention."
            )
            return
        
        if user_id not in gc_data["noleave"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Not Restricted",
                f"User {format_user_display(user, user_id)} is not in the noleave list."
            )
            return
        
        gc_data["noleave"].remove(user_id)
        
        if update_gc_data(ctx.channel.id, gc_data):
            await send_embed_safely(
                ctx.channel.id,
                "✅ Success",
                f"User {format_user_display(user, user_id)} removed from noleave list."
            )
            script_log(f"Removed user {user_id} from noleave list in group chat {ctx.channel.id}")
        else:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Database Error",
                "Failed to save noleave data. Please try again."
            )
    
    async def handle_lockdown(ctx):
        """Handle lockdown command."""
        gc_data = get_gc_data(ctx.channel.id)
        
        if gc_data["lockdown"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Already Active",
                "Lockdown is already enabled for this group chat."
            )
            return
        
        try:
            # Generate whitelist from current members
            whitelist = await generate_whitelist(ctx.channel)
            
            gc_data["lockdown"] = True
            gc_data["whitelist"] = whitelist
            
            if update_gc_data(ctx.channel.id, gc_data):
                description = f"""**Lockdown Mode Active:**
• Only whitelisted users can join this group chat
• Whitelisted users cannot leave
• nojoin/noleave lists are disabled during lockdown
• Whitelist contains {len(whitelist)} authorized users

Use `gm status` to view the whitelist or `gm unlock` to disable lockdown."""
                
                await send_embed_safely(
                    ctx.channel.id,
                    "🔒 LOCKDOWN ENABLED!",
                    description
                )
                script_log(f"Lockdown enabled in group chat {ctx.channel.id} with {len(whitelist)} whitelisted users")
            else:
                await send_embed_safely(
                    ctx.channel.id,
                    "❌ Database Error",
                    "Failed to enable lockdown. Please try again."
                )
        except Exception as e:
            script_log(f"Error enabling lockdown in group chat {ctx.channel.id}: {e}", level="ERROR")
            await send_embed_safely(
                ctx.channel.id,
                "❌ Lockdown Error",
                f"Failed to enable lockdown mode. Error: {str(e)[:100]}"
            )
    
    async def handle_unlock(ctx):
        """Handle unlock command."""
        gc_data = get_gc_data(ctx.channel.id)
        
        if not gc_data["lockdown"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Not Active",
                "Lockdown is not currently enabled."
            )
            return
        
        try:
            gc_data["lockdown"] = False
            gc_data["whitelist"] = []
            
            if update_gc_data(ctx.channel.id, gc_data):
                await send_embed_safely(
                    ctx.channel.id,
                    "🔓 Lockdown Disabled",
                    "Lockdown has been disabled."
                )
                script_log(f"Lockdown disabled in group chat {ctx.channel.id}")
            else:
                await send_embed_safely(
                    ctx.channel.id,
                    "❌ Database Error",
                    "Failed to disable lockdown. Please try again."
                )
        except Exception as e:
            script_log(f"Error disabling lockdown in group chat {ctx.channel.id}: {e}", level="ERROR")
            await send_embed_safely(
                ctx.channel.id,
                "❌ Unlock Error",
                f"Failed to disable lockdown mode. Error: {str(e)[:100]}"
            )
    
    async def handle_whitelist(ctx, args):
        """Handle whitelist command."""
        if not args:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Invalid Usage",
                "**Usage:** `gm whitelist <user_id|username|@mention>`"
            )
            return
        
        user_input = ' '.join(args)  # Join all args in case username has spaces
        user, user_id = await resolve_user(ctx, user_input)
        
        if not user_id:
            await send_embed_safely(
                ctx.channel.id,
                "❌ User Not Found",
                f"Could not find user: `{user_input}`. Try using their user ID, exact username, or mention."
            )
            return
        
        gc_data = get_gc_data(ctx.channel.id)
        
        if not gc_data["lockdown"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Lockdown Not Active",
                "Lockdown is not enabled. Whitelist is only used during lockdown mode."
            )
            return
        
        if user_id in gc_data["whitelist"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Already Whitelisted",
                f"User {format_user_display(user, user_id)} is already in the lockdown whitelist."
            )
            return
        
        gc_data["whitelist"].append(user_id)
        
        if update_gc_data(ctx.channel.id, gc_data):
            await send_embed_safely(
                ctx.channel.id,
                "✅ Success",
                f"User {format_user_display(user, user_id)} added to lockdown whitelist."
            )
            script_log(f"Added user {user_id} to whitelist in group chat {ctx.channel.id}")
        else:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Database Error",
                "Failed to update whitelist. Please try again."
            )
    
    async def handle_unwhitelist(ctx, args):
        """Handle unwhitelist command."""
        if not args:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Invalid Usage",
                "**Usage:** `gm unwhitelist <user_id|username|@mention>`"
            )
            return
        
        user_input = ' '.join(args)  # Join all args in case username has spaces
        user, user_id = await resolve_user(ctx, user_input)
        
        if not user_id:
            await send_embed_safely(
                ctx.channel.id,
                "❌ User Not Found",
                f"Could not find user: `{user_input}`. Try using their user ID, exact username, or mention."
            )
            return
        
        gc_data = get_gc_data(ctx.channel.id)
        
        if not gc_data["lockdown"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Lockdown Not Active",
                "Lockdown is not enabled. Whitelist is only used during lockdown mode."
            )
            return
        
        if user_id not in gc_data["whitelist"]:
            await send_embed_safely(
                ctx.channel.id,
                "⚠️ Not Whitelisted",
                f"User {format_user_display(user, user_id)} is not in the lockdown whitelist."
            )
            return
        
        gc_data["whitelist"].remove(user_id)
        
        if update_gc_data(ctx.channel.id, gc_data):
            await send_embed_safely(
                ctx.channel.id,
                "✅ Success",
                f"User {format_user_display(user, user_id)} removed from lockdown whitelist."
            )
            script_log(f"Removed user {user_id} from whitelist in group chat {ctx.channel.id}")
        else:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Database Error",
                "Failed to update whitelist. Please try again."
            )
    
    async def handle_status(ctx):
        """Handle status command."""
        try:
            gc_data = get_gc_data(ctx.channel.id)
            
            if gc_data["lockdown"]:
                # During lockdown, show lockdown status and whitelist
                status_text = f"🔒 **LOCKDOWN MODE ACTIVE**\n\n"
                status_text += f"**Current Mode:**\n"
                status_text += f"• Only whitelisted users can join this group chat\n"
                status_text += f"• Whitelisted users cannot leave (full lockdown)\n"
                status_text += f"• nojoin/noleave lists are disabled during lockdown\n\n"
                status_text += f"**Authorized Whitelist ({len(gc_data['whitelist'])} users):**\n"
                
                if gc_data["whitelist"]:
                    for user_id in gc_data["whitelist"]:
                        user = bot.get_user(int(user_id))
                        if not user:
                            try:
                                user = await bot.fetch_user(int(user_id))
                            except:
                                pass
                        status_text += f"• {format_user_display(user, user_id)}\n"
                else:
                    status_text += "• No users in whitelist (only current members can join)\n"
                
                status_text += f"\n*Use `gm unlock` to disable lockdown mode*"
                
                await send_embed_safely(
                    ctx.channel.id,
                    "🔒 Lockdown Status",
                    status_text
                )
            else:
                # Normal status display
                nojoin_text = ""
                if gc_data["nojoin"]:
                    for user_id in gc_data["nojoin"]:
                        user = bot.get_user(int(user_id))
                        if not user:
                            try:
                                user = await bot.fetch_user(int(user_id))
                            except:
                                pass
                        nojoin_text += f"• {format_user_display(user, user_id)}\n"
                else:
                    nojoin_text = "• No restrictions\n"
                
                noleave_text = ""
                if gc_data["noleave"]:
                    for user_id in gc_data["noleave"]:
                        user = bot.get_user(int(user_id))
                        if not user:
                            try:
                                user = await bot.fetch_user(int(user_id))
                            except:
                                pass
                        noleave_text += f"• {format_user_display(user, user_id)}\n"
                else:
                    noleave_text = "• No restrictions\n"
                
                status_text = f"🔒 **Lockdown:** Disabled\n\n"
                status_text += f"**No Join List ({len(gc_data['nojoin'])} users):**\n{nojoin_text}\n"
                status_text += f"**No Leave List ({len(gc_data['noleave'])} users):**\n{noleave_text}"
                
                await send_embed_safely(
                    ctx.channel.id,
                    "📊 Group Chat Status",
                    status_text
                )
        except Exception as e:
            script_log(f"Error displaying status in group chat {ctx.channel.id}: {e}", level="ERROR")
            await send_embed_safely(
                ctx.channel.id,
                "❌ Status Error",
                f"Failed to retrieve group chat status. Error: {str(e)[:100]}"
            )
    
    async def handle_clear(ctx, args):
        """Handle clear command."""
        if not args:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Invalid Usage",
                "**Usage:** `gm clear <nojoin|noleave>`"
            )
            return
        
        clear_type = args[0].lower()
        
        if clear_type not in ["nojoin", "noleave"]:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Invalid Type",
                "Clear type must be either `nojoin` or `noleave`."
            )
            return
        
        gc_data = get_gc_data(ctx.channel.id)
        
        # Check if lockdown is active
        if gc_data["lockdown"]:
            await send_embed_safely(
                ctx.channel.id,
                "❌ Lockdown Active",
                f"Cannot clear {clear_type} list while lockdown is active. Use `gm unlock` first."
            )
            return
        
        try:
            if clear_type == "nojoin":
                cleared_count = len(gc_data["nojoin"])
                gc_data["nojoin"] = []
            else:  # noleave
                cleared_count = len(gc_data["noleave"])
                gc_data["noleave"] = []
            
            if update_gc_data(ctx.channel.id, gc_data):
                await send_embed_safely(
                    ctx.channel.id,
                    "✅ Success",
                    f"Cleared {cleared_count} users from {clear_type} list."
                )
                script_log(f"Cleared {clear_type} list in group chat {ctx.channel.id}")
            else:
                await send_embed_safely(
                    ctx.channel.id,
                    "❌ Database Error",
                    f"Failed to clear {clear_type} list. Please try again."
                )
        except Exception as e:
            script_log(f"Error clearing {clear_type} list in group chat {ctx.channel.id}: {e}", level="ERROR")
            await send_embed_safely(
                ctx.channel.id,
                "❌ Clear Error",
                f"Failed to clear {clear_type} list. Error: {str(e)[:100]}"
            )
    
    async def show_help(ctx):
        """Show detailed help information."""
        prefix = getConfigData().get('prefix', '<p>')
        help_text = f"""**Basic Commands:**
• `{prefix}gm nojoin <user_id>` - Prevent user from joining
• `{prefix}gm noleave <user_id>` - Prevent user from leaving
• `{prefix}gm allowjoin <user_id>` - Remove user from nojoin list
• `{prefix}gm allowleave <user_id>` - Remove user from noleave list
• `{prefix}gm status` - Show current restrictions

**Lockdown Commands:**
• `{prefix}gm lockdown` - Enable lockdown mode
• `{prefix}gm unlock` - Disable lockdown mode
• `{prefix}gm whitelist <user_id>` - Add user to lockdown whitelist
• `{prefix}gm unwhitelist <user_id>` - Remove user from whitelist

**Management Commands:**
• `{prefix}gm clear nojoin` - Clear all nojoin restrictions
• `{prefix}gm clear noleave` - Clear all noleave restrictions

**Lockdown Mode:**
• **JOIN LOCKDOWN:** Only whitelisted users can join the group chat
• **LEAVE LOCKDOWN:** Whitelisted users cannot leave the group chat
• Auto-generates whitelist from current members when enabled
• nojoin/noleave lists are disabled during lockdown mode
• Only the lockdown whitelist matters when active

**Error Handling:**
• Enhanced error reporting for permission issues
• Detailed feedback when operations fail
• Automatic detection of Discord API limitations

**Notes:**
• Only works in Discord group chats (group DMs)
• All restrictions are specific to this group chat
• Use numeric user IDs, usernames, or mentions
• Commands work for all group chat members"""
        
        await send_embed_safely(
            ctx.channel.id,
            "📚 Group Chat Manager Help",
            help_text
        )
    
    # Event listener for group chat recipient changes
    @bot.listen("on_group_join")
    async def on_group_join(channel, user):
        """Handle when someone joins a group chat."""
        if not is_group_chat(channel):
            return
        
        gc_data = get_gc_data(channel.id)
        user_id = str(user.id)
        
        # During lockdown, only check whitelist (nojoin is disabled)
        if gc_data["lockdown"]:
            if user_id not in gc_data["whitelist"]:
                success, error_msg = await safe_remove_recipient(channel, user, "lockdown enforcement")
                if success:
                    script_log(f"Removed user {user_id} from group chat {channel.id} (lockdown - not whitelisted)")
                else:
                    # Send error message to channel
                    try:
                        await send_embed_safely(
                            channel.id,
                            "🔒 Lockdown Enforcement Failed",
                            f"User {format_user_display(user, user_id)} joined but is not whitelisted.\n\n{error_msg}"
                        )
                    except:
                        script_log(f"Failed to send lockdown error message to channel {channel.id}", level="ERROR")
            return
        
        # Normal mode: check nojoin restrictions only
        if user_id in gc_data["nojoin"]:
            success, error_msg = await safe_remove_recipient(channel, user, "nojoin enforcement")
            if success:
                script_log(f"Removed user {user_id} from group chat {channel.id} (nojoin)")
            else:
                # Send error message to channel
                try:
                    await send_embed_safely(
                        channel.id,
                        "⛔ Nojoin Enforcement Failed",
                        f"User {format_user_display(user, user_id)} joined but is on the nojoin list.\n\n{error_msg}"
                    )
                except:
                    script_log(f"Failed to send nojoin error message to channel {channel.id}", level="ERROR")
    
    @bot.listen("on_group_remove")
    async def on_group_remove(channel, user):
        """Handle when someone leaves a group chat."""
        if not is_group_chat(channel):
            return
        
        gc_data = get_gc_data(channel.id)
        user_id = str(user.id)
        
        # During lockdown, prevent whitelisted users from leaving
        if gc_data["lockdown"]:
            if user_id in gc_data["whitelist"]:
                script_log(f"User {user_id} left group chat {channel.id} during lockdown but is whitelisted - re-adding", level="INFO")
                
                success, error_msg = await safe_add_recipient(channel, user, "lockdown leave prevention")
                if success:
                    script_log(f"Successfully re-added whitelisted user {user_id} to group chat {channel.id} (lockdown)", level="INFO")
                else:
                    # Send error message to channel
                    try:
                        await send_embed_safely(
                            channel.id,
                            "🔒 Lockdown Leave Prevention Failed",
                            f"Whitelisted user {format_user_display(user, user_id)} left during lockdown but could not be re-added.\n\n{error_msg}"
                        )
                    except:
                        script_log(f"Failed to send lockdown leave prevention error message to channel {channel.id}", level="ERROR")
            else:
                # Non-whitelisted user left during lockdown - this is allowed
                script_log(f"Non-whitelisted user {user_id} left group chat {channel.id} during lockdown (allowed)", level="INFO")
            return
        
        # Normal mode: check noleave restrictions only
        if user_id in gc_data["noleave"]:
            script_log(f"User {user_id} left group chat {channel.id} but is on noleave list", level="INFO")
            
            success, error_msg = await safe_add_recipient(channel, user, "noleave enforcement")
            if success:
                script_log(f"Re-added user {user_id} to group chat {channel.id} (noleave)", level="INFO")
            else:
                # Send error message to channel
                try:
                    await send_embed_safely(
                        channel.id,
                        "🚫 Noleave Enforcement Failed",
                        f"User {format_user_display(user, user_id)} left but is on the noleave list.\n\n{error_msg}"
                    )
                except:
                    script_log(f"Failed to send noleave error message to channel {channel.id}", level="ERROR")
    
    script_log("Group Chat Manager initialized successfully")

script_function()