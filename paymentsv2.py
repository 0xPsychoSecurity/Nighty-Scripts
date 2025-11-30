@nightyScript(
    name="Payment Settings V2",
    author="Twister x Rico",
    description="UI Script | Configure payment information display through a user interface",
    usage="UI Script"
)
def paymentSettings():
    import os, json, re

    # Dateipfad
    os.makedirs(f'{getScriptsPath()}/scriptData', exist_ok=True)
    script_config_path = f"{getScriptsPath()}/scriptData/payments.json"

    # Standardfelder inkl. Solana und Ethereum
    default_settings = {
        "paypal": "",
        "cashapp": "",
        "litecoin": "",
        "solana": "",
        "ethereum": "",
        "venmo": ""
    }

    # Robust: payments.json automatisch reparieren!
    def loadSettings():
        if os.path.exists(script_config_path):
            try:
                with open(script_config_path, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                # Defaultfelder ergänzen/abschneiden
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

    # Validierung
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

    # Universelle Input-Prüfung
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
        return validateInput(new_value, paypal_input, isValidPaypal, "paypal", "Ungültiges PayPal Format.")

    def checkCashtagInput(new_value):
        return validateInput(new_value, cashtag_input, isValidCashtag, "cashapp", "Ungültiger CashApp Tag. Muss mit $ und 1-15 Alphanumerisch sein.")

    def checkLtcInput(new_value):
        return validateInput(new_value, ltc_input, isValidCryptoAddress, "litecoin", "Ungültige Litecoin Adresse.")

    def checkVenmoInput(new_value):
        return validateInput(new_value, venmo_input, isValidVenmo, "venmo", "Ungültiges Venmo Handle, muss mit @ beginnen.")

    def checkSolanaInput(new_value):
        return validateInput(new_value, solana_input, isValidSolana, "solana", "Ungültige Solana-Adresse.")

    def checkEthereumInput(new_value):
        return validateInput(new_value, ethereum_input, isValidEthereum, "ethereum", "Ungültige Ethereum-Adresse.")

    # Nighty UI Tab
    payment_tab = Tab(name="Payment Settings", title="Payment Settings", icon="calc")
    p_container = payment_tab.create_container(type="columns")
    payment_card = p_container.create_card(height="full", width="full", gap=4)

    payment_card.create_ui_element(UI.Text, content="Payment Methods", size="xl", weight="bold")
    payment_card.create_ui_element(UI.Text, content=f"To send your payment methods, use the {bot.command_prefix}payments command.", size="base", weight="bold", margin="mt-2")

    payment_group = payment_card.create_group(type="columns", gap=3, full_width=True)

    # Inputs
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
        placeholder=getSetting("litecoin") or "LTC ADDY HERE",
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
        valid_payments = [f"> {name}: **{value}**" for name, value in payments.items() if value]
        if valid_payments:
            instructions = (
                "**💳 Payment Instructions 💳**\n\n"
                "1️⃣ Ensure the transaction is completed successfully.\n"
                "2️⃣ Provide a screenshot of the transaction details as proof of payment.\n"
                "3️⃣ Make sure the screenshot is **clear** and **uncropped**.\n\n"
                "**⚠️ Rules for Payment ⚠️**\n"
                "- Double-check the address before sending funds.\n"
                "- **All payments are non-refundable** in case of errors or incorrect transactions.\n"
                "- Do **NOT** include any notes or memos with the transaction. (Incase of cashapp use *discord* as the note) \n\n"
                "### Accepted Payment Methods ###\n"
                + "\n".join(valid_payments)
            )
            await ctx.send(instructions)
        else:
            await ctx.send("> No payment methods have been set up.")

    payment_tab.render()

paymentSettings()
