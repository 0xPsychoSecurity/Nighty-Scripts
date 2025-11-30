@nightyScript(
    name="Message Logger v4",
    author="@Rayyy, Updated by @10010100101010011100101101010101",
    description=(
        "Logs deleted, edited, and bulk deleted messages to a webhook for DMs, Groups, and specified servers. "
        "Supports dynamic server management, including commands to add, remove, and view monitored servers."
    ),
    usage=(
        "UI Script | Commands:\n"
        "• `(prefix)addmsglog <server_id>` → Adds a server to the message log monitored servers.\n"
        "• `(prefix)removemsglog <server_id>` → Removes a server from the monitored servers.\n"
        "• `(prefix)showmsglog` → Displays all monitored servers.\n"
        "• `(prefix)testwebhook` → Tests the main webhook with a sample message.\n"
        "• `(prefix)blacklistrole add <role_id>` → Add a role ID to the blacklist.\n"
        "• `(prefix)blacklistrole remove <role_id>` → Remove a role ID from the blacklist.\n"
        "• `(prefix)blacklistrole list` → List all blacklisted roles.\n"
        "• `(prefix)blacklistchannel add <channel_id>` → Add a channel ID to the blacklist.\n"
        "• `(prefix)blacklistchannel remove <channel_id>` → Remove a channel ID from the blacklist.\n"
        "• `(prefix)blacklistchannel list` → List all blacklisted channel IDs.\n\n"
        "Automatically logs deleted, edited, and bulk deleted messages for servers in the monitored servers, "
        "including message content and attachments."
    )
)

