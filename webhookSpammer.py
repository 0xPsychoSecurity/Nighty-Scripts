@nightyScript(
    name="Webhook spammer", 
    author="for donworry",
    description="A simple webhook spammer, can be done through a command (spamwebhook), or through the UI.", 
    usage='.spamwebhook <webhook_url> <delayInSeconds> <amount> <"your message"> [avatar_url] ["name"]'
)
def customWebhookSpammer():
    async def sendWebhookMessages(url, delay: float, amount: int, message: str, avatar_url: str=None, username: str=None):
        session = ClientSession()
        webhook = discord.Webhook.from_url(url, session=session)
        for index in range(amount):
            await webhook.send(content=message, username=username, avatar_url=avatar_url)
            await asyncio.sleep(delay)
        await session.close()
    
    async def startWebhookSpam():
        try:
            ws_tab.toast(title="Starting", description="Webhook spam has just started.", type="SUCCESS")
            session = ClientSession()
            webhook = discord.Webhook.from_url(webhook_url_input.value, session=session)
            for index in range(int(amount_input.value)):
                await webhook.send(content=messageToSend_input.value, username=w_username_input.value, avatar_url=w_avatarurl_input.value)
                await asyncio.sleep(int(delay_input.value))
            await session.close()
            ws_tab.toast(title="Webhook Spam", description="Finished spamming webhook.", type="INFO")
        except Exception as e:
            ws_tab.toast(title="Webhook Spam", description=str(e), type="ERROR")
    @bot.command(usage='<webhook_url> <delayInSeconds> <amount> <"your message"> [avatar_url] ["name"]')
    async def spamwebhook(ctx, webhook_url: str, delayInSeconds: float, amount: int, messageToSend: str, avatarUrl: str=None, name: str=None):
        await ctx.message.delete()
        await sendWebhookMessages(url=webhook_url, delay=delayInSeconds, amount=amount, message=messageToSend, avatar_url=avatarUrl, username=name)

    ws_tab = Tab(name='Webhook Spam', title="Webhook Spammer", icon="message")
    ws_container = ws_tab.create_container(type="rows")
    ws_card = ws_container.create_card(height="full", width="full", gap=2)

    # required options
    ws_card.create_ui_element(UI.Text, content="Required options", size="xl", weight="bold")
    webhook_url_input = ws_card.create_ui_element(UI.Input, label="Webhook URL", full_width=True, show_clear_button=True, required=True)
    messageToSend_input = ws_card.create_ui_element(UI.Input, label="Message", full_width=True, show_clear_button=True, required=True)
    amount_n_delay = ws_card.create_group(type="columns", gap=3, full_width=True)
    delay_input = amount_n_delay.create_ui_element(UI.Input, label="Delay (in seconds)", full_width=True, show_clear_button=True, required=True)
    amount_input = amount_n_delay.create_ui_element(UI.Input, label="Amount (of messages)", full_width=True, show_clear_button=True, required=True)
    
    # optional options
    ws_card.create_ui_element(UI.Text, content="Optional options", size="xl", weight="bold", margin="mt-5")
    w_username_input = ws_card.create_ui_element(UI.Input, label="Username", full_width=True, show_clear_button=True, required=False)
    w_avatarurl_input = ws_card.create_ui_element(UI.Input, label="Avatar URL", full_width=True, show_clear_button=True, required=False, margin="mb-3")

    start_button = ws_card.create_ui_element(UI.Button, label='Start', disabled=False, full_width=True, onClick=startWebhookSpam)
    ws_tab.render()
customWebhookSpammer()
