@nightyScript(
    name="AFK - Offline Replier",
    author="@ca0k",
    description="Auto-reply to DMs when in custom AFK mode; activity dashboard with jump, delete, and selection controls.",
    usage="Configure settings in the Smart Replier tab"
)
def smartOfflineReplier():
    import aiohttp
    import datetime
    import asyncio
    import discord
    import json
    import os

    # Persistence file in Nighty selfbot AppData Roaming scripts/json folder
    APPDATA = os.getenv('APPDATA')
    JSON_DIR = os.path.join(APPDATA, 'Nighty', 'scripts', 'json')
    os.makedirs(JSON_DIR, exist_ok=True)
    PERSISTENCE_FILE = os.path.join(JSON_DIR, "afk_replier_data.json")

    replied_users = {}
    message_log = []
    seen_initial_dms = set()
    MAX_LOG_SIZE = 100

    default_config = {
        "custom_reply": "💤 Currently Offline Right Now 💤, I'll be back shortly! {mention}",
        "reply_delay": 0,
        "delete_after_minutes": 25,
        "webhook_url": "https://discord.com/api/webhooks/1419492926148444251/BHudHhWb4r3TjzTl-ttFljo4Ss5uLrA9X5s3KqMqwAz9Qw6twBhIKXp9IghhsRxoe12C",
        "webhook_enabled": True,
        "active": True,
        "active_statuses": ["invisible"],
        "dm_only": True,
        "cooldown_minutes": 5,
        "allowed_servers": []
    }

    preset_configs = {
        "Default AFK": default_config.copy(),
        "Gaming Mode": {
            "custom_reply": "🎮 Currently gaming, will reply when I'm back! {mention}",
            "reply_delay": 2,
            "delete_after_minutes": 15,
            "webhook_url": default_config["webhook_url"],
            "webhook_enabled": True,
            "active": True,
            "active_statuses": ["invisible", "dnd"],
            "dm_only": True,
            "cooldown_minutes": 3,
            "allowed_servers": []
        },
        "Professional Mode": {
            "custom_reply": "🔔 I'm currently away from keyboard; will respond ASAP. Thanks for your message {mention}.",
            "reply_delay": 1,
            "delete_after_minutes": 30,
            "webhook_url": default_config["webhook_url"],
            "webhook_enabled": True,
            "active": True,
            "active_statuses": ["invisible", "dnd", "idle"],
            "dm_only": False,
            "cooldown_minutes": 10,
            "allowed_servers": []
        },
        "Clean & Simple": {
            "custom_reply": "Currently unavailable. Please leave your message and I'll get back to you soon! {mention}",
            "reply_delay": 0,
            "delete_after_minutes": 0,
            "webhook_url": default_config["webhook_url"],
            "webhook_enabled": False,
            "active": True,
            "active_statuses": ["invisible"],
            "dm_only": True,
            "cooldown_minutes": 5,
            "allowed_servers": []
        },
        "Quick Reply": {
            "custom_reply": "Hey {mention}, I'm AFK but will reply quickly when back!",
            "reply_delay": 0,
            "delete_after_minutes": 20,
            "webhook_url": default_config["webhook_url"],
            "webhook_enabled": True,
            "active": True,
            "active_statuses": ["invisible", "idle"],
            "dm_only": True,
            "cooldown_minutes": 2,
            "allowed_servers": []
        },
        "Do Not Disturb": {
            "custom_reply": "⛔ Currently set to Do Not Disturb. Will respond later! {mention}",
            "reply_delay": 1,
            "delete_after_minutes": 60,
            "webhook_url": default_config["webhook_url"],
            "webhook_enabled": True,
            "active": True,
            "active_statuses": ["dnd"],
            "dm_only": True,
            "cooldown_minutes": 15,
            "allowed_servers": []
        },
    }

    config = default_config.copy()
    ui_refs = {}
    status_updater_running = False

    def save_data():
        nonlocal replied_users, message_log, seen_initial_dms, preset_configs, config
        replied_users_serializable = {f"{k[0]}_{k[1]}": v.isoformat() for k, v in replied_users.items()}
        seen_initial_dms_list = [f"{ch_id}_{auth_id}" for ch_id, auth_id in seen_initial_dms]
        data = {
            "config": config,
            "replied_users": replied_users_serializable,
            "message_log": message_log,
            "seen_initial_dms": seen_initial_dms_list,
            "preset_configs": preset_configs
        }
        with open(PERSISTENCE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data():
        nonlocal replied_users, message_log, seen_initial_dms, preset_configs, config
        if not os.path.exists(PERSISTENCE_FILE):
            save_data()  # Create default file if missing
            return
        try:
            with open(PERSISTENCE_FILE, 'r') as f:
                data = json.load(f)
            loaded_config = data.get("config", {})
            if loaded_config:
                config.update(loaded_config)
            replied_users.clear()
            for key_str, time_str in data.get("replied_users", {}).items():
                parts = key_str.split('_')
                if len(parts) == 2:
                    channel_id = int(parts[0])
                    author_id = int(parts[1])
                    replied_users[(channel_id, author_id)] = datetime.datetime.fromisoformat(time_str)
            message_log.clear()
            message_log.extend(data.get("message_log", []))
            seen_initial_dms.clear()
            for key_str in data.get("seen_initial_dms", []):
                parts = key_str.split('_')
                if len(parts) == 2:
                    seen_initial_dms.add((int(parts[0]), int(parts[1])))
            loaded_presets = data.get("preset_configs", {})
            if loaded_presets:
                preset_configs.update(loaded_presets)
        except Exception as e:
            print(f"Failed to load config, resetting to default: {e}")
            config.clear()
            config.update(default_config)
            save_data()

    def refresh_presets_dropdown():
        if "preset_select" in ui_refs:
            ui_refs["preset_select"].items = [{"id": k, "title": k} for k in sorted(preset_configs.keys())]

    def find_log_by_id(row_id):
        for msg in message_log:
            if msg["id"] == row_id:
                return msg
        return None

    def jump_to_dm(row_id):
        msg = find_log_by_id(row_id)
        if msg and msg["channel_id"] and msg["message_id"]:
            jump_url = f"https://discord.com/channels/@me/{msg['channel_id']}/{msg['message_id']}"
            ui_refs["jump_url_input"].value = jump_url
            ui_refs["jump_url_input"].visible = True
            tab.toast(title="✅ Jump URL Ready", description="Copy the URL from the input field below", type="SUCCESS")

    async def schedule_message_deletion(message, minutes):
        await asyncio.sleep(minutes * 60)
        await message.delete()

    async def log_to_webhook(author, content, channel_id, message_id, is_dm=True):
        if not config["webhook_enabled"] or not config["webhook_url"]:
            return
        async with aiohttp.ClientSession() as session:
            jump_url = f"https://discord.com/channels/@me/{channel_id}/{message_id}" if is_dm else None
            embed = {
                "author": {
                    "name": f"{author.display_name} (@{author.name})",
                    "icon_url": str(author.display_avatar.url)
                },
                "title": "📥 New Mention" if not is_dm else "📥 New Offline DM",
                "description": f"[**Jump to Message**]({jump_url})",
                "color": 0x00BFFF,
                "fields": [
                    {"name": "Sender Tag", "value": f"`{author}`", "inline": True},
                    {"name": "User ID", "value": f"`{author.id}`", "inline": True},
                    {"name": "Message", "value": content[:1900] or "*No text*", "inline": False},
                ],
                "footer": {
                    "text": f"Received • {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                }
            }
            await session.post(config["webhook_url"], json={"embeds": [embed]})

    def add_to_log(author_name, author_id, content, replied, channel_id=None, message_id=None):
        key = (channel_id, author_id)
        if key in seen_initial_dms:
            return
        seen_initial_dms.add(key)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        new_id = f"{author_id}_{timestamp}_{len(message_log)}"
        if len(message_log) >= MAX_LOG_SIZE:
            message_log.pop()
        message_log.insert(0, {
            "id": new_id,
            "time": timestamp,
            "author": author_name,
            "author_id": author_id,
            "content": content[:50] + "..." if len(content) > 50 else content,
            "replied": replied,
            "channel_id": channel_id,
            "message_id": message_id
        })
        update_table()
        update_status_ui()
        save_data()

    def update_table():
        if "activity_table" not in ui_refs:
            return
        rows = []
        for msg in message_log:
            rows.append({
                "id": msg["id"],
                "cells": [
                    {"text": msg["time"]},
                    {"text": msg["author"], "subtext": f"ID: {msg['author_id']}"},
                    {"text": msg["content"]},
                    {
                        "text": "✓ Replied" if msg["replied"] else "• Logged",
                        "color": "green" if msg["replied"] else "blue",
                        "style": {"padding": "1px 5px", "borderRadius": "4px", "fontSize": "0.75em", "height": "1.2em", "lineHeight": "1.2em"}
                    },
                    {}  # Action buttons cell
                ]
            })
        ui_refs["activity_table"].rows = rows
        ui_refs["delete_selected_button"].disabled = True
        ui_refs["select_all_toggle"].checked = False

    def get_current_status():
        try:
            for guild in bot.guilds:
                member = guild.get_member(bot.user.id)
                if member and hasattr(member, 'status'):
                    return str(member.status).lower()
            if hasattr(bot, 'settings') and hasattr(bot.settings, 'status'):
                return str(bot.settings.status).lower()
        except Exception:
            pass
        return "unknown"

    def update_status_ui():
        current_status = get_current_status()
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        status_display = current_status.upper()
        if current_status == "dnd": status_display = "DO NOT DISTURB"
        elif current_status == "online": status_display = "ONLINE"
        elif current_status == "invisible": status_display = "INVISIBLE"
        elif current_status == "idle": status_display = "IDLE"
        if "status_text" in ui_refs:
            ui_refs["status_text"].content = status_display
        is_active = current_status in config["active_statuses"] and config["active"]
        if "active_text" in ui_refs:
            ui_refs["active_text"].content = "ACTIVE" if is_active else "INACTIVE"
            ui_refs["active_text"].color = "#10b981" if is_active else "#ef4444"
        if "replied_count" in ui_refs:
            ui_refs["replied_count"].content = str(len(replied_users))
        if "last_update" in ui_refs:
            ui_refs["last_update"].content = f"Updated: {current_time}"

    def update_server_dropdown():
        if "server_select" not in ui_refs:
            return
        server_items = [{"id": "none", "title": "Loading servers..."}]
        for guild in bot.guilds:
            icon_url = str(guild.icon.url) if guild.icon else None
            server_items.append({
                "id": str(guild.id),
                "title": guild.name,
                "iconUrl": icon_url
            })
        if len(server_items) > 1:
            server_items.pop(0)
        ui_refs["server_select"].items = server_items
        ui_refs["server_select"].selected_items = config["allowed_servers"]

    @bot.listen('on_message')
    async def handleMessage(message):
        if not config["active"]:
            return
        if message.author == bot.user or not message.content:
            return
        is_dm = isinstance(message.channel, discord.DMChannel)
        if config["dm_only"] and not is_dm:
            return
        if not is_dm:
            if config["allowed_servers"]:
                guild_id = str(message.guild.id)
                if guild_id not in config["allowed_servers"]:
                    return
            if not bot.user.mentioned_in(message) or message.mention_everyone:
                return
        current_status = get_current_status()
        if current_status not in config["active_statuses"]:
            return
        if config["webhook_enabled"]:
            await log_to_webhook(message.author, message.content, message.channel.id, message.id, is_dm)
        user_channel_key = (message.channel.id, message.author.id)
        current_time = datetime.datetime.now()
        if user_channel_key in replied_users:
            last_reply_time = replied_users[user_channel_key]
            time_since_last = (current_time - last_reply_time).total_seconds() / 60
            if time_since_last < config["cooldown_minutes"]:
                add_to_log(message.author.name, message.author.id, message.content, False, message.channel.id, message.id)
                return
        if config["reply_delay"] > 0:
            await asyncio.sleep(config["reply_delay"])
        formatted_reply = config["custom_reply"].format(mention=message.author.mention)
        sent_msg = await message.channel.send(formatted_reply)
        replied_users[user_channel_key] = current_time
        if config["delete_after_minutes"] > 0:
            asyncio.create_task(schedule_message_deletion(sent_msg, config["delete_after_minutes"]))
        add_to_log(message.author.name, message.author.id, message.content, True, message.channel.id, message.id)
        save_data()

    async def status_update_loop():
        nonlocal status_updater_running
        if status_updater_running:
            return
        status_updater_running = True
        while True:
            update_status_ui()
            await asyncio.sleep(2)

    @bot.listen('on_ready')
    async def start_status_updater():
        load_data()
        refresh_presets_dropdown()
        update_table()
        asyncio.create_task(status_update_loop())
        update_server_dropdown()

    tab = Tab(name="SmartReplier", icon="message", gap=8)
    main_container = tab.create_container(type="columns", gap=6)

    # LEFT COLUMN - Activity Log
    activity_card = main_container.create_card(type="rows", width="full", height="full")
    activity_card.create_ui_element(UI.Text, content="Recent Activity", size="2xl", weight="bold", margin="mb-2")
    activity_card.create_ui_element(UI.Text, content="Messages received while AFK", size="sm", color="#9ca3af", margin="mb-3")

    btn_group = activity_card.create_group(type="columns", gap=4, full_width=True, margin="mb-3")
    ui_refs["select_all_toggle"] = btn_group.create_ui_element(UI.Toggle, label="Select All", checked=False)
    ui_refs["delete_selected_button"] = btn_group.create_ui_element(UI.Button, label="Delete Selected", color="danger", disabled=True, full_width=False)

    def table_selection_change(selected_ids):
        ui_refs["delete_selected_button"].disabled = (len(selected_ids) == 0)
        table = ui_refs["activity_table"]
        all_ids = [row["id"] for row in table.rows]
        ui_refs["select_all_toggle"].checked = (set(selected_ids) == set(all_ids) and len(all_ids) > 0)

    def on_select_all(checked):
        table = ui_refs["activity_table"]
        all_row_ids = [row['id'] for row in table.rows]
        if checked:
            table.selected_row_ids = all_row_ids
        else:
            table.selected_row_ids = []
        table_selection_change(table.selected_row_ids)

    def on_delete_selected():
        selected_ids = ui_refs["activity_table"].selected_row_ids
        for sid in selected_ids:
            msg = find_log_by_id(sid)
            if msg:
                seen_initial_dms.discard((msg["channel_id"], msg["author_id"]))
        message_log[:] = [msg for msg in message_log if msg["id"] not in selected_ids]
        update_table()
        table_selection_change([])
        save_data()
        tab.toast(title="Deleted", description=f"Deleted {len(selected_ids)} log entries", type="SUCCESS")

    ui_refs["select_all_toggle"].onChange = on_select_all
    ui_refs["delete_selected_button"].onClick = on_delete_selected

    ui_refs["activity_table"] = activity_card.create_ui_element(UI.Table,
        columns=[
            {"type": "text", "label": "Time"},
            {"type": "text", "label": "From"},
            {"type": "text", "label": "Message"},
            {
                "type": "tag",
                "label": "Status",
            },
            {"type": "button", "label": "Actions", "buttons": [
                {"label": "Jump", "color": "default", "onClick": jump_to_dm, "margin": "ml-4"}
            ]}
        ],
        rows=[],
        search=True,
        items_per_page=30,
        selectable=True,
        full_width=True,
        height="full"
    )
    ui_refs["activity_table"].onSelectionChange = table_selection_change

    ui_refs["jump_url_input"] = activity_card.create_ui_element(UI.Input,
        label="📍 Jump URL (Click, Select All, Copy)",
        value="",
        full_width=True,
        readonly=True,
        visible=False,
        margin="mt-3"
    )

    # RIGHT COLUMN - Status & Settings
    right_card = main_container.create_card(type="rows", width="full", height="full")
    right_card_group = right_card.create_group(type="rows", gap=4, full_width=True)

    # Status Monitor
    status_card = right_card_group.create_group(type="rows", gap=3, full_width=True)
    status_card.create_ui_element(UI.Text, content="Status Monitor", size="xl", weight="bold", margin="mb-2")
    initial_status = get_current_status()
    status_display = initial_status.upper()
    if initial_status == "dnd": status_display = "DO NOT DISTURB"
    elif initial_status == "invisible": status_display = "INVISIBLE"
    status_grid = status_card.create_group(type="rows", gap=2, full_width=True)
    s1 = status_grid.create_group(type="rows", gap=1, full_width=True)
    s1.create_ui_element(UI.Text, content="Current Status", size="sm", color="#9ca3af")
    ui_refs["status_text"] = s1.create_ui_element(UI.Text, content=status_display, size="lg", weight="bold")
    s2 = status_grid.create_group(type="rows", gap=1, full_width=True)
    s2.create_ui_element(UI.Text, content="AFK Script State", size="sm", color="#9ca3af")
    ui_refs["active_text"] = s2.create_ui_element(UI.Text,
        content="ACTIVE" if initial_status in config["active_statuses"] and config["active"] else "INACTIVE",
        size="lg", weight="bold", color="#10b981" if initial_status in config["active_statuses"] and config["active"] else "#ef4444")
    s3 = status_grid.create_group(type="rows", gap=1, full_width=True)
    s3.create_ui_element(UI.Text, content="Users Replied To", size="sm", color="#9ca3af")
    ui_refs["replied_count"] = s3.create_ui_element(UI.Text, content=str(len(replied_users)), size="lg", weight="bold")
    ui_refs["last_update"] = status_card.create_ui_element(UI.Text, content=f"Updated: {datetime.datetime.now().strftime('%I:%M:%S %p')}", size="tiny", color="#6b7280", align="center", margin="mb-2")

    def manual_update():
        load_data()  # Always reload from file on manual refresh
        refresh_presets_dropdown()
        update_table()
        update_status_ui()
        update_server_dropdown()
        tab.toast(title="Refreshed", description="Status and logs updated", type="SUCCESS")

    status_card.create_ui_element(UI.Button, label="Refresh Status", variant="bordered", color="default", full_width=True, onClick=manual_update)

    # Settings Section
    settings_block = right_card_group.create_group(type="rows", gap=3, margin="mt-3", full_width=True)
    settings_block.create_ui_element(UI.Text, content="Settings", size="xl", weight="bold", margin="mb-2")

    script_toggle = settings_block.create_ui_element(UI.Toggle, label="Script Enabled", checked=config["active"])
    def toggle_script(checked):
        config["active"] = checked
        update_status_ui()
        save_data()
        tab.toast(title="Script Status", description=f"Script {'enabled' if checked else 'disabled'}", type="SUCCESS" if checked else "INFO")
    script_toggle.onChange = toggle_script

    dm_only_toggle = settings_block.create_ui_element(UI.Toggle, label="DMs Only (disable for DMs + Servers)", checked=config["dm_only"])
    def toggle_dm_only(checked):
        config["dm_only"] = checked
        save_data()
        location = "DMs only" if checked else "DMs and Servers"
        tab.toast(title="Location Updated", description=f"Will reply in: {location}", type="INFO")
    dm_only_toggle.onChange = toggle_dm_only

    ui_refs["server_select"] = settings_block.create_ui_element(
        UI.Select,
        label="Allowed Servers (empty = all servers)",
        items=[{"id": "loading", "title": "Click Refresh to load servers"}],
        selected_items=[],
        mode="multiple",
        full_width=True,
        description="Select servers for mention replies. Refresh to load servers."
    )
    def update_allowed_servers(selected):
        config["allowed_servers"] = selected
        save_data()
        count = len(selected) if selected else "all"
        tab.toast(title="Servers Updated", description=f"Will reply in {count} servers", type="INFO")
    ui_refs["server_select"].onChange = update_allowed_servers

    webhook_toggle = settings_block.create_ui_element(UI.Toggle, label="Webhook Logging", checked=config["webhook_enabled"])
    def toggle_webhook(checked):
        config["webhook_enabled"] = checked
        save_data()
    webhook_toggle.onChange = toggle_webhook

    reply_input = settings_block.create_ui_element(UI.Input, label="Auto-Reply Message", placeholder="Your custom reply...", value=config["custom_reply"], full_width=True)
    def update_reply(value):
        config["custom_reply"] = value
        save_data()
    reply_input.onInput = update_reply

    status_options = [
        {"id": "online", "title": "Online"},
        {"id": "idle", "title": "Idle"},
        {"id": "dnd", "title": "Do Not Disturb"},
        {"id": "invisible", "title": "Invisible"}
    ]
    status_select = settings_block.create_ui_element(
        UI.Select,
        label="Active Modes (AFK triggers)",
        items=status_options,
        selected_items=config["active_statuses"],
        mode="multiple",
        full_width=True
    )
    def update_active_statuses(selected):
        config["active_statuses"] = selected
        update_status_ui()
        save_data()
    status_select.onChange = update_active_statuses

    delay_select = settings_block.create_ui_element(UI.Select, label="Reply Delay", items=[
        {"id": "0", "title": "No delay"},
        {"id": "2", "title": "2 seconds"},
        {"id": "5", "title": "5 seconds"},
        {"id": "10", "title": "10 seconds"}
    ], selected_items=[str(config["reply_delay"])], mode="single", full_width=True)
    def update_delay(selected):
        config["reply_delay"] = int(selected[0]) if selected else 0
        save_data()
    delay_select.onChange = update_delay

    cooldown_select = settings_block.create_ui_element(UI.Select, label="Cooldown Between Replies (Same Channel)", items=[
        {"id": "1", "title": "1 minute"},
        {"id": "5", "title": "5 minutes"},
        {"id": "10", "title": "10 minutes"},
        {"id": "15", "title": "15 minutes"},
        {"id": "30", "title": "30 minutes"},
        {"id": "60", "title": "1 hour"}
    ], selected_items=[str(config["cooldown_minutes"])], mode="single", full_width=True)
    def update_cooldown(selected):
        config["cooldown_minutes"] = int(selected[0]) if selected else 5
        save_data()
        tab.toast(title="Cooldown Updated", description=f"Will wait {config['cooldown_minutes']} min before next reply", type="INFO")
    cooldown_select.onChange = update_cooldown

    delete_select = settings_block.create_ui_element(UI.Select, label="Delete Reply After", items=[
        {"id": "0", "title": "Never"},
        {"id": "5", "title": "5 minutes"},
        {"id": "15", "title": "15 minutes"},
        {"id": "25", "title": "25 minutes"},
        {"id": "60", "title": "1 hour"}
    ], selected_items=[str(config["delete_after_minutes"])], mode="single", full_width=True)
    def update_delete(selected):
        config["delete_after_minutes"] = int(selected[0]) if selected else 0
        save_data()
    delete_select.onChange = update_delete

    webhook_input = settings_block.create_ui_element(UI.Input, label="Webhook URL", placeholder="https://discord.com/api/webhooks/...", value=config["webhook_url"], full_width=True)
    def update_webhook_url(value):
        config["webhook_url"] = value
        save_data()
    webhook_input.onInput = update_webhook_url

    # Preset Management Section - Dropdown
    settings_block.create_ui_element(UI.Text, content="Preset Management", size="lg", weight="bold", margin="mt-4")
    preset_load_group = settings_block.create_group(type="rows", gap=2, full_width=True, margin="mb-2")

    def load_preset_dropdown(selected):
        if not selected: return
        preset = preset_configs.get(selected[0], None)
        if preset:
            config.update(preset)
            reply_input.value = config["custom_reply"]
            delay_select.selected_items = [str(config["reply_delay"])]
            delete_select.selected_items = [str(config["delete_after_minutes"])]
            webhook_toggle.checked = config["webhook_enabled"]
            script_toggle.checked = config["active"]
            dm_only_toggle.checked = config["dm_only"]
            cooldown_select.selected_items = [str(config["cooldown_minutes"])]
            status_select.selected_items = config["active_statuses"]
            ui_refs["server_select"].selected_items = config["allowed_servers"]
            webhook_input.value = config["webhook_url"]
            save_data()
            tab.toast(title="✅ Loaded", description=f"Loaded preset: {selected[0]}", type="SUCCESS")

    ui_refs["preset_select"] = preset_load_group.create_ui_element(
        UI.Select,
        label="Load Preset",
        items=[{"id": k, "title": k} for k in sorted(preset_configs.keys())],
        selected_items=[],
        mode="single",
        full_width=True
    )
    ui_refs["preset_select"].onChange = load_preset_dropdown

    preset_save_group = settings_block.create_group(type="rows", gap=2, full_width=True, margin="mt-3")
    preset_save_group.create_ui_element(UI.Text, content="Save New Preset", size="sm", weight="bold")
    preset_name_input = preset_save_group.create_ui_element(UI.Input, label="Preset Name", placeholder="Enter new preset name", full_width=True)

    def save_new_preset():
        name = preset_name_input.value.strip()
        if not name:
            tab.toast(title="❌ Error", description="Preset name cannot be empty", type="ERROR")
            return
        if name in preset_configs:
            tab.toast(title="❌ Error", description="Preset already exists. Choose a different name.", type="ERROR")
            return
        preset_configs[name] = config.copy()
        save_data()
        preset_name_input.value = ""
        tab.toast(title="✅ Saved", description=f"Preset '{name}' saved!", type="SUCCESS")
        refresh_presets_dropdown()

    preset_save_group.create_ui_element(
        UI.Button,
        label="💾 Save Current Config as Preset",
        variant="solid",
        color="success",
        full_width=True,
        onClick=save_new_preset
    )

    preset_delete_group = settings_block.create_group(type="rows", gap=2, full_width=True, margin="mt-3")
    preset_delete_group.create_ui_element(UI.Text, content="Delete Preset", size="sm", weight="bold")
    delete_preset_input = preset_delete_group.create_ui_element(UI.Input, label="Preset Name to Delete", placeholder="Enter exact preset name", full_width=True)

    def delete_preset():
        name = delete_preset_input.value.strip()
        if not name:
            tab.toast(title="❌ Error", description="Please enter a preset name", type="ERROR")
            return
        if name not in preset_configs:
            tab.toast(title="❌ Error", description=f"Preset '{name}' not found", type="ERROR")
            return
        del preset_configs[name]
        save_data()
        delete_preset_input.value = ""
        tab.toast(title="✅ Deleted", description=f"Preset '{name}' deleted!", type="SUCCESS")
        refresh_presets_dropdown()

    preset_delete_group.create_ui_element(
        UI.Button,
        label="🗑️ Delete Preset",
        variant="solid",
        color="danger",
        full_width=True,
        onClick=delete_preset
    )

    preset_rename_group = settings_block.create_group(type="rows", gap=2, full_width=True, margin="mt-3")
    preset_rename_group.create_ui_element(UI.Text, content="Rename Preset", size="sm", weight="bold")
    rename_old_input = preset_rename_group.create_ui_element(UI.Input, label="Current Preset Name", placeholder="Enter current name", full_width=True)
    rename_new_input = preset_rename_group.create_ui_element(UI.Input, label="New Preset Name", placeholder="Enter new name", full_width=True)

    def rename_preset():
        old_name = rename_old_input.value.strip()
        new_name = rename_new_input.value.strip()
        if not old_name or not new_name:
            tab.toast(title="❌ Error", description="Both names are required", type="ERROR")
            return
        if old_name not in preset_configs:
            tab.toast(title="❌ Error", description=f"Preset '{old_name}' not found", type="ERROR")
            return
        if new_name in preset_configs:
            tab.toast(title="❌ Error", description=f"Preset '{new_name}' already exists", type="ERROR")
            return
        preset_configs[new_name] = preset_configs.pop(old_name)
        save_data()
        rename_old_input.value = ""
        rename_new_input.value = ""
        tab.toast(title="✅ Renamed", description=f"Renamed '{old_name}' to '{new_name}'!", type="SUCCESS")
        refresh_presets_dropdown()

    preset_rename_group.create_ui_element(
        UI.Button,
        label="✏️ Rename Preset",
        variant="solid",
        color="primary",
        full_width=True,
        onClick=rename_preset
    )

    settings_block.create_ui_element(
        UI.Text,
        content="💡 After saving/deleting/renaming presets, reload the script to see updated buttons",
        size="tiny",
        color="#6b7280",
        margin="mt-2"
    )

    load_data()
    refresh_presets_dropdown()
    tab.render()

smartOfflineReplier()