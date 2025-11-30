@nightyScript(
    name="Riskserver",
    author="Polak",
    description="Check for a server with dangerous permissions.", 
    usage="riskserver"
)
def check_riskserver():
    
    @bot.command(description="Show you all servers with dangerous permissions.")
    async def riskserver(ctx):
        await ctx.message.delete()
        
        admins = []
        bots = []
        kicks = []
        bans = []
        manage_guild = []
        manage_roles = []
        manage_webhooks = []
        manage_channels = []
        manage_threads = []
        timeout_members = []
        manage_messages = []
        manage_nicknames = []
        everyone = []

        for guild in bot.guilds:
            if guild.me.guild_permissions.administrator:
                admins.append(discord.utils.escape_markdown(guild.name))
            else:
                if guild.me.guild_permissions.manage_guild:
                    manage_guild.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.manage_roles:
                    manage_roles.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.manage_webhooks:
                    manage_webhooks.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.manage_channels:
                    manage_channels.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.manage_threads:
                    manage_threads.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.moderate_members:
                    timeout_members.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.manage_messages:
                    manage_messages.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.manage_nicknames:
                    manage_nicknames.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.mention_everyone:
                    everyone.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.ban_members:
                    bans.append(discord.utils.escape_markdown(guild.name))
                if guild.me.guild_permissions.kick_members:
                    kicks.append(discord.utils.escape_markdown(guild.name))

        response = []

        if admins:
            adminPermServers = f"📋 __Servers with Admin Permission__: **{len(admins)}**\n- " + "\n- ".join(admins)
            response.append(adminPermServers)

        if manage_guild:
            manageGuildPermServers = f"\n\n🛠 __Servers with Manage Guild Permission__: **{len(manage_guild)}**\n- " + "\n- ".join(manage_guild)
            response.append(manageGuildPermServers)

        if manage_roles:
            manageRolesPermServers = f"\n\n🎭 __Servers with Manage Roles Permission__: **{len(manage_roles)}**\n- " + "\n- ".join(manage_roles)
            response.append(manageRolesPermServers)

        if manage_webhooks:
            manageWebhooksPermServers = f"\n\n🔗 __Servers with Manage Webhooks Permission__: **{len(manage_webhooks)}**\n- " + "\n- ".join(manage_webhooks)
            response.append(manageWebhooksPermServers)

        if manage_channels:
            manageChannelsPermServers = f"\n\n📺 __Servers with Manage Channels Permission__: **{len(manage_channels)}**\n- " + "\n- ".join(manage_channels)
            response.append(manageChannelsPermServers)

        if manage_threads:
            manageThreadsPermServers = f"\n\n🧵 __Servers with Manage Threads Permission__: **{len(manage_threads)}**\n- " + "\n- ".join(manage_threads)
            response.append(manageThreadsPermServers)

        if timeout_members:
            timeoutMembersPermServers = f"\n\n⏱ __Servers with Timeout Members Permission__: **{len(timeout_members)}**\n- " + "\n- ".join(timeout_members)
            response.append(timeoutMembersPermServers)

        if manage_messages:
            manageMessagesPermServers = f"\n\n📨 __Servers with Manage Messages Permission__: **{len(manage_messages)}**\n- " + "\n- ".join(manage_messages)
            response.append(manageMessagesPermServers)

        if manage_nicknames:
            manageNicknamesPermServers = f"\n\n📝 __Servers with Manage Nicknames Permission__: **{len(manage_nicknames)}**\n- " + "\n- ".join(manage_nicknames)
            response.append(manageNicknamesPermServers)

        if everyone:
            mentionEveryonePermServers = f"\n\n📢 __Servers with everyone Permission__: **{len(everyone)}**\n- " + "\n- ".join(everyone)
            response.append(mentionEveryonePermServers)

        if bans:
            banPermServers = f"\n\n⛔ __Servers with Ban Permission__: **{len(bans)}**\n- " + "\n- ".join(bans)
            response.append(banPermServers)

        if kicks:
            kickPermServers = f"\n\n👢 __Servers with Kick Permission__: **{len(kicks)}**\n- " + "\n- ".join(kicks)
            response.append(kickPermServers)

        async def send_long_message(ctx, message, max_length=2000):
            sent_messages = []
            if len(message) > max_length:
                for i in range(0, len(message), max_length):
                    part = message[i:i + max_length]
                    msg = await ctx.send(part)
                    sent_messages.append(msg)
            else:
                msg = await ctx.send(message)
                sent_messages.append(msg)
            return sent_messages

        if response:
            sent_messages = await send_long_message(ctx, ''.join(response))
            await asyncio.sleep(60)
            for msg in sent_messages:
                await msg.delete()
        else:
            await ctx.send("No servers found with dangerous permissions.")

check_riskserver()