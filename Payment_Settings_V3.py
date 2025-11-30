@nightyScript(
    name="Payment Settings V3",
    author="Twister x Rico",
    description="UI Script",
    usage="UI Script"
)
def paymentSettings():
    import os, json, re, requests

    # Storage path and defaults
    os.makedirs(f'{getScriptsPath()}/scriptData', exist_ok=True)
    script_config_path = f"{getScriptsPath()}/scriptData/payments.json"
    default_settings = {
        "paypal": "",
        "cashapp": "",
        "litecoin": "",
        "solana": "",
        "ethereum": "",
        "venmo": ""
    }

    # Settings storage logic
    def loadSettings():
        if os.path.exists(script_config_path):
            try:
                with open(script_config_path, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                for key in default_settings:
                    if key not in data:
                        data[key] = ""
                data = {k: data.get(k, "") for k in default_settings}
                with open(script_config_path, 'w', encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                return data
            except Exception:
                with open(script_config_path, 'w', encoding="utf-8") as f:
                    json.dump(default_settings, f, indent=2)
                return default_settings
        else:
            with open(script_config_path, 'w', encoding="utf-8") as f:
                json.dump(default_settings, f, indent=2)
            return default_settings

    def updateSetting(key, value):
        settings = loadSettings()
        settings[key] = value
        with open(script_config_path, 'w', encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

    def getSetting(key=None):
        settings = loadSettings()
        return settings.get(key) if key else settings

    # Validation
    def isValidCashtag(cashtag):
        return bool(re.fullmatch(r"\$[a-zA-Z0-9]{1,15}", cashtag)) or not cashtag

    def isValidCryptoAddress(address):
        return bool(re.fullmatch(r"[LM][a-km-zA-HJ-NP-Z1-9]{25,34}", address)) or not address

    def isValidPaypal(email):
        return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email)) or not email

    def isValidVenmo(venmo):
        return bool(re.fullmatch(r"@[a-zA-Z0-9_]+", venmo)) or not venmo

    def isValidSolana(address):
        return bool(re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{32,44}", address)) or not address

    def isValidEthereum(address):
        return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", address)) or not address

    # Universal input checking
    def validateInput(new_value, current_input, validate_func, key, error_message):
        if not validate_func(new_value):
            current_input.invalid = True
            current_input.error_message = error_message
            return False
        current_input.invalid = False
        current_input.error_message = None
        updateSetting(key, new_value)
        return True

    def checkPaypalInput(new_value):
        return validateInput(new_value, paypal_input, isValidPaypal, "paypal", "Invalid PayPal format.")

    def checkCashtagInput(new_value):
        return validateInput(new_value, cashtag_input, isValidCashtag, "cashapp", "Invalid CashApp Tag. Must start with $ and be 1-15 characters.")

    def checkLtcInput(new_value):
        return validateInput(new_value, ltc_input, isValidCryptoAddress, "litecoin", "Invalid Litecoin address.")

    def checkVenmoInput(new_value):
        return validateInput(new_value, venmo_input, isValidVenmo, "venmo", "Invalid Venmo handle, must start with @.")

    def checkSolanaInput(new_value):
        return validateInput(new_value, solana_input, isValidSolana, "solana", "Invalid Solana address.")

    def checkEthereumInput(new_value):
        return validateInput(new_value, ethereum_input, isValidEthereum, "ethereum", "Invalid Ethereum address.")

    # --- UI Section ---
    payment_tab = Tab(name="Payment Settings", title="Payment Settings", icon="calc")
    p_container = payment_tab.create_container(type="columns")
    payment_card = p_container.create_card(height="full", width="full", gap=4)

    payment_card.create_ui_element(UI.Text, content="Payment Methods", size="xl", weight="bold")
    payment_card.create_ui_element(UI.Text, content=f"To send your payment methods, use the {bot.command_prefix}payments command.", size="base", weight="bold", margin="mt-2")

    payment_group = payment_card.create_group(type="columns", gap=3, full_width=True)

    paypal_input = payment_group.create_ui_element(
        UI.Input,
        label="PayPal Email (leave blank to exclude)",
        placeholder=getSetting("paypal") or "PAYPAL EMAIL HERE",
        show_clear_button=True,
        onInput=checkPaypalInput,
        full_width=True
    )
    cashtag_input = payment_group.create_ui_element(
        UI.Input,
        label="CashApp Tag (leave blank to exclude)",
        placeholder=getSetting("cashapp") or "CASHTAG HERE",
        show_clear_button=True,
        onInput=checkCashtagInput,
        full_width=True
    )
    ltc_input = payment_card.create_ui_element(
        UI.Input,
        label="Litecoin Address (leave blank to exclude)",
        placeholder=getSetting("litecoin") or "LTC ADDRESS HERE",
        show_clear_button=True,
        onInput=checkLtcInput,
        full_width=True
    )
    solana_input = payment_card.create_ui_element(
        UI.Input,
        label="Solana Address (leave blank to exclude)",
        placeholder=getSetting("solana") or "SOLANA WALLET HERE",
        show_clear_button=True,
        onInput=checkSolanaInput,
        full_width=True
    )
    ethereum_input = payment_card.create_ui_element(
        UI.Input,
        label="Ethereum Address (leave blank to exclude)",
        placeholder=getSetting("ethereum") or "ETH WALLET HERE",
        show_clear_button=True,
        onInput=checkEthereumInput,
        full_width=True
    )
    venmo_input = payment_group.create_ui_element(
        UI.Input,
        label="Venmo Handle (leave blank to exclude)",
        placeholder=getSetting("venmo") or "@VENMO HANDLE HERE",
        show_clear_button=True,
        onInput=checkVenmoInput,
        full_width=True
    )

    # --- Discord Commands ---

    @bot.command()
    async def ltcbal(ctx):
        addr = getSetting("litecoin")
        if not addr:
            await ctx.send("> No Litecoin address set in your UI!")
            return
        page_url = f"https://litecoinspace.org/de/address/{addr}"
        await ctx.send(
            f"**📊 Litecoin Balance Check**\n"
            f"> **Address:** `{addr}`\n"
            f"> [Click here to view your LTC balance & transactions]({page_url})"
        )

    @bot.command()
    async def paypal(ctx):
        email = getSetting("paypal")
        if not email:
            await ctx.send("> No PayPal email set!")
            return
        msg = (
            "**• Payment Regulations •**\n"
            "- Send via Friends & Family\n"
            "- Send in Euro (€)\n"
            "- No Notes attached\n"
            "- Attach a Screenshot of the Transaction Summary once the Funds have been sent.\n\n"
            f"**PayPal:** `{email}`"
        )
        await ctx.send(msg)

    @bot.command()
    async def addy(ctx):
        ltc = getSetting("litecoin")
        if not ltc:
            await ctx.send("> No LTC address set!")
            return
        msg = (
            "**Litecoin Payment Info**\n"
            f"**Address:** `{ltc}`\n"
            "\nAttach a Screenshot of the TXID once the Funds have been sent."
        )
        await ctx.send(msg)

    @bot.command()
    async def payment(ctx):
        await ctx.message.delete()
        payments = {
            "PayPal": getSetting("paypal"),
            "CashApp": getSetting("cashapp"),
            "Litecoin": getSetting("litecoin"),
            "Solana": getSetting("solana"),
            "Ethereum": getSetting("ethereum"),
            "Venmo": getSetting("venmo"),
        }
        msg = "**💳 Payment Methods & Regulations 💳**\n"
        if payments["PayPal"]:
            msg += (
                "\n__**PayPal**__\n"
                "- Send via Friends & Family\n"
                "- Send in Euro (€)\n"
                "- No Notes attached\n"
                "- Attach a Screenshot of the Transaction Summary once the Funds have been sent.\n"
                f"> `{payments['PayPal']}`\n"
            )
        if payments["Litecoin"]:
            msg += (
                "\n__**Litecoin**__\n"
                "- Attach a Screenshot of the TXID once the Funds have been sent.\n"
                f"> `{payments['Litecoin']}`\n"
            )
        for k in ["CashApp", "Solana", "Ethereum", "Venmo"]:
            if payments[k]:
                msg += f"\n__**{k}**__\n> `{payments[k]}`\n"
        if msg == "**💳 Payment Methods & Regulations 💳**\n":
            msg += "> No payment methods have been set up."
        await ctx.send(msg)

    payment_tab.render()

paymentSettings()
