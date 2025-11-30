@nightyScript(
    name="Message Deleter",
    author="Polak",
    description="Automates the deletion of messages based on custom settings."
)
def msgdeleterar():
    import json

jsonFilePath = os.path.join(os.path.expandvars(r"%APPDATA%"), "Nighty Selfbot", "data", "scripts", "scriptsettings", "arsettings.json")

default_data = {
    "yourId": 1049775985823846440,
    "deleteInterval": 6400,
    "blacklistedIds": [],
    "deleteEnabled": True
}

os.makedirs(os.path.dirname(jsonFilePath), exist_ok=True)

if not os.path.exists(jsonFilePath):
    print("JSON file not found. Creating a new one...")
    for guild in bot.guilds:
        if guild.owner == bot.user:
            default_data["blacklistedIds"].append(guild.id)
            print(f"Anti-Report | Added: {guild.name} to the blacklist.")

    with open(jsonFilePath, "w", encoding="utf-8") as file:
        json.dump(default_data, file, indent=4)
    print("JSON file created with default values.")
else:
    with open(jsonFilePath, "r", encoding="utf-8") as file:
        data = json.load(file)
        yourId = data.get("yourId", default_data["yourId"])
        deleteInterval = data.get("deleteInterval", default_data["deleteInterval"])
        blacklisted_ids = data.get("blacklistedIds", default_data["blacklistedIds"])
        deleteEnabled = data.get("deleteEnabled", default_data["deleteEnabled"])
        print(f"Message Deleter activated! Interval = {deleteInterval}")

@bot.listen()
async def on_message(message):
    global yourId, deleteInterval, blacklisted_ids, deleteEnabled

    if not deleteEnabled:
        return

    channel = message.channel
    channel_name = channel.name.lower()
    sender_guild_id = message.guild.id if message.guild else None

    if (
        "ticket" not in channel_name
        and "support" not in channel_name
        and message.author.id == yourId
        and sender_guild_id not in blacklisted_ids
    ):
        await asyncio.sleep(int(deleteInterval)) 
        await message.delete()

@bot.command(description="Toggle message deletion on or off")
async def artoggle(ctx):
    global jsonFilePath, deleteEnabled

    await ctx.message.delete()

    deleteEnabled = not deleteEnabled


    with open(jsonFilePath, "r+", encoding="utf-8") as file:
        data = json.load(file)
        data["deleteEnabled"] = deleteEnabled
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate() 

    status = "enabled" if deleteEnabled else "disabled"
    await ctx.send(f"The automatic message deletion has been `{status}.`")
    print(f"Anti-Report | Message deletion has been {status}.")

@bot.command(usage="<seconds>",description="Set the interval for Anti-Report-deletion")
async def arinterval(ctx, newInterval=None):
    await ctx.message.delete()

    if newInterval is None:
        await ctx.send("Interval not specified.")
    else:
        global jsonFilePath

        print(f"Anti-Report | New intervall: {newInterval}")
        try:
            newInterval = int(newInterval)

            with open(jsonFilePath, "r+", encoding="utf-8") as file:
                data = json.load(file)
                data["deleteInterval"] = newInterval
                file.seek(0)  
                json.dump(data, file, indent=4)
                file.truncate()

            await ctx.send(f"Interval set to `{newInterval}` seconds. **Please restart to apply the changes.**")

        except ValueError:
            print("Anti-Report | Invalid interval. Please enter a valid number.")
            await ctx.send("**Invalid interval.** Please enter a `valid` number.")

