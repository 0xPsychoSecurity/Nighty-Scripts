@nightyScript(
    name="Automatically leave groupchats", 
    author="oncaged",
    description="Automatically leave groupchats when you're added.", 
    usage=".autoleavegc (toggle)"
)
def LeaveGroupchatShit():
    @bot.command()
    async def autoleavegc(ctx):
        await ctx.message.delete()
        current = getConfigData().get("automatically_leave_gc", False)
        print(str(current))
        updated = not current
        updateConfigData("automatically_leave_gc", updated)
        status = "On" if updated else "Off"
        await ctx.send(f"The automatic groupchat leaving script is now {status}", delete_after=3)
    
    @bot.listen('on_private_channel_create')
    async def on_channel_create(channel):
        if getConfigData().get("automatically_leave_gc", False):
            await channel.leave()


LeaveGroupchatShit()
