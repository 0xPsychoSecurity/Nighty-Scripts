@nightyScript(
    name="Impersonate a Person - Fixed",
    author="ogn",
    description="Uses display name to impersonate with webhook", 
    usage="imi <@user> <text>"
)
def imi():
    
    @bot.command(usage="<@user> <message>", description="Uses display name to impersonate with webhook")
    async def imi(ctx, user: discord.User = None, *, message: str = None):
        await ctx.message.delete()

        if not user:
            msg = await ctx.send("Error: You need to provide a user.\n"
                        f"Usage: `{bot.command_prefix}imi <@user> <message>`")
            await asyncio.sleep(10)
            await msg.delete()
            return

        if not message:
            msg = await ctx.send("Error: You need to provide a message.\n"
                        f"Usage: `{bot.command_prefix}imi <@user> <message>`")
            await asyncio.sleep(10)
            await msg.delete()
            return

        try:
            webhook = await ctx.channel.create_webhook(name=user.display_name)
            await webhook.send(message, username=user.display_name, avatar_url=user.avatar.url)

            await webhook.delete()
        except discord.errors.HTTPException as e:
            msg = await ctx.send(f"An error occurred while creating the webhook: {str(e)}")
            await asyncio.sleep(10)
            await msg.delete()
        except Exception as e:
            msg = await ctx.send(f"An unexpected error occurred: {str(e)}")
            await asyncio.sleep(10)
            await msg.delete()

imi()