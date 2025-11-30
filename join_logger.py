import json
import asyncio
import aiohttp
import discord
import os

@nightyScript(
    name="Join Logger",
    author="Syn",
    description="Logs all Joins to all discord servers that the bot is in.",
    usage="UI"
)
def JoinLogger():
    import os
    import json
    import asyncio
    import aiohttp
    import discord

    # Global variables for settings
    global join_logging_enabled, webhook_url, guild_ids
    join_logging_enabled = False
    webhook_url = ""
    guild_ids = set()

    # Config file path (script-relative)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, "scriptSettings", "join_logger_config.json")

    def load_config():
        global webhook_url, join_logging_enabled, guild_ids
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    webhook_url = config.get("webhook_url", "")
                    join_logging_enabled = config.get("join_logging_enabled", False)
                    saved_ids = config.get("guild_ids", [])
                    if isinstance(saved_ids, list):
                        guild_ids.update(int(g) for g in saved_ids)
            else:
                print(f"[JoinLogger] No config file found, using defaults")
        except Exception as e:
            print(f"[JoinLogger] Error loading config: {e}")

    def save_config():
        global webhook_url, join_logging_enabled, guild_ids
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            config = {
                "webhook_url": webhook_url,
                "join_logging_enabled": join_logging_enabled,
                "guild_ids": list(guild_ids),
            }
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"[JoinLogger] Error saving config: {e}")

    # Load config on startup
    load_config()

    async def on_ready():
        global guild_ids
        if not guild_ids:
            guild_ids = {g.id for g in bot.guilds}
            print(f"[JoinLogger] Initialized guild_ids with {len(guild_ids)} current guilds")
            save_config()
        else:
            print(f"[JoinLogger] Using {len(guild_ids)} guild_ids loaded from config")

    @bot.command(name="testjoinlog", description="Test command")
    async def testjoinlog(ctx):
        await ctx.send("Test command works!")

    @bot.listen('on_member_join')
    async def on_member_join_listener(member):
        if not join_logging_enabled:
            return
        
        if member.guild.id not in guild_ids:
            return
        
        if not webhook_url or not webhook_url.startswith("https://"):
            return
        
        content = (
            f":green_circle: Member joined: **{member}** (<@{member.id}>)\n"
            f"Guild: **{member.guild.name}** (`{member.guild.id}`)"
        )
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    webhook_url,
                    json={"content": content},
                    timeout=10
                ) as resp:
                    if resp.status >= 400:
                        error_text = await resp.text()
                        print(f"[JoinLogger] Webhook error {resp.status}: {error_text}")
            except Exception as e:
                print(f"[JoinLogger] Failed to send webhook: {e}")

    @bot.listen('on_member_remove')
    async def on_member_remove_listener(member):
        
        if not join_logging_enabled:
            return
        
        if member.guild.id not in guild_ids:
            return
        
        if not webhook_url or not webhook_url.startswith("https://"):
            return
        
        content = (
            f":red_circle: Member left: **{member}** (<@{member.id}>)\n"
            f"Guild: **{member.guild.name}** (`{member.guild.id}`)"
        )
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    webhook_url,
                    json={"content": content},
                    timeout=10
                ) as resp:
                    if resp.status >= 400:
                        error_text = await resp.text()
                        print(f"[JoinLogger] Webhook error {resp.status}: {error_text}")
            except Exception as e:
                print(f"[JoinLogger] Failed to send leave webhook: {e}")

    @bot.command(usage="joinlog [enable|disable|remove <guild_id>]", description="Controls the join logger")
    async def joinlog(ctx, *args):
        global join_logging_enabled, guild_ids, webhook_url
        
        
        if not args:
            await ctx.message.delete()
            
            # Create status message
            status = "✅ ENABLED" if join_logging_enabled else "❌ DISABLED"
            webhook_status = "✅ CONFIGURED" if webhook_url else "❌ NOT SET"
            guild_count = len(guild_ids)
            
            help_text = (
                f"**Join Logger Status**\n"
                f"• Logging: {status}\n"
                f"• Webhook: {webhook_status}\n"
                f"• Guilds: {guild_count} monitored\n\n"
                f"**Available Commands:**\n"
                f"• `<p>joinlog enable` - Start logging joins\n"
                f"• `<p>joinlog disable` - Stop logging joins\n"
                f"• `<p>joinlog remove <guild_id>` - Remove guild from monitoring\n\n"
                f"**UI Controls:**\n"
                f"• Use the Join Logger tab to set webhook URL\n"
                f"• Toggle logging on/off from the UI"
            )
            
            msg = await ctx.send(help_text)
            await asyncio.sleep(15)
            await msg.delete()
            return
        
        action = args[0].lower()
        guild_id = None
        
        if len(args) > 1:
            try:
                guild_id = int(args[1])
            except ValueError:
                await ctx.message.delete()
                msg = await ctx.send("Invalid guild ID format.")
                await asyncio.sleep(10)
                await msg.delete()
                return
        
        if action == "enable":
            join_logging_enabled = True
            save_config()
            await ctx.message.delete()
            msg = await ctx.send("Join logging has been **enabled**.")
            await asyncio.sleep(10)
            await msg.delete()
        elif action == "disable":
            join_logging_enabled = False
            save_config()
            await ctx.message.delete()
            msg = await ctx.send("Join logging has been **disabled**.")
            await asyncio.sleep(10)
            await msg.delete()
        elif action == "remove":
            if guild_id is None:
                await ctx.message.delete()
                msg = await ctx.send("Please provide a guild ID: `<p>joinlog remove <guild_id>`")
                await asyncio.sleep(10)
                await msg.delete()
                return
            
            if guild_id not in guild_ids:
                await ctx.message.delete()
                msg = await ctx.send(f"Guild ID `{guild_id}` is not currently being logged.")
                await asyncio.sleep(10)
                await msg.delete()
                return
            
            guild_ids.remove(guild_id)
            save_config()
            await ctx.message.delete()
            msg = await ctx.send(f"Removed guild ID `{guild_id}` from join logging.")
            await asyncio.sleep(10)
            await msg.delete()
        else:
            await ctx.message.delete()
            msg = await ctx.send("Invalid action. Use `enable`, `disable`, or `remove`.")
            await asyncio.sleep(10)
            await msg.delete()

    async def saveWebhookSettings():
        global webhook_url
        url = str(webhook_url_input.value).strip()
        
        if not url:
            msg = await ctx.send("Please enter a webhook URL.")
            await asyncio.sleep(10)
            await msg.delete()
            join_logger_tab.toast(title="ERROR", description="Please enter a webhook URL.", type="ERROR")
            return
        
        if not url.startswith("https://discord.com/api/webhooks/"):
            join_logger_tab.toast(title="INVALID URL", description="Must be a Discord webhook URL.", type="ERROR")
            return
        
        webhook_url = url
        save_config()
        join_logger_tab.toast(title="SUCCESS", description="Webhook URL saved!", type="SUCCESS")

    async def toggleLogging():
        global join_logging_enabled
        join_logging_enabled = not join_logging_enabled
        save_config()
        status = "enabled" if join_logging_enabled else "disabled"
        join_logger_tab.toast(title="TOGGLED", description=f"Join logging {status}.", type="SUCCESS")

    # Create UI tab
    join_logger_tab = Tab(name='Join Logger', title="Join Logger", icon="users")
    join_logger_container = join_logger_tab.create_container(type="rows")
    join_logger_card = join_logger_container.create_card(height="full", width="full", gap=2)

    join_logger_card.create_ui_element(UI.Text, content="Join Logger Settings", size="xl", weight="bold")
    webhook_url_input = join_logger_card.create_ui_element(UI.Input, label="Webhook URL", full_width=True, show_clear_button=True, margin="mb-3")
    save_webhook_button = join_logger_card.create_ui_element(UI.Button, label='Save Webhook', disabled=False, full_width=True, onClick=saveWebhookSettings)
    toggle_button = join_logger_card.create_ui_element(UI.Button, label='Toggle Logging', disabled=False, full_width=True, onClick=toggleLogging)

    join_logger_tab.render()
    
    # Schedule on_ready to run in bot's event loop
    asyncio.run_coroutine_threadsafe(on_ready(), bot.loop)

JoinLogger()