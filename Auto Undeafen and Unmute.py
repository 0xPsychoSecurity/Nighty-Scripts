@nightyScript(
    name="Auto Undeafen and Unmute",
    author="Polak",
    description="Automatically undeafens and unmutes if you are muted or deafened.", 
    usage="neverdeaf on/off"
)
def AutoUndeafenAndUnmute():
    async def on_ready():
        global auto_undeafen_enabled
        auto_undeafen_enabled = True # True or False

    @bot.listen('on_voice_state_update')
    async def on_voice_state_update(member, before, after):
        global auto_undeafen_enabled

        if not auto_undeafen_enabled:
            return

        if member.id != bot.user.id:
            return

        if (before.self_deaf == False and after.self_deaf == True) or (before.deaf == False and after.deaf == True):
            if before.self_deaf == False and after.self_deaf == True:
                return
            
            try:
                await member.edit(deafen=False)
                print("Bot was deafened. Automatically undeafened.")
            except discord.Forbidden:
                print("Bot does not have the permission to undeafen.")
            except discord.HTTPException as e:
                print(f"An error occurred while trying to undeafen: {e}")

        if (before.self_mute == False and after.self_mute == True) or (before.mute == False and after.mute == True):
            if before.self_mute == False and after.self_mute == True:
                return

            try:
                await member.edit(mute=False)
                print("Bot was muted. Automatically unmuted.")
            except discord.Forbidden:
                print("Bot does not have the permission to unmute.")
            except discord.HTTPException as e:
                print(f"An error occurred while trying to unmute: {e}")

    @bot.command(usage="on/off", description="Toggles auto-undeafen and unmute on or off.")
    async def neverdeaf(ctx, state: str = None):
        global auto_undeafen_enabled

        await ctx.message.delete()

        if state is None:
            msg = await ctx.send("Please provide a valid option: `on` or `off`. Example: `.neverdeaf on` or `.neverdeaf off`.")
            await asyncio.sleep(10)
            await msg.delete()
            return

        if state.lower() == "on":
            auto_undeafen_enabled = True
            msg = await ctx.send("Auto-undeafen and unmute have been **enabled**.")
        elif state.lower() == "off":
            auto_undeafen_enabled = False
            msg = await ctx.send("Auto-undeafen and unmute have been **disabled**.")
        else:
            msg = await ctx.send("Invalid option. Please use `on` or `off`.")

        await asyncio.sleep(10)
        await msg.delete()

    asyncio.run_coroutine_threadsafe(on_ready(), bot.loop)
AutoUndeafenAndUnmute()