@nightyScript(
    name="Permanent Invite Link",
    author="ca0k",
    description="Script to create a permanent invite link without using the server's vanity URL",
    usage="Use (prefix)invite"
)
def permanentInviteLink():
    @bot.command()
    async def invite(ctx):
        await ctx.message.delete()

        guild = ctx.guild
        if guild is None:
            showToast(
                text="This command can only be used in a server.",
                type_="ERROR",
                title="Invite Error"
            )
            return
        
        target_channel = guild.system_channel or next(
            (channel for channel in guild.text_channels if channel.permissions_for(guild.me).create_instant_invite), None
        )

        if not target_channel:
            showToast(
                text="No suitable channel found to create an invite.",
                type_="ERROR",
                title="Invite Error"
            )
            return

        try:
            invite = await target_channel.create_invite(max_age=0, max_uses=0, unique=True)

            pyperclip.copy(invite.url)

            showToast(
                text=f"Permanent invite link: {invite.url} (Copied to clipboard!)",
                type_="SUCCESS",
                title="Invite Created"
            )
        except Exception as e:
            showToast(
                text=f"An error occurred: {e}",
                type_="ERROR",
                title="Invite Error"
            )

permanentInviteLink()
