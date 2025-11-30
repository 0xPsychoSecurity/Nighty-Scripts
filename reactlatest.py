@nightyScript(
    name="Latest Message Reactor",
    author="Syn",
    description="Reacts to the latest message in a Discord channel with a specified emoji.",
    usage="Use (prefix)reactlatest"
)
def LatestMessageReactor():
    import os
    import json
    import asyncio
    import aiohttp
    import discord
    import re
    
    # Global status tracking
    loop_status = {"running": False, "task": None, "channel_id": None, "emoji": None, "guild_id": None}
    
    @bot.command()
    async def reactlatest(ctx, *args):
        """
        Reacts to the latest message in a Discord channel.
        """
        
        # Handle management commands first
        if len(args) == 1 and args[0].lower() in ["stop", "status", "start"]:
            command = args[0].lower()
            
            if command == "stop":
                if loop_status["task"] and not loop_status["task"].done():
                    loop_status["task"].cancel()
                loop_status["running"] = False
                
                stop_msg = await ctx.send("⚠️ Message reactor stopped")
                await asyncio.sleep(5)
                try:
                    await ctx.message.delete()
                    await stop_msg.delete()
                except:
                    pass
                return
            
            if command == "status":
                status_text = "✅ Active" if loop_status["running"] else "❌ Inactive"
                
                # Get channel info
                channel_info = "Not set"
                if loop_status["channel_id"] and loop_status["guild_id"]:
                    try:
                        guild = ctx.bot.get_guild(loop_status["guild_id"])
                        if guild:
                            channel = guild.get_channel(loop_status["channel_id"])
                            if channel:
                                channel_info = f"{channel.mention} ({loop_status['channel_id']})"
                            else:
                                channel_info = str(loop_status["channel_id"])
                        else:
                            channel_info = str(loop_status["channel_id"])
                    except:
                        channel_info = str(loop_status["channel_id"])
                
                status_msg = await ctx.send(f"""```
📊 Message Reactor Status:
========================
Status: {status_text}
Channel: {channel_info}
Emoji: {loop_status['emoji'] or 'Not set'}
========================
```""")
                await asyncio.sleep(10)
                try:
                    await ctx.message.delete()
                    await status_msg.delete()
                except:
                    pass
                return
            
            if command == "start":
                if not loop_status["channel_id"] or not loop_status["emoji"]:
                    error_msg = await ctx.send("❌ No reactor configuration found. Start a new reactor first.")
                    await asyncio.sleep(5)
                    try:
                        await ctx.message.delete()
                        await error_msg.delete()
                    except:
                        pass
                    return
                
                if not loop_status["running"]:
                    # Find the channel and guild again
                    target_channel = None
                    target_guild = None
                    
                    for guild in ctx.bot.guilds:
                        channel = guild.get_channel(loop_status["channel_id"])
                        if channel:
                            target_channel = channel
                            target_guild = guild
                            break
                    
                    if target_channel and target_guild:
                        loop_status["running"] = True
                        loop_status["task"] = ctx.bot.loop.create_task(monitor_channel(target_channel, target_guild, loop_status["emoji"], ctx.author))
                        
                        start_msg = await ctx.send("✅ Message reactor started")
                        await asyncio.sleep(5)
                        try:
                            await ctx.message.delete()
                            await start_msg.delete()
                        except:
                            pass
                    else:
                        error_msg = await ctx.send("❌ Could not find the configured channel.")
                        await asyncio.sleep(5)
                        try:
                            await ctx.message.delete()
                            await error_msg.delete()
                        except:
                            pass
                else:
                    error_msg = await ctx.send("⚠️ Reactor is already running")
                    await asyncio.sleep(5)
                    try:
                        await ctx.message.delete()
                        await error_msg.delete()
                    except:
                        pass
                return
        
        # If no arguments provided, show help
        if len(args) == 0:
            # Show detailed help
            help_text = """
🔧 Latest Message Reactor Commands:
==================================================

📝 Basic Usage:
   reactlatest <channel_id>
   └─ Uses default emoji (:downvote:)

📝 Custom Emoji:
   reactlatest :emoji: <channel_id>
   └─ Uses specified emoji

📝 Examples:
   reactlatest 123456789012345678
   reactlatest :downvote: 123456789012345678
   reactlatest :thumbsup: 123456789012345678
   reactlatest :custom_emoji: 123456789012345678

📝 Supported Emojis:
   • Standard emojis: :thumbsup:, :downvote:, :heart:, :laughing:
   • Custom server emojis: :server_emoji_name:
   • Unicode emojis: 👍, 👎, ❤️, 😂

📝 Management Commands:
   reactlatest stop    - Stop the reactor
   reactlatest status  - Show current status
   reactlatest start   - Resume the reactor

📝 How to find Channel ID:
   1. Right-click on a channel in Discord
   2. Click 'Copy Channel ID' (enable Developer Mode first)
   3. Paste the ID in the command

📝 Notes:
   • You must have permission to add reactions in the target channel
   • The script will skip your own messages
   • Default emoji is :downvote: if not specified
   • Only one reactor can run at a time
==================================================
            """
            await ctx.send(f"```{help_text}```")
            return
        
        # Parse arguments
        if len(args) == 1:
            # Only channel ID provided
            try:
                channel_id = int(args[0])
                emoji = ":downvote:"  # Use default emoji
            except (ValueError, TypeError):
                await ctx.send("❌ Invalid channel ID. Channel ID must be a number.")
                return
        elif len(args) == 2:
            # Emoji and channel ID provided
            emoji = args[0]
            try:
                channel_id = int(args[1])
            except (ValueError, TypeError):
                await ctx.send("❌ Invalid channel ID. Channel ID must be a number.")
                return
        else:
            await ctx.send("❌ Too many arguments. Use `reactlatest` for help.")
            return
        
        # Get the target channel - search all servers the bot is in
        target_channel = None
        target_guild = None
        
        for guild in ctx.bot.guilds:
            channel = guild.get_channel(channel_id)
            if channel:
                target_channel = channel
                target_guild = guild
                break
        
        if not target_channel:
            error_msg = await ctx.send(f"❌ Channel with ID `{channel_id}` not found in any server.")
            await asyncio.sleep(5)
            try:
                await ctx.message.delete()
                await error_msg.delete()
            except:
                pass
            return
        
        # Stop any existing reactor
        if loop_status["task"] and not loop_status["task"].done():
            loop_status["task"].cancel()
        
        # Update global status
        loop_status["running"] = True
        loop_status["channel_id"] = channel_id
        loop_status["emoji"] = emoji
        loop_status["guild_id"] = target_guild.id
        
        # React to the last 5 messages and then start monitoring
        status_msg = await ctx.send(f"🔍 Starting to react to messages in {target_channel.mention} ({target_guild.name}) with {emoji}")
        
        # Delete the command and status message after 5 seconds
        await asyncio.sleep(5)
        try:
            await ctx.message.delete()
            await status_msg.delete()
        except:
            pass  # Ignore if can't delete
        
        # React to the last 5 messages first
        try:
            message_count = 0
            async for msg in target_channel.history(limit=5):
                if msg.author == ctx.author:
                    continue  # Skip own messages
                
                try:
                    # Handle emoji - could be actual emoji object or text
                    if hasattr(emoji, 'name'):
                        # Actual emoji object from Discord
                        await msg.add_reaction(emoji)
                        message_count += 1
                    elif isinstance(emoji, str) and emoji.startswith(":") and emoji.endswith(":"):
                        # Text emoji format like :downvote:
                        emoji_name = emoji[1:-1]
                        # Try to find the custom emoji in the target guild
                        custom_emoji = discord.utils.get(target_guild.emojis, name=emoji_name)
                        if custom_emoji:
                            await msg.add_reaction(custom_emoji)
                            message_count += 1
                        else:
                            # Try to add as a standard emoji (unicode)
                            await msg.add_reaction(emoji)
                            message_count += 1
                    else:
                        # Direct emoji or unicode character
                        await msg.add_reaction(emoji)
                        message_count += 1
                        
                except discord.Forbidden:
                    continue  # Skip if can't add reaction
                except Exception:
                    continue  # Skip other errors
        
        except discord.Forbidden:
            error_msg = await ctx.send(f"❌ Don't have permission to read messages in {target_channel.mention}.")
            await asyncio.sleep(5)
            try:
                await ctx.message.delete()
                await error_msg.delete()
            except:
                pass
            return
        except Exception as e:
            error_msg = await ctx.send(f"❌ Error fetching past messages: {e}")
            await asyncio.sleep(5)
            try:
                await ctx.message.delete()
                await error_msg.delete()
            except:
                pass
            return
        
        completion_msg = await ctx.send(f"✅ Reacted to {message_count} recent messages. Now monitoring for new messages...")
        
        # Delete completion message after 5 seconds
        await asyncio.sleep(5)
        try:
            await completion_msg.delete()
        except:
            pass  # Ignore if can't delete
        
        # Start monitoring for new messages
        last_message_id = None
        try:
            async for msg in target_channel.history(limit=1):
                last_message_id = msg.id
        except:
            pass
        
        # Create a monitoring task
        loop_status["task"] = ctx.bot.loop.create_task(monitor_channel(target_channel, target_guild, emoji, ctx.author))

    # Standalone monitor function
    async def monitor_channel(target_channel, target_guild, emoji, user_who_started):
        last_message_id = None
        try:
            async for msg in target_channel.history(limit=1):
                last_message_id = msg.id
        except:
            pass
        
        while loop_status["running"]:
            try:
                # Get the latest message
                latest_messages = []
                async for msg in target_channel.history(limit=5):
                    latest_messages.append(msg)
                
                # Process messages that are newer than our last tracked message
                for msg in latest_messages:
                    if msg.author == user_who_started:
                        continue  # Skip own messages
                    
                    # If this message is newer than our last tracked message
                    if last_message_id is None or msg.id > last_message_id:
                        try:
                            # Handle emoji - could be actual emoji object or text
                            if hasattr(emoji, 'name'):
                                # Actual emoji object from Discord
                                await msg.add_reaction(emoji)
                            elif isinstance(emoji, str) and emoji.startswith(":") and emoji.endswith(":"):
                                # Text emoji format like :downvote:
                                emoji_name = emoji[1:-1]
                                # Try to find the custom emoji in the target guild
                                custom_emoji = discord.utils.get(target_guild.emojis, name=emoji_name)
                                if custom_emoji:
                                    await msg.add_reaction(custom_emoji)
                                else:
                                    # Try to add as a standard emoji (unicode)
                                    await msg.add_reaction(emoji)
                            else:
                                # Direct emoji or unicode character
                                await msg.add_reaction(emoji)
                            
                            # Update the last message ID to this message
                            last_message_id = msg.id
                            
                        except discord.Forbidden:
                            continue  # Skip if can't add reaction
                        except Exception:
                            continue  # Skip other errors
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                await asyncio.sleep(5)  # Wait longer on error
        
        loop_status["running"] = False

LatestMessageReactor()
