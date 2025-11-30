@nightyScript(
    name="Restart Nighty Command",
    author="Luxed",
    description="Restart nighty from the (p)restart command, perfect for those who use nighty on a vps",
    usage="(prefix)restart'"
)
def restart():
    @bot.command(name="Restart")
    async def restart(ctx):
        await ctx.message.delete()
        os.execv(sys.executable, ["python"] + sys.argv)

restart()