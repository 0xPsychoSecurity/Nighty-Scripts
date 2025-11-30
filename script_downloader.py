# The original author was: bnly

# Update V1.1

# --- Features --- 
# - Automatic Reload Scripts (you can skip this with <p>dls off)
# - For new scripts it is no longer necessary to use: misc togglescript (Name)
# - Now only detects .py and .txt files

@nightyScript(
    name="Script Downloader (DLS)",
    author="Luxed",
    description="Downloads a .py or .txt attachment from a reply and automatically reloads scripts.",
    usage="<p>dls (off) (when replying to a message with a .py or .txt attachment)"
)
def script_downloader_dls():
    import asyncio
    from pathlib import Path
    import aiohttp
    import traceback
    import io
    import os
    import json
    
    SCRIPTS_DIR = Path(getScriptsPath())
    
    try:
        appdata_path = os.getenv('APPDATA') or os.path.join(os.path.expanduser('~'), '.config')
        if 'local' in appdata_path.lower():
             appdata_path = Path(appdata_path).parent / 'Roaming'

        MISC_DATA_DIR = Path(appdata_path) / 'Nighty Selfbot' / 'data' / 'misc'
        SCRIPTS_JSON_PATH = MISC_DATA_DIR / 'scripts.json'
        os.makedirs(MISC_DATA_DIR, exist_ok=True)
    except Exception as e:
        print(f"[DLS] Could not define path to scripts.json: {e}", type_="ERROR")
        SCRIPTS_JSON_PATH = None

    async def handle_error(ctx, status_msg=None):
        """A centralized function to capture, format, and send the full traceback."""
        error_traceback = traceback.format_exc()
        print(f"An error occurred in DLS Script:\n{error_traceback}", type_="ERROR")

        error_header = "An unexpected error occurred. Full traceback below:"
        
        if len(error_traceback) > 1900:
            error_file = discord.File(
                fp=io.BytesIO(error_traceback.encode('utf-8')),
                filename="dls_error_traceback.txt"
            )
            content = f"{error_header}\nThe error was too long and has been sent as a file."
            if status_msg:
                await status_msg.edit(content=content, attachments=[error_file], delete_after=60)
            else:
                await ctx.send(content=content, file=error_file, delete_after=60)
        else:
            content = f"{error_header}\n```python\n{error_traceback}\n```"
            if status_msg:
                await status_msg.edit(content=content, delete_after=60)
            else:
                await ctx.send(content=content, delete_after=60)

    async def update_scripts_json(script_name: str, status_msg):
        """Reads, updates, and writes the scripts.json file to enable a new script."""
        if not SCRIPTS_JSON_PATH or not os.path.exists(SCRIPTS_JSON_PATH):
            await status_msg.edit(content=f"Warning: `scripts.json` not found at {SCRIPTS_JSON_PATH}. Skipping auto-enable.", delete_after=15)
            return False

        try:
            with open(SCRIPTS_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if script_name not in data.get("enabled", []):
                await status_msg.edit(content=f"Enabling `{script_name}` in configuration...")
                data.setdefault("enabled", []).append(script_name)
                
                with open(SCRIPTS_JSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                print(f"[DLS] Successfully enabled '{script_name}' in scripts.json.", type_="SUCCESS")
                return True
            else:
                print(f"[DLS] Script '{script_name}' is already enabled.", type_="INFO")
                return True # Return True as it's already in the desired state
        except (IOError, json.JSONDecodeError) as e:
            await status_msg.edit(content=f"Error processing `scripts.json`: {e}", delete_after=15)
            print(f"Failed to read or write scripts.json: {e}", type_="ERROR")
            return False

    async def reload_all_scripts(status_msg):
        """Attempts to call the global script reload function."""
        await status_msg.edit(content="Reloading all scripts...")
        print("[DLS] Script reload command executed.", type_="SUCCESS")
        reloadAllScripts()
        return True

    @bot.command(
        name="dls",
        aliases=["downloadscript"],
        description="Downloads an attachment from a reply into the scripts folder."
    )
    async def dls_command(ctx, *, args: str = None):
        """
        Handles the download of an attachment, enables it in config, and reloads scripts.
        """
        await ctx.message.delete()
        status_msg = None

        # --- Check for 'off' argument ---
        do_reload = True
        if args and args.strip().lower() == "off":
            do_reload = False

        try:
            if not (ctx.message.reference and ctx.message.reference.message_id):
                await ctx.send("You must use this command by replying to a message.", delete_after=15)
                return

            replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

            if not replied_message.attachments:
                await ctx.send("The replied message has no attachments.", delete_after=15)
                return

            attachment = replied_message.attachments[0]
            filename = attachment.filename

            # --- File Type Validation ---
            if not (filename.endswith('.py') or filename.endswith('.txt')):
                await ctx.send(f"Invalid file type. Only `.py` and `.txt` files are allowed.", delete_after=15)
                return

            status_msg = await ctx.send(f"Downloading `{filename}`...")
            
            file_path = SCRIPTS_DIR / filename
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(attachment.url) as response:
                    if response.status == 200:
                        with open(file_path, "wb") as f:
                            f.write(await response.read())
                        
                        final_message = f"Successfully saved `{filename}`."

                        # --- Update Config and Reload for .py files ---
                        if filename.endswith('.py'):
                            script_name = Path(filename).stem
                            json_updated = await update_scripts_json(script_name, status_msg)
                            
                            if json_updated:
                                if do_reload:
                                    reloaded = await reload_all_scripts(status_msg)
                                    if reloaded:
                                        final_message += "\nScripts reloaded automatically."
                                    else:
                                        final_message += "\n**Could not reload automatically. Please do it manually.**"
                                else:
                                    final_message += "\nSkipped auto-reload. Please reload manually."
                                    print("[DLS] Skipped auto-reload (user requested 'off').", type_="INFO")
                        
                        await status_msg.edit(content=final_message, delete_after=20)
                    else:
                        await status_msg.edit(content=f"Failed to download. HTTP Status: {response.status}", delete_after=15)
                        print(f"HTTP Error {response.status} downloading {filename}", type_="ERROR")

        except Exception:
            await handle_error(ctx, status_msg)

script_downloader_dls()