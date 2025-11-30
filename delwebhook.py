@nightyScript(
    name="Webhook deleter",
    author="nimiec02",
    description="Delete a webhook with the link.", 
    usage="UI"
)
def Delwh():
    import requests
    import asyncio

    @bot.command(usage="<webhook_url>", description="Delete a Discord Webhook")
    async def delwebhook(ctx, webhook_url: str = None):
        if not webhook_url:
            await ctx.message.delete()
            showToast(
                text=f"Please provide a webhook URL.", 
                type_="ERROR", 
                title="NO URL FOUND"
            )
            return

        try:
            response = requests.delete(webhook_url)
            response.raise_for_status()
            showToast(
                text=f"Webhook successfully deleted.", 
                type_="SUCCESS", 
                title="Webhook deleted"
            )
        except requests.exceptions.RequestException:
            showToast(
                text=f"Error deleting the webhook.", 
                type_="ERROR", 
                title="ERROR"
            )
        finally:
            await ctx.message.delete()


    async def startWebhookDelete():
        webhook_url = str(webhook_url_input.value).strip()

        if not webhook_url:
            delwh_tab.toast(title="NO URL FOUND", description="Please provide a webhook URL.", type="ERROR")
            return

        delwh_tab.toast(title="Starting", description="Attempting to delete webhook...", type="SUCCESS")

        try:
            response = requests.delete(webhook_url)
            response.raise_for_status()
            delwh_tab.toast(title="Webhook deleted", description="Webhook successfully deleted.", type="SUCCESS")
        except requests.exceptions.RequestException:
            delwh_tab.toast(title="ERROR", description="Error deleting the webhook.", type="ERROR")

    delwh_tab = Tab(name='Webhook Deleter', title="Webhook Deleter", icon="trash")
    delwh_container = delwh_tab.create_container(type="rows")
    delwh_card = delwh_container.create_card(height="full", width="full", gap=2)

    delwh_card.create_ui_element(UI.Text, content="Delete a Discord Webhook", size="xl", weight="bold")
    webhook_url_input = delwh_card.create_ui_element(UI.Input, label="Webhook URL", full_width=True, show_clear_button=True, required=True, margin="mb-3")
    delete_button = delwh_card.create_ui_element(UI.Button, label='Delete Webhook', disabled=False, full_width=True, onClick=startWebhookDelete)

    delwh_tab.render()

Delwh()
