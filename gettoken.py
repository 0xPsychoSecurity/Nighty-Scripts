# Token Retreiver - Universal way to grab your own token

# --- Note ---
# - Using the command in public channels may expose your token to others.
# - Always keep your token private to avoid account compromise.

@nightyScript(
    name="Token Retriever",
    author="Sakyiee",
    description="Retrieve your Discord token without checking network tab",
    usage="<p>token"
)
def script_function():
    """
    TOKEN RETRIEVER
    ---------------
    
    Quickly retrieve your Discord user token without needing to check network tab
    
    COMMANDS:
    <p>token - Display your Discord token
    <p>token copy - Copy your token to clipboard (if supported)
    
    EXAMPLES:
    <p>token - Shows your token in chat (deleted after 10 seconds)
    <p>token copy - Attempts to copy token to clipboard
    
    """
    
    import asyncio
    
    @bot.command(
        name="token",
        aliases=["gettoken", "mytoken"],
        usage="[copy]",
        description="Retrieve your Discord token"
    )
    async def token_command(ctx, *, args: str = ""):
        await ctx.message.delete()
        token = bot.http.token
        
        if not token:
            await ctx.send("Unable to retrieve token. Bot may not be properly authenticated.")
            return
        
        args = args.strip().lower()
        
        if args == "copy":
            try:
                import pyperclip
                pyperclip.copy(token)
                msg = await ctx.send("Token copied to clipboard!\n\n**Security reminder:** Your token provides full access to your account. Never share it.")
                await asyncio.sleep(5)
                await msg.delete()
            except Exception as e:
                msg = await ctx.send(f"Failed to copy to clipboard: {e}\n\nYour token:\n```\n" + token + "\n```")
                await asyncio.sleep(10)
                await msg.delete()
        else:
            msg = await ctx.send(
                f"🔑 **Your Discord Token:**\n```\n{token}\n```\n\n"
                f"**Security Warning:**\n"
                f"• Never share this token with anyone\n"
                f"• Anyone with this token has full access to your account\n"
                f"• This message will be deleted in 10 seconds\n\n"
            )
            await asyncio.sleep(10)
            try:
                await msg.delete()
            except Exception:
                pass

script_function()

def create_ui():
    try:
        tab = Tab(name="Token Retriever", title="Token Retriever", icon="key")
        main = tab.create_container(type="columns")
        card = main.create_card(gap=4)
        card.create_ui_element(UI.Text, content="Token Retriever", size="lg", weight="bold")
        card.create_ui_element(
            UI.Text,
            content="Reveal or copy your Discord token. The token is stored locally and only visible to you.",
            size="base",
            color="secondary",
        )
        group = card.create_group(type="columns", gap=4)
        token_input = group.create_ui_element(UI.Input, label="Your Token (hidden)", placeholder="Click Show to reveal", full_width=True)
        token_input.value = "" 
        token_input.read_only = True

        button_group = card.create_group(type="columns", gap=4, horizontal_align="center")
        show_button = button_group.create_ui_element(UI.Button, label="Show Token", variant="solid", color="primary")
        copy_button = button_group.create_ui_element(UI.Button, label="Copy Token", variant="solid", color="success")
        revealed = {"state": False}

        def on_show_click():
            revealed["state"] = not revealed["state"]
            if revealed["state"]:
                token_input.value = bot.http.token or "(not available)"
                show_button.label = "Hide Token"
                tab.toast("Token Revealed", "Your token is now visible in the input field. Keep it private.", "INFO")
            else:
                token_input.value = ""
                show_button.label = "Show Token"
                tab.toast("Token Hidden", "Your token is now hidden.", "INFO")
        def on_copy_click():
            token = bot.http.token
            if not token:
                tab.toast("Copy Failed", "Unable to retrieve token.", "ERROR")
                return
            try:
                import pyperclip
                pyperclip.copy(token)
                tab.toast("Copied", "Token copied to clipboard.", "SUCCESS")
            except Exception as e:
                tab.toast("Copy failed", f"{e}", "ERROR")
        show_button.onClick = on_show_click
        copy_button.onClick = on_copy_click
        try:
            tab.render()
        except Exception:
            pass
    except Exception as e:
        print(f"UI creation failed: {e}", type_="ERROR")

create_ui()