@bot.command(usage="<add|remove> <guildid>", description="Manage the Anti-Report blacklist")
async def arblacklist(ctx, action=None, server_id=None):
    await ctx.message.delete()

    if action not in ["add", "remove"] or server_id is None:
        await ctx.send("Error: **Usage:** antireportblacklist `<add|remove> <guildid>`")
        return

    global jsonFilePath

    try:
        server_id = int(server_id)

        with open(jsonFilePath, "r+", encoding="utf-8") as file:
            data = json.load(file)
            blacklisted_ids = data.get("blacklistedIds", [])

            if action == "add":
                if server_id not in blacklisted_ids:
                    blacklisted_ids.append(server_id)
                    data["blacklistedIds"] = blacklisted_ids
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    file.truncate()

                    await ctx.send(f"Server ID `{server_id}` added to the blacklist. **Please restart to apply the changes.**")
                    print(f"Server ID {server_id} added to the blacklist.")
                else:
                    await ctx.send(f"Server ID `{server_id}` is already in the blacklist.")
                    print(f"Server ID {server_id} is already blacklisted.")

            elif action == "remove":
                if server_id in blacklisted_ids:
                    blacklisted_ids.remove(server_id)
                    data["blacklistedIds"] = blacklisted_ids
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    file.truncate()

                    await ctx.send(f"Server ID `{server_id}` removed from the blacklist. **Please restart to apply the changes.**")
                    print(f"Server ID {server_id} removed from the blacklist.")
                else:
                    await ctx.send(f"Server ID `{server_id}` is not in the blacklist.")
                    print(f"Server ID {server_id} is not in the blacklist.")

    except ValueError:
        print("Anti-Report | Invalid server ID. Please enter a valid number.")
        await ctx.send("**Invalid server ID.** Please enter a `valid` number.")

@bot.command(description="Change 'yourId' in the Anti-Report settings")
async def archangeid(ctx, new_id=None):
    await ctx.message.delete()

    if new_id is None:
        await ctx.send("Please specify a ID. `Usage: archangeid <new_id>`")
        return

    try:
        new_id = int(new_id)

        global jsonFilePath
        with open(jsonFilePath, "r+", encoding="utf-8") as file:
            data = json.load(file)
            data["yourId"] = new_id
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

        await ctx.send(f"ID has been updated to `{new_id}`. **Please restart to apply the changes.**")
        print(f"Anti Report | ID updated to {new_id}.")

    except ValueError:
        await ctx.send("**Invalid ID.** Please enter a `valid` number.")

@bot.command(description="Display Anti-Report settings")
async def arsettings(ctx):
    await ctx.message.delete()

    with open(jsonFilePath, "r", encoding="utf-8") as file:
        data = json.load(file)
        yourId = data["yourId"]
        deleteInterval = data["deleteInterval"]
        blacklisted_ids = data.get("blacklistedIds", [])

        settings_message = (
            f"```Anti-Report Settings:```\n"
            f"Your ID: `{int(yourId)}`\n"
            f"Delete Intervall: `{int(deleteInterval)}` Seconds\n\n"
        )

        if blacklisted_ids:
            settings_message += f"Blacklist IDs ({len(blacklisted_ids)}):\n"
            for blacklisted_id in blacklisted_ids:
                server = bot.get_guild(blacklisted_id)
                server_name = server.name if server else "Unknown Server"
                settings_message += (
                    f"ID: `{int(blacklisted_id)}` (Server: {server_name})\n"
                )
        else:
            settings_message += "No blacklisted IDs.\n"

        settings_message += "-# If you need help use `arhelp` command"

        max_chars = 2000
        messages = []
        current_message = ""
        for line in settings_message.split("\n"):
            if (
                len(current_message + line) + 3 > max_chars
            ):  
                messages.append(current_message + "...")
                current_message = ""
                break

            current_message += line + "\n"

        if current_message:  
            messages.append(current_message)

        for message in messages:
            await ctx.send(message)

@bot.command(description="Displays a list of all Anti-Report commands")
async def arhelp(ctx):
    await ctx.message.delete()

    def get_prefix():
        config_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Nighty Selfbot", "nighty.config")
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                content = file.read()

            import re
            match = re.search(r'"prefix":\s*"([^"]+)"', content)
            if match:
                return match.group(1)

            return "!"

        except FileNotFoundError:
            return "!" 
        except Exception as e:
            return "!"

    prefix = get_prefix()

    help_message = (
        f"```Anti-Report Commands:```\n"
        f"- {prefix}arhelp - Displays this help message.\n"
        f"- {prefix}artoggle - Toggle message deletion on or off.\n"
        f"- {prefix}arinterval `<seconds>` - Set the interval for message deletion.\n"
        f"- {prefix}arblacklist `<add|remove> <guildid>` - Manage the Anti-Report blacklist.\n"
        f"- {prefix}archangeid `<new_id>` - Change  your ID in the Anti-Report settings.\n"
        f"- {prefix}arsettings - Display current Anti-Report settings.\n"
        f"-# When you run the script for the first time, all servers you own will be blacklisted by default. You can remove them using the `[{get_prefix()}arblacklist]` command."
    )
    
    await ctx.send(help_message)

msgdeleterar()