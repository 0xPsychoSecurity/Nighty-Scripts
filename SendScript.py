# The original author was: Luxed

# Update V1.1

## --- Improvements: ---

# - A better way to send the script instead of DM
# - Now it sends the script in the channel you ran the command in
# - As the previous version required you to have an open DM with the user

@nightyScript(
    name="Send Script",
    author="30_3_",
    description="Sends a specific script to the current channel. If you misspell the name, it suggests similar scripts.",
    usage="Use [p]sendscript {script name}"
)
def sendscript():
    @bot.command()
    async def sendscript(ctx, script_name: str):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            showToast(
                text="I don't have permission to delete messages in this channel.",
                type_="ERROR",
                title="SendScript Error"
            )
        except discord.HTTPException as e:
            showToast(
                text=f"Failed to delete the command message due to `{e}`.",
                type_="ERROR",
                title="SendScript Error"
            )

        scripts_path = getScriptsPath()

        if not os.path.exists(scripts_path):
            showToast(
                text=f"The scripts folder `{scripts_path}` does not exist.",
                type_="ERROR",
                title="SendScript Error"
            )
            return

        if script_name.endswith(".py"):
            script_name = script_name[:-3]

        script_path = os.path.join(scripts_path, f"{script_name}.py")

        if not os.path.exists(script_path):
            available_scripts = [f for f in os.listdir(scripts_path) if f.endswith(".py")]
            similar_scripts = [s[:-3] for s in available_scripts if script_name.lower() in s.lower()]

            if similar_scripts:
                similar_scripts_str = ", ".join([f"`{s}`" for s in similar_scripts])
                await ctx.send(f"Script `{script_name}` not found. Did you mean: {similar_scripts_str}?")
                showToast(
                    text=f"Script `{script_name}` not found. Did you mean: {similar_scripts_str}?",
                    type_="ERROR",
                    title="SendScript Error"
                )
            else:
                await ctx.send(f"Script `{script_name}` not found in `{scripts_path}`.")
                showToast(
                    text=f"Script `{script_name}` not found in `{scripts_path}`.",
                    type_="ERROR",
                    title="SendScript Error"
                )
            return

        try:
            with open(script_path, "rb") as script_file:
                await ctx.channel.send(
                    content=f"📜 **Script:** `{script_name}.py`",
                    file=discord.File(script_file, f"{script_name}.py")
                )
            
            showToast(
                text=f"Script `{script_name}` posted in #{ctx.channel.name}.",
                type_="SUCCESS",
                title="SendScript Success"
            )

        except discord.Forbidden:
            showToast(
                text=f"I don't have permission to send messages in #{ctx.channel.name}.",
                type_="ERROR",
                title="SendScript Error"
            )
        except discord.HTTPException as e:
            showToast(
                text=f"Failed to send script due to `{e}`.",
                type_="ERROR",
                title="SendScript Error"
            )
        except Exception as e:
            showToast(
                text=f"Unexpected error sending script: `{e}`",
                type_="ERROR",
                title="SendScript Error"
            )

sendscript()
