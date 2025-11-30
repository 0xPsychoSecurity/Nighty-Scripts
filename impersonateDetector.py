# Made in reference to the suggestion: https://discord.com/channels/1053816317129527336/1258907502838415370/1334056661316276245
@nightyScript(
    name="Impersonate detector", 
    author="nes",
    description="Detect impersonators & get notified about it.", 
    usage="Works as soon as the script is enabled."
)
def impersonateDetector():
    os.makedirs(f'{getScriptsPath()}/scriptData', exist_ok=True)
    script_config_path = f"{getScriptsPath()}/scriptData/impersonateDetector.json"
    
    def updateSetting(key, value):
        json.dump({**(json.load(open(script_config_path, 'r', encoding="utf-8", errors="ignore")) if os.path.exists(script_config_path) else {}), key: value}, open(script_config_path, 'w', encoding="utf-8", errors="ignore"), indent=2)

    def getSetting(key=None):
        return (lambda p: (settings := json.load(open(p, 'r', encoding="utf-8", errors="ignore"))) and settings.get(key) if key else settings)(script_config_path) if os.path.exists(script_config_path) else (None if key else {})

    def updateInputState(input, invalid=False, error_message=None):
        input.invalid = invalid
        input.error_message = error_message

    def setIDWebhookUrl(value):
        if "https://discord.com/api/webhooks/" in value:
            updateInputState(id_input, False, None)
            updateSetting("webhook_url", value)
        else:
            updateInputState(id_input, True, "Invalid webhook url.")

    id_tab = Tab(name='Impersonate Detect', title="Impersonate detector", icon="bell")
    id_container = id_tab.create_container(type="rows")
    id_card = id_container.create_card(height="full", width="full", gap=3)
    id_input = id_card.create_ui_element(UI.Input, label="Webhook URL", full_width=True, show_clear_button=True, required=True, onInput=setIDWebhookUrl, placeholder=getSetting("webhook_url"))
    

    @bot.listen("on_message")
    async def onImpersonation(message):
        if message.author.display_name == bot.user.display_name and message.author.bot:
            sendAppNotification(f"Impersonation found | {message.clean_content}", message.jump_url, message.channel, message=message)
            await sendWebhookNotification(getSetting("webhook_url"), "Impersonation found", f"Content: {message.content}\nJump: {message.jump_url}")

    id_tab.render()
impersonateDetector()