def messageLogger():
    BASE_DIR = Path(getScriptsPath()) / "json"
    SERVER_FILE = BASE_DIR / "msglogservers.json"
    CONFIG_FILE = BASE_DIR / "msglogconfig.json"

    def initialize_files():
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        if not SERVER_FILE.exists():
            with open(SERVER_FILE, "w") as f:
                json.dump({"servers": []}, f, indent=4)
        if not CONFIG_FILE.exists():
            default_config = {
                "main_webhook": "https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxx",
                "image_dump_webhook": "https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxx",
                "custom_avatar_url": "https://png.pngtree.com/xxxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxx.png",
                "custom_username": "Message Logger",
                "log_deleted": True,
                "log_edited": True,
                "log_bulk_deleted": True,
                "log_attachments": True,
                "log_dm": True,
                "log_group": True,
                "debug": False,
                "blacklisted_roles": [],
                "blacklisted_channels": []
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(default_config, f, indent=4)

    def load_config():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Recreate a fresh config if missing or corrupt to avoid recursion
            try:
                if CONFIG_FILE.exists():
                    CONFIG_FILE.unlink()
            except Exception:
                pass
            initialize_files()
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)

    def save_config(config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    def debug_print(*args, **kwargs):
        config = load_config()
        if config.get("debug", False):
            print(*args, **kwargs)

    def load_servers():
        try:
            with open(SERVER_FILE, "r") as f:
                data = json.load(f)
                servers = data.get("servers", [])
                debug_print(f"Loaded servers from file: {servers}")
                return servers
        except (FileNotFoundError, json.JSONDecodeError) as e:
            debug_print(f"Error loading servers: {e}")
            return []

    def save_servers(servers):
        try:
            with open(SERVER_FILE, "w") as f:
                json.dump({"servers": servers}, f, indent=4)
            debug_print(f"Saved servers to file: {servers}")
        except Exception as e:
            debug_print(f"Error saving servers: {e}")

    # Initialize files
    initialize_files()

    def get_current_time():
        """Get the current time formatted for the embed."""
        current_time = datetime.utcnow() + timedelta(hours=8)
        return current_time.strftime('%Y-%m-%d %I:%M %p (UTC+8)')

    async def upload_media_to_dump(attachment, message):
        """Upload media (image/video/audio) to the image dump webhook with size limit and temp cleanup.
        Returns the hosted URL on success, or None otherwise.
        """
        config = load_config()
        if not config.get("log_attachments", True):
            return None

        # Allowlists and size limit
        MAX_BYTES = 20 * 1024 * 1024  # 20MB limit
        name_lower = (attachment.filename or "").lower()
        is_image = name_lower.endswith(("png", "jpg", "jpeg", "gif", "bmp", "webp")) or \
                   (attachment.content_type or "").startswith("image/")
        is_video = name_lower.endswith(("mp4",)) or (attachment.content_type or "").startswith("video/")
        is_audio = name_lower.endswith(("mp3", "wav", "ogg")) or (attachment.content_type or "").startswith("audio/")

        if not (is_image or is_video or is_audio):
            return None

        # Skip if over size limit (use Attachment.size when available to avoid downloading)
        try:
            if hasattr(attachment, "size") and attachment.size and attachment.size > MAX_BYTES:
                return None
        except Exception:
            pass

        # Build location info
        if message.guild:
            location_info = f"🌍 **Server:** {message.guild.name} (`{message.guild.id}`)\n" \
                            f"📺 **Channel:** {message.channel.mention} (`{message.channel.id}`)"
        elif message.channel.type == discord.ChannelType.group:
            location_info = f"👥 **Group Chat:** {message.channel.name or 'Unnamed Group'} (`{message.channel.id}`)"
        else:
            location_info = "📩 **Direct Message**"

        # Determine label and mime type
        label = "Image" if is_image else ("Video" if is_video else "Audio")

        # Download to a temp file then upload; ensure cleanup
        import tempfile, os, mimetypes
        temp_path = None
        try:
            # Stream download to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix="_" + attachment.filename) as tmp:
                temp_path = tmp.name
                with requests.get(attachment.url, stream=True) as r:
                    r.raise_for_status()
                    total = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        total += len(chunk)
                        if total > MAX_BYTES:
                            # Exceeds limit; stop and skip
                            raise ValueError("File exceeds 20MB limit")
                        tmp.write(chunk)

            mime, _ = mimetypes.guess_type(attachment.filename)
            mime = mime or (attachment.content_type or "application/octet-stream")

            with open(temp_path, "rb") as f:
                response = requests.post(
                    config["image_dump_webhook"],
                    files={"file": (attachment.filename, f, mime)},
                    data={
                        "content": (
                            f"🗑 **Deleted {label}**\n"
                            f"🧑 **User:** <@{message.author.id}> (`{message.author.id}`)\n"
                            f"{location_info}"
                        )
                    },
                )

            if response.status_code == 200:
                uploaded_data = response.json()
                if "attachments" in uploaded_data and len(uploaded_data["attachments"]) > 0:
                    return uploaded_data["attachments"][0]["url"]
            else:
                print(f"Failed to upload media. Response: {response.status_code} {response.text}")
                return None
        except ValueError:
            # Over size limit or other validation; skip logging
            return None
        except Exception as e:
            print(f"Error uploading media: {e}")
            return None
        finally:
            # Purge temp file
            try:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass

    async def send_to_webhook(webhook_url, data):
        """Send data (embed or text) to a specified webhook."""
        try:
            response = requests.post(webhook_url, json=data)
            if response.status_code != 204:
                print(f"Failed to send webhook: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error posting to webhook: {e}")

    async def fetch_server_name(server_id: str):
        """Fetch the server name using the server ID."""
        try:
            guild_id = int(server_id)
            guild = bot.get_guild(guild_id)
            
            if not guild:
                try:
                    guild = await bot.fetch_guild(guild_id)
                except discord.NotFound:
                    print(f"Guild with ID {server_id} not found")
                    return None
                except discord.Forbidden:
                    print(f"No permission to access guild {server_id}")
                    return None
                except Exception as e:
                    print(f"Error fetching guild {server_id}: {e}")
                    return None
            
            if guild:
                # Clean up markdown formatting from server name
                clean_name = guild.name.replace('**', '').replace('*', '').replace('__', '').replace('_', '').replace('~~', '').strip()
                return clean_name
            return None
            
        except ValueError:
            print(f"Invalid server ID format: {server_id}")
            return None
        except Exception as e:
            print(f"Unexpected error in fetch_server_name: {e}")
            return None

    @bot.listen('on_message_delete')
    async def log_deleted_message(message):
        config = load_config()
        # ...existing code...
        # Add DM/Group toggle logic:
        if not config["log_deleted"] or message.author.bot or message.author.id == bot.user.id:
            return
            
        # Check if author has any blacklisted roles
        if message.guild and hasattr(message.author, 'roles'):
            user_roles = [str(role.id) for role in message.author.roles]
            if any(role_id in user_roles for role_id in config.get('blacklisted_roles', [])):
                debug_print(f"Skipping message from user with blacklisted role")
                return
        # Check if channel is blacklisted
        if str(getattr(message.channel, 'id', '')) in config.get('blacklisted_channels', []):
            debug_print(f"Skipping due to blacklisted channel")
            return

        watch_servers = load_servers()
        # Only log DMs if enabled
        if message.guild is None:
            if message.channel.type == discord.ChannelType.private and not config.get("log_dm", True):
                return
            if message.channel.type == discord.ChannelType.group and not config.get("log_group", True):
                return
        # Only log servers if enabled
        if message.guild and not any(server["id"] == str(message.guild.id) for server in watch_servers):
            return

        channel_name = message.channel.mention if message.guild else "📩 **Direct Message**"
        timestamp = get_current_time()
        message_content = message.content or "*No Message Content*"

        attachment_names = [attachment.filename for attachment in message.attachments]
        image_attachments = [attachment for attachment in message.attachments if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'))]
        video_attachments = [attachment for attachment in message.attachments if attachment.filename.lower().endswith(('mp4',))]
        audio_attachments = [attachment for attachment in message.attachments if attachment.filename.lower().endswith(('mp3', 'wav', 'ogg'))]

        attachment_text = "No Attachments" if not attachment_names else ", ".join(attachment_names)
        image_text = "No Images" if not image_attachments else ", ".join([f"[{attachment.filename}]({attachment.url})" for attachment in image_attachments])
        video_text = "No Videos" if not video_attachments else ", ".join([f"[{attachment.filename}]({attachment.url})" for attachment in video_attachments])
        audio_text = "No Audios" if not audio_attachments else ", ".join([f"[{attachment.filename}]({attachment.url})" for attachment in audio_attachments])

        embed_data = {
            "title": "🗑️ Deleted Message",
            "description": f"**{message.author.name}** deleted a message.",
            "color": 0xFF4500,
            "fields": [
                {"name": "📜 Content", "value": f"`{message_content}`", "inline": False},
                {"name": "📎 Attachments", "value": attachment_text, "inline": False},
                {"name": "🖼️ Images", "value": image_text, "inline": False},
                {"name": "🎥 Videos", "value": video_text, "inline": False},
                {"name": "🎵 Audios", "value": audio_text, "inline": False},
                {"name": "🧑 User", "value": f"<@{message.author.id}>", "inline": True},
                {"name": "🔗 Channel", "value": channel_name, "inline": True},
                {"name": "⏰ Timestamp", "value": timestamp, "inline": True},
            ],
            "footer": {"text": config["custom_username"]},
            "timestamp": datetime.utcnow().isoformat()
        }

        # Upload supported media to the dump webhook (images, videos, audios) under 20MB
        for attachment in message.attachments:
            try:
                await upload_media_to_dump(attachment, message)
            except Exception:
                pass

        await send_to_webhook(config["main_webhook"], {"username": config["custom_username"], "avatar_url": config["custom_avatar_url"], "embeds": [embed_data]})

    @bot.listen('on_bulk_message_delete')
    async def log_bulk_deleted_messages(messages):
        config = load_config()
        # ...existing code...
        # Only log DMs/Groups if enabled
        if messages and messages[0].guild is None:
            if messages[0].channel.type == discord.ChannelType.private and not config.get("log_dm", True):
                return
            if messages[0].channel.type == discord.ChannelType.group and not config.get("log_group", True):
                return
        # Only log servers if enabled
        if messages and messages[0].guild and not any(server["id"] == str(messages[0].guild.id) for server in load_servers()):
            return
        # Check if channel is blacklisted
        if messages and str(getattr(messages[0].channel, 'id', '')) in config.get('blacklisted_channels', []):
            return

        channel_name = messages[0].channel.mention if messages[0].guild else "📩 **Direct Message**"
        timestamp = get_current_time()

        message_log = "\n".join(
            [f"**{msg.author.name}:** `{msg.content or '*No Content*'}`" for msg in messages[:2000]]
        )

        deleted_count = len(messages)

        text_data = {
            "username": config["custom_username"],
            "avatar_url": config["custom_avatar_url"],
            "content": f"🗑️ **Bulk Deleted Messages**\nIn {channel_name} at {timestamp}\n\n"
            f"Deleted {deleted_count} messages:\n\n{message_log}"
        }

        await send_to_webhook(config["main_webhook"], text_data)

    @bot.listen('on_message_edit')
    async def log_edited_message(before, after):
        config = load_config()
        # ...existing code...
        # Only log DMs/Groups if enabled
        if before.guild is None:
            if before.channel.type == discord.ChannelType.private and not config.get("log_dm", True):
                return
            if before.channel.type == discord.ChannelType.group and not config.get("log_group", True):
                return
        # Only log servers if enabled
        if before.guild and not any(server["id"] == str(before.guild.id) for server in load_servers()):
            return
        # Check if channel is blacklisted
        if str(getattr(before.channel, 'id', '')) in config.get('blacklisted_channels', []):
            return

        channel_name = before.channel.mention if before.guild else "📩 **Direct Message**"
        timestamp = get_current_time()
        before_content = before.content or "*No Message Content*"
        after_content = after.content or "*No Message Content*"

        attachment_names = [attachment.filename for attachment in before.attachments]
        image_attachments = [attachment for attachment in before.attachments if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'))]
        video_attachments = [attachment for attachment in before.attachments if attachment.filename.lower().endswith(('mp4',))]
        audio_attachments = [attachment for attachment in before.attachments if attachment.filename.lower().endswith(('mp3', 'wav', 'ogg'))]

        attachment_text = "No Attachments" if not attachment_names else ", ".join(attachment_names)
        image_text = "No Images" if not image_attachments else ", ".join([f"[{attachment.filename}]({attachment.url})" for attachment in image_attachments])
        video_text = "No Videos" if not video_attachments else ", ".join([f"[{attachment.filename}]({attachment.url})" for attachment in video_attachments])
        audio_text = "No Audios" if not audio_attachments else ", ".join([f"[{attachment.filename}]({attachment.url})" for attachment in audio_attachments])

        embed_data = {
            "title": "✏️ Edited Message",
            "description": f"**{before.author.name}** edited a message.",
            "color": 0xFF9900,
            "fields": [
                {"name": "📜 Before", "value": f"`{before_content}`", "inline": False},
                {"name": "📜 After", "value": f"`{after_content}`", "inline": False},
                {"name": "📎 Attachments", "value": attachment_text, "inline": False},
                {"name": "🖼️ Images", "value": image_text, "inline": False},
                {"name": "🎥 Videos", "value": video_text, "inline": False},
                {"name": "🎵 Audios", "value": audio_text, "inline": False},
                {"name": "🧑 User", "value": f"<@{before.author.id}>", "inline": True},
                {"name": "🔗 Channel", "value": channel_name, "inline": True},
                {"name": "⏰ Timestamp", "value": timestamp, "inline": True},
            ],
            "footer": {"text": config["custom_username"]},
            "timestamp": datetime.utcnow().isoformat()
        }

        # Upload supported media to the dump webhook (images, videos, audios) under 20MB
        for attachment in before.attachments:
            try:
                await upload_media_to_dump(attachment, before)
            except Exception:
                pass

        await send_to_webhook(config["main_webhook"], {"username": config["custom_username"], "avatar_url": config["custom_avatar_url"], "embeds": [embed_data]})

    # Commands
    @bot.command()
    async def addmsglog(ctx, server_id: str):
        """Add a server to the message monitored servers with its name."""
        watch_servers = load_servers()

        if any(server["id"] == server_id for server in watch_servers):
            await ctx.send(f"⚠️ Server ID `{server_id}` is already in the monitored servers.")
            return

        server_name = await fetch_server_name(server_id)
        if not server_name:
            await ctx.send(f"❌ Unable to find a server with the ID `{server_id}`.")
            return

        watch_servers.append({"id": server_id, "name": server_name})
        save_servers(watch_servers)
        await ctx.send(f"✅ Server **{server_name}** (`{server_id}`) has been added to the monitored servers.")

    @bot.command()
    async def removemsglog(ctx, server_id: str):
        """Remove a server from the message log monitored servers."""
        watch_servers = load_servers()

        for server in watch_servers:
            if server["id"] == server_id:
                watch_servers.remove(server)
                save_servers(watch_servers)
                await ctx.send(f"✅ Server **{server['name']}** (`{server_id}`) has been removed.")
                return

        await ctx.send(f"⚠️ Server ID `{server_id}` is not in the monitored servers.")

    @bot.command()
    async def showmsglog(ctx):
        """Show all servers currently in the message monitored servers."""
        watch_servers = load_servers()

        if not watch_servers:
            await ctx.send("⚠️ The monitored servers is currently empty.")
            return

        server_list = "\n".join([f"- **{server['name']}** (`{server['id']}`)" for server in watch_servers])
        await ctx.send(f"📋 **Monitored Servers:**\n{server_list}")
        
    @bot.command()
    async def blacklistrole(ctx, action: str = None, role_id: str = None):
        """Manage role blacklist for message logging.
        
        Usage:
        `(prefix)blacklistrole add <role_id>` - Add a role to the blacklist
        `(prefix)blacklistrole remove <role_id>` - Remove a role from the blacklist
        `(prefix)blacklistrole list` - List all blacklisted roles
        """
        config = load_config()
        
        if action is None:
            await ctx.send("ℹ️ Please specify an action: `add`, `remove`, or `list`")
            return
            
        if action.lower() == "list":
            blacklisted_roles = config.get('blacklisted_roles', [])
            if not blacklisted_roles:
                await ctx.send("📋 No roles are currently blacklisted.")
                return
                
            roles_info = []
            for role_id in blacklisted_roles:
                role_obj = discord.utils.get(ctx.guild.roles, id=int(role_id)) if ctx.guild else None
                role_name = role_obj.name if role_obj else "Unknown Role"
                roles_info.append(f"- {role_name} (`{role_id}`)")
                
            await ctx.send("🚫 **Blacklisted Roles:**\n" + "\n".join(roles_info))
            return
            
        if role_id is None:
            await ctx.send("⚠️ Please provide a role ID to blacklist.")
            return
            
        # Validate role ID format
        if not role_id.isdigit():
            await ctx.send("⚠️ Invalid role ID. Please provide a valid numeric role ID.")
            return
            
        blacklisted_roles = config.get('blacklisted_roles', [])
        
        if action.lower() == "add":
            if role_id in blacklisted_roles:
                await ctx.send(f"⚠️ Role ID `{role_id}` is already in the blacklist.")
                return
                
            # Verify the role exists
            role = discord.utils.get(ctx.guild.roles, id=int(role_id)) if ctx.guild else None
            role_name = role.name if role else "Unknown Role"
                
            blacklisted_roles.append(role_id)
            config['blacklisted_roles'] = blacklisted_roles
            save_config(config)
            await ctx.send(f"✅ Added role **{role_name}** (`{role_id}`) to the blacklist.")
            
        elif action.lower() == "remove":
            if role_id not in blacklisted_roles:
                await ctx.send(f"⚠️ Role ID `{role_id}` is not in the blacklist.")
                return
                
            role = discord.utils.get(ctx.guild.roles, id=int(role_id)) if ctx.guild else None
            role_name = role.name if role else "Unknown Role"
                
            blacklisted_roles.remove(role_id)
            config['blacklisted_roles'] = blacklisted_roles
            save_config(config)
            await ctx.send(f"✅ Removed role **{role_name}** (`{role_id}`) from the blacklist.")
            
        else:
            await ctx.send("❌ Invalid action. Please use `add`, `remove`, or `list`.")

    @bot.command()
    async def blacklistchannel(ctx, action: str = None, channel_id: str = None):
        config = load_config()

        if action is None:
            await ctx.send("ℹ️ Please specify an action: `add`, `remove`, or `list`")
            return

        if action.lower() == "list":
            blacklisted_channels = config.get('blacklisted_channels', [])
            if not blacklisted_channels:
                await ctx.send("📋 No channels are currently blacklisted.")
                return
            lines = []
            for cid in blacklisted_channels:
                ch = bot.get_channel(int(cid)) if cid.isdigit() else None
                name = ch.name if ch else "Unknown Channel"
                mention = ch.mention if ch else f"<#{cid}>"
                lines.append(f"- {mention} (`{cid}`) - {name}")
            await ctx.send("🚫 **Blacklisted Channels:**\n" + "\n".join(lines))
            return

        if channel_id is None:
            await ctx.send("⚠️ Please provide a channel ID.")
            return
        if not channel_id.isdigit():
            await ctx.send("⚠️ Invalid channel ID. Please provide a valid numeric channel ID.")
            return

        blacklisted_channels = config.get('blacklisted_channels', [])

        if action.lower() == "add":
            if channel_id in blacklisted_channels:
                await ctx.send(f"⚠️ Channel ID `{channel_id}` is already in the blacklist.")
                return
            ch = bot.get_channel(int(channel_id))
            name = ch.name if ch else "Unknown Channel"
            blacklisted_channels.append(channel_id)
            config['blacklisted_channels'] = blacklisted_channels
            save_config(config)
            await ctx.send(f"✅ Added channel **{name}** (`{channel_id}`) to the blacklist.")
        elif action.lower() == "remove":
            if channel_id not in blacklisted_channels:
                await ctx.send(f"⚠️ Channel ID `{channel_id}` is not in the blacklist.")
                return
            ch = bot.get_channel(int(channel_id))
            name = ch.name if ch else "Unknown Channel"
            blacklisted_channels.remove(channel_id)
            config['blacklisted_channels'] = blacklisted_channels
            save_config(config)
            await ctx.send(f"✅ Removed channel **{name}** (`{channel_id}`) from the blacklist.")
        else:
            await ctx.send("❌ Invalid action. Please use `add`, `remove`, or `list`.")

    @bot.command()
    async def testwebhook(ctx):
        """Test the main webhook by sending a sample message."""
        config = load_config()
        timestamp = get_current_time()
        embed_data = {
            "title": "🧪 Webhook Test",
            "description": "This is a test message sent from the Message Logger script.",
            "color": 0x00FF00,
            "fields": [
                {"name": "🧑 Tester", "value": f"<@{ctx.author.id}>", "inline": True},
                {"name": "⏰ Timestamp", "value": timestamp, "inline": True},
            ],
            "footer": {"text": f"{config['custom_username']} - Webhook Test"},
            "timestamp": datetime.utcnow().isoformat()
        }

        await send_to_webhook(config["main_webhook"], {"username": config["custom_username"], "avatar_url": config["custom_avatar_url"], "embeds": [embed_data]})
        await ctx.send("✅ Test message sent to the webhook!")

    # UI Helper Functions
    def isValidUrl(string):
        regex = re.compile(r'^(https?)://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
        return bool(regex.match(string)) or not string

    def isValidWebhookUrl(string):
        webhook_regex = re.compile(r'^https://discord\.com/api/webhooks/\d+/[\w-]+$', re.IGNORECASE)
        return bool(webhook_regex.match(string)) or not string

    def validateWebhookUrl(new_value, current_input):
        if not isValidWebhookUrl(new_value):
            current_input.invalid = True
            current_input.error_message = "Invalid Discord webhook URL format"
            return False
        current_input.invalid = False
        current_input.error_message = None
        return True

    def validateAvatarUrl(new_value, current_input):
        if not isValidUrl(new_value):
            current_input.invalid = True
            current_input.error_message = "Invalid URL format"
            return False
        current_input.invalid = False
        current_input.error_message = None
        return True

    def validateUsername(new_value, current_input):
        if not (2 <= len(new_value) <= 32) and new_value:
            current_input.invalid = True
            current_input.error_message = "Username must be between 2 and 32 characters"
            return False
        current_input.invalid = False
        current_input.error_message = None
        return True

    def validateServerId(new_value, current_input):
        # Allow empty values for clearing
        if not new_value:
            current_input.invalid = False
            current_input.error_message = None
            return True
            
        if not new_value.isdigit():
            current_input.invalid = True
            current_input.error_message = "Server ID must be a valid number"
            return False
            
        # Check if it's a reasonable Discord ID length (17-19 digits)
        if len(new_value) < 17 or len(new_value) > 19:
            current_input.invalid = True
            current_input.error_message = "Server ID should be 17-19 digits long"
            return False
            
        current_input.invalid = False
        current_input.error_message = None
        return True

    # UI Functions
    def updateWebhookSettings():
        config = load_config()
        
        def setMainWebhook(new_value):
            if validateWebhookUrl(new_value, main_webhook_input):
                config["main_webhook"] = new_value
                save_config(config)
                msglog_tab.toast(type="SUCCESS", title="Main webhook updated", description="Main webhook URL has been saved")

        def setImageWebhook(new_value):
            if validateWebhookUrl(new_value, image_webhook_input):
                config["image_dump_webhook"] = new_value
                save_config(config)
                msglog_tab.toast(type="SUCCESS", title="Image webhook updated", description="Image dump webhook URL has been saved")

        def setCustomUsername(new_value):
            if validateUsername(new_value, username_input):
                config["custom_username"] = new_value
                save_config(config)
                msglog_tab.toast(type="SUCCESS", title="Username updated", description="Custom username has been saved")

        def setCustomAvatar(new_value):
            if validateAvatarUrl(new_value, avatar_input):
                config["custom_avatar_url"] = new_value
                save_config(config)
                msglog_tab.toast(type="SUCCESS", title="Avatar updated", description="Custom avatar URL has been saved")

        return setMainWebhook, setImageWebhook, setCustomUsername, setCustomAvatar

    def updateLogSettings():
        config = load_config()

        def toggleDeletedLogs(checked):
            config["log_deleted"] = checked
            save_config(config)
            toggle = "enabled" if checked else "disabled"
            msglog_tab.toast(type="INFO", title="Deleted message logging", description=f"Deleted message logging {toggle}")

        def toggleEditedLogs(checked):
            config["log_edited"] = checked
            save_config(config)
            toggle = "enabled" if checked else "disabled"
            msglog_tab.toast(type="INFO", title="Edited message logging", description=f"Edited message logging {toggle}")

        def toggleBulkLogs(checked):
            config["log_bulk_deleted"] = checked
            save_config(config)
            toggle = "enabled" if checked else "disabled"
            msglog_tab.toast(type="INFO", title="Bulk deleted logging", description=f"Bulk deleted message logging {toggle}")

        def toggleAttachmentLogs(checked):
            config["log_attachments"] = checked
            save_config(config)
            toggle = "enabled" if checked else "disabled"
            msglog_tab.toast(type="INFO", title="Attachment logging", description=f"Attachment logging {toggle}")

        def toggleDMLogs(checked):
            config["log_dm"] = checked
            save_config(config)
            toggle = "enabled" if checked else "disabled"
            msglog_tab.toast(type="INFO", title="DM logging", description=f"DM logging {toggle}")

        def toggleGroupLogs(checked):
            config["log_group"] = checked
            save_config(config)
            toggle = "enabled" if checked else "disabled"
            msglog_tab.toast(type="INFO", title="Group logging", description=f"Group logging {toggle}")

        def toggleDebug(checked):
            config["debug"] = checked
            save_config(config)
            toggle = "enabled" if checked else "disabled"
            msglog_tab.toast(type="INFO", title="Debug mode", description=f"Debug mode {toggle}")

        return (
            toggleDeletedLogs, toggleEditedLogs, toggleBulkLogs,
            toggleAttachmentLogs, toggleDMLogs, toggleGroupLogs, toggleDebug
        )

    def updateServerManagement():
        # Remove all usage of nonlocal current_add_server_id
        def addServerToWatch(server_id):
            debug_print(f"addServerToWatch called with server_id: '{server_id}'")
            if not server_id or not server_id.strip():
                debug_print("Server ID is empty or None")
                msglog_tab.toast(type="ERROR", title="Invalid input", description="Please enter a server ID")
                return

            server_id = server_id.strip()
            debug_print(f"Trimmed server_id: '{server_id}'")

            if not validateServerId(server_id, server_id_input):
                debug_print(f"Validation failed for server_id: {server_id}")
                return

            watch_servers = load_servers()
            debug_print(f"Current servers: {watch_servers}")

            if any(server["id"] == server_id for server in watch_servers):
                debug_print(f"Server {server_id} already exists")
                msglog_tab.toast(type="WARNING", title="Server already exists", description=f"Server ID {server_id} is already being monitored")
                return

            try:
                add_server_button.loading = True
                debug_print("Set button to loading state")
            except Exception as e:
                debug_print(f"Error setting loading state: {e}")

            msglog_tab.toast(type="INFO", title="Adding server", description="Fetching server information...")

            async def fetchAndAdd():
                try:
                    debug_print(f"Fetching server name for ID: {server_id}")
                    server_name = await fetch_server_name(server_id)
                    debug_print(f"Server name result: {server_name}")

                    if not server_name:
                        msglog_tab.toast(type="ERROR", title="Server not found", description=f"Unable to find server with ID {server_id}. Make sure the bot is in this server.")
                        return

                    current_servers = load_servers()
                    new_server = {"id": server_id, "name": server_name}
                    current_servers.append(new_server)
                    save_servers(current_servers)
                    debug_print(f"Server saved: {new_server}")

                    msglog_tab.toast(type="SUCCESS", title="Server added", description=f"Added {server_name} to monitored servers")

                    # Clear input
                    try:
                        server_id_input.value = ""
                    except Exception as e:
                        debug_print(f"Error clearing input: {e}")

                    refreshServerList()

                except Exception as e:
                    debug_print(f"Error in fetchAndAdd: {e}")
                    msglog_tab.toast(type="ERROR", title="Error", description=f"Failed to add server: {str(e)}")
                finally:
                    try:
                        add_server_button.loading = False
                        debug_print("Removed loading state")
                    except Exception as e:
                        debug_print(f"Error removing loading state: {e}")

            try:
                debug_print("Creating async task")
                bot.loop.create_task(fetchAndAdd())
            except Exception as e:
                debug_print(f"Error creating task: {e}")
                try:
                    add_server_button.loading = False
                except:
                    pass
                msglog_tab.toast(type="ERROR", title="Error", description=f"Failed to create task: {str(e)}")

        def removeServerFromWatch(server_id):
            if not validateServerId(server_id, server_id_input):
                return

            watch_servers = load_servers()
            for server in watch_servers:
                if server["id"] == server_id:
                    watch_servers.remove(server)
                    save_servers(watch_servers)
                    msglog_tab.toast(type="SUCCESS", title="Server removed", description=f"Removed {server['name']} from monitored servers")
                    server_id_input.value = ""
                    refreshServerList()
                    return

            msglog_tab.toast(type="WARNING", title="Server not found", description=f"Server ID {server_id} is not in monitored servers")

        async def testWebhookUI():
            test_button.loading = True
            config = load_config()
            timestamp = get_current_time()
            embed_data = {
                "title": "🧪 UI Webhook Test",
                "description": "This is a test message sent from the Message Logger UI.",
                "color": 0x00FF00,
                "fields": [
                    {"name": "⏰ Timestamp", "value": timestamp, "inline": True},
                ],
                "footer": {"text": f"{config['custom_username']} - UI Test"},
                "timestamp": datetime.utcnow().isoformat()
            }

            try:
                await send_to_webhook(config["main_webhook"], {"username": config["custom_username"], "avatar_url": config["custom_avatar_url"], "embeds": [embed_data]})
                msglog_tab.toast(type="SUCCESS", title="Test successful", description="Test message sent to webhook!")
            except Exception as e:
                debug_print(f"Test webhook error: {e}")
                msglog_tab.toast(type="ERROR", title="Test failed", description=f"Failed to send test message: {str(e)}")
            finally:
                test_button.loading = False

        def refreshServerList():
            try:
                watch_servers = load_servers()
                debug_print(f"Refreshing server list. Current servers: {watch_servers}")
                if watch_servers:
                    server_list_content = "\n".join([f"• {server['name']} (`{server['id']}`)" for server in watch_servers])
                else:
                    server_list_content = "*No servers are being monitored*"
                server_list_text.content = server_list_content
                debug_print(f"Server list updated to: {server_list_content}")
            except Exception as e:
                debug_print(f"Error in refreshServerList: {e}")
                server_list_text.content = "*Error loading server list*"

        return addServerToWatch, removeServerFromWatch, testWebhookUI, refreshServerList

    # Create UI Tab
    msglog_tab = Tab(name="Message Logger", title="Message Logger", icon="message")
    main_container = msglog_tab.create_container(type="columns", gap=4)

    # Configuration Section
    config_card = main_container.create_card(height="full", width="full", gap=4)
    config_card.create_ui_element(UI.Text, content="Configuration", size="xl", weight="bold")

    config = load_config()
    setMainWebhook, setImageWebhook, setCustomUsername, setCustomAvatar = updateWebhookSettings()

    # Webhook URLs
    webhook_group = config_card.create_group(type="columns", gap=3, full_width=True)
    main_webhook_input = webhook_group.create_ui_element(UI.Input, label="Main Webhook URL", placeholder=config["main_webhook"], onInput=setMainWebhook, full_width=True)
    image_webhook_input = webhook_group.create_ui_element(UI.Input, label="Image Dump Webhook URL", placeholder=config["image_dump_webhook"], onInput=setImageWebhook, full_width=True)

    # Custom Settings
    custom_group = config_card.create_group(type="columns", gap=3, full_width=True)
    username_input = custom_group.create_ui_element(UI.Input, label="Custom Username", placeholder=config["custom_username"], onInput=setCustomUsername, full_width=True)
    avatar_input = custom_group.create_ui_element(UI.Input, label="Custom Avatar URL", placeholder=config["custom_avatar_url"], onInput=setCustomAvatar, full_width=True)

    # Logging Options
    config_card.create_ui_element(UI.Text, content="Logging Options", size="lg", weight="bold")
    (
        toggleDeletedLogs, toggleEditedLogs, toggleBulkLogs,
        toggleAttachmentLogs, toggleDMLogs, toggleGroupLogs, toggleDebug
    ) = updateLogSettings()

    logging_group = config_card.create_group(type="columns", gap=3, full_width=True)
    deleted_toggle = logging_group.create_ui_element(UI.Toggle, label="Log Deleted Messages", checked=config["log_deleted"], onChange=toggleDeletedLogs)
    edited_toggle = logging_group.create_ui_element(UI.Toggle, label="Log Edited Messages", checked=config["log_edited"], onChange=toggleEditedLogs)

    logging_group2 = config_card.create_group(type="columns", gap=3, full_width=True)
    bulk_toggle = logging_group2.create_ui_element(UI.Toggle, label="Log Bulk Deleted", checked=config["log_bulk_deleted"], onChange=toggleBulkLogs)
    attachment_toggle = logging_group2.create_ui_element(UI.Toggle, label="Log Attachments", checked=config["log_attachments"], onChange=toggleAttachmentLogs)

    # DM/Group toggles
    logging_group3 = config_card.create_group(type="columns", gap=3, full_width=True)
    dm_toggle = logging_group3.create_ui_element(
        UI.Toggle,
        label="Log DMs",
        checked=config.get("log_dm", True),
        onChange=toggleDMLogs
    )
    group_toggle = logging_group3.create_ui_element(
        UI.Toggle,
        label="Log Groups",
        checked=config.get("log_group", True),
        onChange=toggleGroupLogs
    )

    # Debug Toggle
    debug_group = config_card.create_group(type="columns", gap=3, full_width=True)
    debug_toggle = debug_group.create_ui_element(
        UI.Toggle,
        label="Debug Mode",
        checked=config.get("debug", False),
        onChange=toggleDebug
    )

    # Server Management Section
    server_card = main_container.create_card(height="full", width="full", gap=4)
    server_card.create_ui_element(UI.Text, content="Server Management", size="xl", weight="bold")

    addServerToWatch, removeServerFromWatch, testWebhookUI, refreshServerList = updateServerManagement()

    # Store input values globally
    current_server_id = ""

    def on_server_input(value):
        nonlocal current_server_id
        current_server_id = value
        validateServerId(value, server_id_input)
        debug_print(f"Server input changed to: {value}")

    def on_add_server_click():
        debug_print(f"Add server button clicked with value: {current_server_id}")
        addServerToWatch(current_server_id)

    def on_remove_server_click():
        debug_print(f"Remove server button clicked with value: {current_server_id}")
        removeServerFromWatch(current_server_id)

    # Add/Remove Server in one row (merged input)
    server_input_group = server_card.create_group(type="columns", gap=3, full_width=True)
    server_id_input = server_input_group.create_ui_element(
        UI.Input,
        label="Server ID",
        placeholder="Enter server ID to monitor or remove",
        onInput=on_server_input,
        full_width=True
    )

    # Buttons in one row
    button_group = server_card.create_group(type="columns", gap=3, full_width=True)
    add_server_button = button_group.create_ui_element(UI.Button, label="Add Server", onClick=on_add_server_click, full_width=False, color="primary")
    remove_server_button = button_group.create_ui_element(UI.Button, label="Remove Server", onClick=on_remove_server_click, full_width=False, color="primary")
    test_button = button_group.create_ui_element(UI.Button, label="Test Webhook", onClick=testWebhookUI, full_width=False, color="primary")

    # Server List
    server_card.create_ui_element(UI.Text, content="Monitored Servers", size="lg", weight="bold")
    server_list_text = server_card.create_ui_element(UI.Text, content="Loading...", size="sm")

    # Initialize server list
    refreshServerList()

    msglog_tab.render()

messageLogger()