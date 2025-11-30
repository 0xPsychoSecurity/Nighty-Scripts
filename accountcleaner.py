@nightyScript(
    name="Account Cleaner",
    author="Twister",
    description="Clean your Discord account: remove all friends, leave all servers/groups, delete all your own messages.",
    usage="Click buttons to clean up your account"
)
def accountCleaner():
    import asyncio
    import time
    
    tab = Tab(name="AccountCleaner", icon="broom", title="Account Cleaner")
    container = tab.create_container(type="columns", gap=10)
    card = container.create_card(gap=7)

    infoText = card.create_ui_element(
        UI.Text,
        content="Warning! These buttons will immediately remove all friends, leave all servers and group DMs, and delete all your own messages! This CANNOT be undone.",
        size="sm",
        color="danger"
    )

    nukeBtn = card.create_ui_element(UI.Button, label="🔥 Nuke My Shit 🔥", variant="solid", full_width=True, size="md", color="danger")
    nukeStatus = card.create_ui_element(UI.Text, content="-", size="sm", color="danger")

    deleteFirstBtn = card.create_ui_element(UI.Button, label="Delete All My Messages FIRST", variant="solid", full_width=True, size="sm", color="danger")
    deleteFirstStatus = card.create_ui_element(UI.Text, content="-", size="sm")

    friendBtn = card.create_ui_element(UI.Button, label="Remove All Friends", variant="solid", full_width=True, size="sm")
    friendStatus = card.create_ui_element(UI.Text, content="-", size="sm")

    serverBtn = card.create_ui_element(UI.Button, label="Leave All Servers", variant="solid", full_width=True, size="sm")
    serverStatus = card.create_ui_element(UI.Text, content="-", size="sm")

    groupBtn = card.create_ui_element(UI.Button, label="Leave All Group DMs", variant="solid", full_width=True, size="sm")
    groupStatus = card.create_ui_element(UI.Text, content="-", size="sm")

    async def nuke_my_shit():
        nukeBtn.loading = True
        nukeStatus.content = "🔥 INITIATING NUKE SEQUENCE..."
        
        # Step 1: Delete all messages
        nukeStatus.content = "🔥 STEP 1: Deleting all messages..."
        total_deleted, failed, rate_limit_hits = 0, 0, 0
        channels = list(bot.private_channels) + [ch for g in bot.guilds for ch in g.text_channels if ch.permissions_for(g.me).read_message_history]
        
        for channel_idx, channel in enumerate(channels):
            try:
                channel_name = getattr(channel, 'name', f'DM #{channel_idx}')
                nukeStatus.content = f"🔥 STEP 1: Scanning {channel_name} ({channel_idx+1}/{len(channels)})..."
                
                last_message_id = None
                while True:
                    try:
                        kwargs = {'limit': 100}
                        if last_message_id:
                            kwargs['before'] = last_message_id
                        
                        messages = []
                        async for message in channel.history(**kwargs):
                            if message.author.id == bot.user.id:
                                messages.append(message)
                        
                        if not messages:
                            break
                        
                        for i, message in enumerate(messages):
                            try:
                                await message.delete()
                                total_deleted += 1
                                if i < len(messages) - 1:
                                    await asyncio.sleep(0.1)
                            except discord.Forbidden:
                                failed += 1
                            except discord.HTTPException as e:
                                if "rate limited" in str(e).lower():
                                    rate_limit_hits += 1
                                    retry_after = 1
                                    try:
                                        if hasattr(e, 'retry_after'):
                                            retry_after = e.retry_after
                                    except:
                                        pass
                                    await asyncio.sleep(retry_after)
                                    failed += 1
                                else:
                                    failed += 1
                            except Exception:
                                failed += 1
                        
                        last_message_id = messages[-1].id
                        await asyncio.sleep(0.5)
                        
                    except discord.Forbidden:
                        break
                    except Exception:
                        break
                        
            except Exception:
                failed += 1
        
        nukeStatus.content = f"🔥 STEP 1 COMPLETE: Deleted {total_deleted} messages, failed: {failed}, rate limits hit: {rate_limit_hits}"
        await asyncio.sleep(2)
        
        # Step 2: Leave all group DMs
        nukeStatus.content = "🔥 STEP 2: Leaving all group DMs..."
        count, failed = 0, 0
        for channel in bot.private_channels:
            if hasattr(channel, "recipients") and len(channel.recipients) > 1:
                try:
                    await channel.leave()
                    count += 1
                    await asyncio.sleep(0.1)
                except discord.HTTPException as e:
                    if "rate limited" in str(e).lower():
                        retry_after = 1
                        try:
                            if hasattr(e, 'retry_after'):
                                retry_after = e.retry_after
                        except:
                            pass
                        await asyncio.sleep(retry_after)
                        failed += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1
        nukeStatus.content = f"🔥 STEP 2 COMPLETE: Left {count} group DMs, failed: {failed}"
        await asyncio.sleep(2)
        
        # Step 3: Leave all servers
        nukeStatus.content = "🔥 STEP 3: Leaving all servers..."
        count, failed = 0, 0
        for guild in bot.guilds:
            try:
                await guild.leave()
                count += 1
                await asyncio.sleep(0.2)
            except discord.HTTPException as e:
                if "rate limited" in str(e).lower():
                    retry_after = 1
                    try:
                        if hasattr(e, 'retry_after'):
                            retry_after = e.retry_after
                    except:
                        pass
                    await asyncio.sleep(retry_after)
                    failed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        nukeStatus.content = f"🔥 STEP 3 COMPLETE: Left {count} servers, failed: {failed}"
        await asyncio.sleep(2)
        
        # Step 4: Remove all friends
        nukeStatus.content = "🔥 STEP 4: Removing all friends..."
        count, failed = 0, 0
        for friend in bot.friends:
            try:
                await friend.remove()
                count += 1
                await asyncio.sleep(0.1)
            except discord.HTTPException as e:
                if "rate limited" in str(e).lower():
                    retry_after = 1
                    try:
                        if hasattr(e, 'retry_after'):
                            retry_after = e.retry_after
                    except:
                        pass
                    await asyncio.sleep(retry_after)
                    failed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        nukeStatus.content = f"🔥 STEP 4 COMPLETE: Removed {count} friends, failed: {failed}"
        await asyncio.sleep(2)
        
        # Final status
        nukeStatus.content = "🔥 NUKE COMPLETE! Account wiped clean."
        nukeBtn.loading = False
        tab.toast(title="Account Nuked", description="All operations completed successfully", type="INFO")

    async def delete_all_my_messages_first():
        deleteFirstBtn.loading = True
        total_deleted, failed, rate_limit_hits = 0, 0, 0
        
        # Get all channels (DMs, group DMs, and server channels)
        channels = list(bot.private_channels) + [ch for g in bot.guilds for ch in g.text_channels if ch.permissions_for(g.me).read_message_history]
        
        deleteFirstStatus.content = f"🔍 Scanning {len(channels)} channels for your messages..."
        
        for channel_idx, channel in enumerate(channels):
            try:
                channel_name = getattr(channel, 'name', f'DM #{channel_idx}')
                deleteFirstStatus.content = f"🔍 Scanning {channel_name} ({channel_idx+1}/{len(channels)})..."
                
                # Fetch messages in batches to respect rate limits
                last_message_id = None
                while True:
                    try:
                        # Get messages (limit 100 per request)
                        kwargs = {'limit': 100}
                        if last_message_id:
                            kwargs['before'] = last_message_id
                        
                        messages = []
                        async for message in channel.history(**kwargs):
                            if message.author.id == bot.user.id:
                                messages.append(message)
                        
                        if not messages:
                            break
                        
                        # Delete messages with rate limiting
                        for i, message in enumerate(messages):
                            try:
                                await message.delete()
                                total_deleted += 1
                                
                                # Rate limiting: wait 0.1 seconds between deletions (10 per second max)
                                if i < len(messages) - 1:  # Don't wait after the last message
                                    await asyncio.sleep(0.1)
                                    
                            except discord.Forbidden:
                                failed += 1
                            except discord.HTTPException as e:
                                if "rate limited" in str(e).lower():
                                    rate_limit_hits += 1
                                    # Extract retry time if available
                                    retry_after = 1  # Default 1 second
                                    try:
                                        if hasattr(e, 'retry_after'):
                                            retry_after = e.retry_after
                                    except:
                                        pass
                                    await asyncio.sleep(retry_after)
                                    failed += 1
                                else:
                                    failed += 1
                            except Exception:
                                failed += 1
                        
                        last_message_id = messages[-1].id
                        
                        # Rate limiting between batches
                        await asyncio.sleep(0.5)
                        
                    except discord.Forbidden:
                        break  # Can't access this channel
                    except Exception:
                        break  # Other error, move to next channel
                        
            except Exception:
                failed += 1
        
        deleteFirstStatus.content = f"✅ Deleted {total_deleted} messages, failed: {failed}, rate limits hit: {rate_limit_hits}"
        deleteFirstBtn.loading = False
        tab.toast(title="Messages Deleted First", description=deleteFirstStatus.content, type="INFO")

    async def remove_all_friends():
        friendBtn.loading = True
        count, failed = 0, 0
        for friend in bot.friends:
            try:
                await friend.remove()
                count += 1
                # Rate limiting: wait 0.1 seconds between friend removals
                await asyncio.sleep(0.1)
            except discord.HTTPException as e:
                if "rate limited" in str(e).lower():
                    retry_after = 1
                    try:
                        if hasattr(e, 'retry_after'):
                            retry_after = e.retry_after
                    except:
                        pass
                    await asyncio.sleep(retry_after)
                    failed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        friendStatus.content = f"✅ Removed {count} friends, failed: {failed}"
        friendBtn.loading = False
        tab.toast(title="Friends Removed", description=friendStatus.content, type="INFO")

    async def leave_all_servers():
        serverBtn.loading = True
        count, failed = 0, 0
        for guild in bot.guilds:
            try:
                await guild.leave()
                count += 1
                # Rate limiting: wait 0.2 seconds between server leaves
                await asyncio.sleep(0.2)
            except discord.HTTPException as e:
                if "rate limited" in str(e).lower():
                    retry_after = 1
                    try:
                        if hasattr(e, 'retry_after'):
                            retry_after = e.retry_after
                    except:
                        pass
                    await asyncio.sleep(retry_after)
                    failed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        serverStatus.content = f"✅ Left {count} servers, failed: {failed}"
        serverBtn.loading = False
        tab.toast(title="Servers Left", description=serverStatus.content, type="INFO")

    async def leave_all_groups():
        groupBtn.loading = True
        count, failed = 0, 0
        for channel in bot.private_channels:
            if hasattr(channel, "recipients") and len(channel.recipients) > 1:
                try:
                    await channel.leave()
                    count += 1
                    # Rate limiting: wait 0.1 seconds between group leaves
                    await asyncio.sleep(0.1)
                except discord.HTTPException as e:
                    if "rate limited" in str(e).lower():
                        retry_after = 1
                        try:
                            if hasattr(e, 'retry_after'):
                                retry_after = e.retry_after
                        except:
                            pass
                        await asyncio.sleep(retry_after)
                        failed += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1
        groupStatus.content = f"✅ Left {count} group DMs, failed: {failed}"
        groupBtn.loading = False
        tab.toast(title="Group DMs Left", description=groupStatus.content, type="INFO")

    nukeBtn.onClick = nuke_my_shit
    deleteFirstBtn.onClick = delete_all_my_messages_first
    friendBtn.onClick = remove_all_friends
    serverBtn.onClick = leave_all_servers
    groupBtn.onClick = leave_all_groups

    tab.render()
accountCleaner()
