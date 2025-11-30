# Please use a paid invite checker, as well as using proxies
# This script will only help you get invites but you will have to pay for a checker outside of nighty
# If you don't know what the invitations are for, I'll explain it to you.:
# Invites are mostly used for Nitro Snipe, that's why you need a checker since when you have about 10k invites (This is an example), you will need to have a configuration, for example: minimum of 1000 members, minimum of 16 boots and minimum of 200 members online.
# With a setup like this, it's more likely that someone will send a Nitro gift and you can get it for your account.
# They can also be sold, their market price is 1k invites for 1 dollar
# If you find any bug or would like to implement something, send me a message.

@nightyScript(
    name="Invite Scraper",
    author="Luxed",
    description="Scans and collects Discord invites from all servers and channels.",
    usage="Use the button to enable or disable invite scanning."
)
def invite_scraper():

    invites_dir = os.path.join(getScriptsPath(), "invites")
    invites_file = os.path.join(invites_dir, "invites.txt")
    config_file = os.path.join(invites_dir, "config.json")
    os.makedirs(invites_dir, exist_ok=True)
    bot.invite_scanning_active = False
    bot.invite_count = 0
    bot.unique_invites = set()
    bot.save_full_url = True
    
    def load_config():
        try:
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    bot.invite_scanning_active = config.get("scanning_active", False)
                    bot.save_full_url = config.get("save_full_url", True)
                    return config
            return {"scanning_active": False, "save_full_url": True}
        except Exception as e:
            tab.toast(type="ERROR", title="Configuration Error", description=f"Error loading configuration: {str(e)}")
            return {"scanning_active": False, "save_full_url": True}
    
    def save_config():
        try:
            config = {
                "scanning_active": bot.invite_scanning_active,
                "save_full_url": bot.save_full_url
            }
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            tab.toast(type="ERROR", title="Configuration Error", description=f"Error saving configuration: {str(e)}")
            return False
    
    def load_invites():
        try:
            if os.path.exists(invites_file):
                with open(invites_file, "r", encoding="utf-8") as f:
                    invites = []
                    for line in f.readlines():
                        line = line.strip()
                        if line and not line.startswith("#"):
                            invite_code = extract_invites(line)
                            if invite_code:
                                invites.extend(invite_code)
                            else:
                                invites.append(line)
                    bot.unique_invites = set(invites)
                    bot.invite_count = len(bot.unique_invites)
                    return {"invites": list(bot.unique_invites), "last_updated": None}
            return {"invites": [], "last_updated": None}
        except Exception as e:
            tab.toast(type="ERROR", title="Invites Error", description=f"Error loading invites: {str(e)}")
            return {"invites": [], "last_updated": None}
    
    def save_invites():
        try:
            date_time = f"# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            with open(invites_file, "w", encoding="utf-8") as f:
                f.write(date_time)
                for invite in bot.unique_invites:
                    if bot.save_full_url:
                        f.write(f"https://discord.gg/{invite}\n")
                    else:
                        f.write(f"{invite}\n")
            return True
        except Exception as e:
            tab.toast(type="ERROR", title="Invites Error", description=f"Error saving invites: {str(e)}")
            return False
    
    def extract_invites(content):
        invite_pattern = re.compile(r'(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discordapp\.com/invite)/([a-zA-Z0-9-]+)')
        matches = invite_pattern.findall(content)
        return matches
    
    def toggle_scanning(checked):
        bot.invite_scanning_active = checked
        if checked:
            data = load_invites()
            bot.unique_invites = set(data.get("invites", []))
            bot.invite_count = len(bot.unique_invites)
            status_text.content = f"Status: Enabled ✅ | Invites: {bot.invite_count}"
            tab.toast(type="SUCCESS", title="Invite Scanning", description="Invite scanning has been enabled")
        else:
            if save_invites():
                status_text.content = f"Status: Disabled ❌ | Invites: {bot.invite_count}"
                tab.toast(type="SUCCESS", title="Invite Scanning", description="Invite scanning has been disabled")
            else:
                tab.toast(type="ERROR", title="Error", description="Could not save invites")
        save_config()
    
    def toggle_url_format(checked):
        bot.save_full_url = checked
        save_config()
        if checked:
            format_text.content = "Format: Full URLs (https://discord.gg/code)"
            tab.toast(type="INFO", title="Format Changed", description="Full URLs will be saved")
        else:
            format_text.content = "Format: Invite codes only"
            tab.toast(type="INFO", title="Format Changed", description="Only invite codes will be saved")
        save_invites()

    def open_invites_folder():
        try:
            os.startfile(invites_dir)
            tab.toast(type="SUCCESS", title="Folder Opened", description="Invites folder has been opened")
        except Exception as e:
            tab.toast(type="ERROR", title="Folder Error", description=f"Error opening folder: {str(e)}")
    
    @bot.listen("on_message")
    async def scan_invites(message):
        if not bot.invite_scanning_active:
            return
        try:
            if message.content:
                invites = extract_invites(message.content)
                if invites:
                    old_count = len(bot.unique_invites)
                    bot.unique_invites.update(invites)
                    new_count = len(bot.unique_invites)
                    
                    if new_count > old_count:
                        bot.invite_count = new_count
                        status_text.content = f"Status: Enabled ✅ | Invites: {bot.invite_count}"
                        save_invites()
                        new_invites = new_count - old_count
        except Exception as e:
            tab.toast(type="ERROR", title="Scanning Error", description=f"Error scanning invites: {str(e)}")
    
    tab = Tab(name="Invite Scraper", title="Invite Scraper", icon="share")
    container = tab.create_container("rows")
    
    card = container.create_card(height="auto", width="full", gap=8)
    
    card.create_ui_element(UI.Text, 
                        content="Invite Scraper",
                        size="xl",
                        weight="bold")

    toggle = card.create_ui_element(UI.Toggle,
                                label="Enable invite scanning",
                                checked=bot.invite_scanning_active,
                                onChange=toggle_scanning)

    status_text = card.create_ui_element(UI.Text,
                                     content=f"Status: {'Enabled ✅' if bot.invite_scanning_active else 'Disabled ❌'} | Invites: {bot.invite_count}",
                                     color="var(--text-muted)")
    
    format_toggle = card.create_ui_element(UI.Toggle,
                                      label="Save full URLs",
                                      checked=bot.save_full_url,
                                      onChange=toggle_url_format)
    
    format_text = card.create_ui_element(UI.Text,
                                     content=f"Format: {'Full URLs (https://discord.gg/code)' if bot.save_full_url else 'Invite codes only'}",
                                     color="var(--text-muted)",
                                     size="sm")
    
    folder_button = card.create_ui_element(UI.Button,
                                       label="Open Invites Folder",
                                       onClick=open_invites_folder,
                                       full_width=True)

    card.create_ui_element(UI.Text,
                        content="This script automatically scans all new messages for Discord invites and saves them to a text file in real-time.",
                        size="sm",
                        color="var(--text-muted)")

    config = load_config()
    bot.invite_scanning_active = config.get("scanning_active", False)
    bot.save_full_url = config.get("save_full_url", True)
    
    toggle.checked = bot.invite_scanning_active
    format_toggle.checked = bot.save_full_url
    
    data = load_invites()
    bot.unique_invites = set(data.get("invites", []))
    bot.invite_count = len(bot.unique_invites)
    status_text.content = f"Status: {'Enabled ✅' if bot.invite_scanning_active else 'Disabled ❌'} | Invites: {bot.invite_count}"
    format_text.content = f"Format: {'Full URLs (https://discord.gg/code)' if bot.save_full_url else 'Invite codes only'}"

    tab.render()

invite_scraper()