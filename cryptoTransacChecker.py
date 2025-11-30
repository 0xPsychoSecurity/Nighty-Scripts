import requests
import json
import os

@nightyScript(
    name="Universal TX Checker",
    author="icetea_lemon",
    description="Checks BTC, BCH, ETH, LTC, DOGE, DASH (via BlockCypher) and SOL (via public RPC).",
    usage="UI Script | Enter TX hash only"
)
def UniversalTxChecker():
    settings_path = f"{getScriptsPath()}/cryptoTransacChecker.json"

    def load_settings():
        defaults = {
            "token": "YOUR_BLOCKCYPHER_TOKEN_HERE",
        }
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    defaults.update(settings)
                    return defaults
            except (json.JSONDecodeError, KeyError):
                pass
        return defaults

    def save_settings(settings_dict):
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings_dict, f, indent=4)

    settings = load_settings()

    tab = Tab(name="Universal Tx", title="Universal TX Checker", icon="search")
    container = tab.create_container(type="rows")

    card = container.create_card(
        title="Check Transaction", 
        width="full", 
        gap=4
    )
    
    tx_input = card.create_group(type="columns", gap=3, full_width=True).create_ui_element(
        UI.Input,
        label="Transaction ID",
        value="",
        onChange=lambda v: None
    )

    result_text = card.create_ui_element(
        UI.Text,
        content="Waiting for TX hash...",
        size="sm",
        color="#888"
    )
    
    result_card = container.create_card(title="Transaction Details", width="full", gap=4, visible=False)

    ui_coin = result_card.create_ui_element(UI.Text, content="Coin: ", size="sm")
    ui_confirmations = result_card.create_ui_element(UI.Text, content="Confirmations: ", size="sm")
    ui_from = result_card.create_ui_element(UI.Text, content="From: ", size="sm")
    ui_amount = result_card.create_ui_element(UI.Text, content="Amount: ", size="sm")
    
    def fetch_solana_rpc(txid):
        try:
            endpoint = "https://api.mainnet-beta.solana.com"
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTransaction",
                "params": [
                    txid,
                    {"encoding": "jsonParsed", "commitment": "confirmed"}
                ]
            }
            r = requests.post(endpoint, json=payload, timeout=8)
            if r.status_code != 200:
                return None
            
            data = r.json()
            result = data.get('result')
            if not result:
                return None

            meta = result.get('meta', {})
            if meta.get('err') is not None:
                status = "❌ Failed"
            else:
                status = "✅ Success"

            lamports = 0
            sender = "N/A"
            instructions = result.get('transaction', {}).get('message', {}).get('instructions', [])
            for inst in instructions:
                if inst.get('program') == 'system' and inst.get('parsed', {}).get('type') == 'transfer':
                    info = inst['parsed']['info']
                    lamports = info.get('lamports', 0)
                    sender = info.get('source', 'N/A')
                    break 
            
            amount_sol = lamports / 1_000_000_000

            return {
                "coin": "SOL",
                "status": f"{status} (Slot: {result.get('slot', 'N/A')})",
                "from": sender,
                "amount": f"{amount_sol:.8f}"
            }
        except Exception as e:
            return None

    def fetch_blockcypher(coin, txid, token):
        try:
            url = f"https://api.blockcypher.com/v1/{coin.lower()}/main/txs/{txid}?token={token}"
            r = requests.get(url, timeout=8)
            if r.status_code != 200:
                return None
            d = r.json()
            coin_info = {
                "btc": {"unit": 10**8, "name": "BTC"},
                "bch": {"unit": 10**8, "name": "BCH"},
                "eth": {"unit": 10**18, "name": "ETH"},
                "ltc": {"unit": 10**8, "name": "LTC"},
                "doge": {"unit": 10**8, "name": "DOGE"},
                "dash": {"unit": 10**8, "name": "DASH"},
            }
            output_value = d.get("total", 0) or d.get("value", 0)
            amount = output_value / coin_info.get(coin.lower(), {"unit": 1})["unit"]
            
            return {
                "coin": coin_info.get(coin.lower(), {"name": coin.upper()})["name"],
                "confirmations": d.get("confirmations", "N/A"),
                "from": d.get("addresses", ["?"])[0],
                "amount": f"{amount:.8f}"
            }
        except Exception as e:
            return None

    def on_check():
        txid = tx_input.value.strip()
        if not txid:
            result_text.content = "⚠️ Please enter a valid transaction hash."
            return

        bc_token = settings.get("token")
        
        is_solana_like = len(txid) > 70
        if (not bc_token or bc_token == "YOUR_BLOCKCYPHER_TOKEN_HERE") and not is_solana_like:
            result_text.content = "⚠️ Please set your BlockCypher API token in the settings for non-Solana transactions."
            return

        result_card.visible = False
        tx_found = False

        if not is_solana_like and bc_token and bc_token != "YOUR_BLOCKCYPHER_TOKEN_HERE":
            supported_coins = ["BTC", "BCH", "ETH", "LTC", "DOGE", "DASH"]
            for coin in supported_coins:
                result_text.content = f"⏳ Checking BlockCypher for {coin}..."
                tx = fetch_blockcypher(coin, txid, bc_token)
                if tx:
                    confirmations = tx['confirmations']
                    status_text = ""
                    try:
                        num_confirmations = int(confirmations)
                        if num_confirmations >= 6:
                            status_text = f"✅ Confirmed ({num_confirmations} blocks passed)"
                        elif num_confirmations > 0:
                            status_text = f"⏳ Pending ({num_confirmations}/6 blocks)"
                        else:
                            status_text = "⌛ Unconfirmed (In mempool)"
                    except (ValueError, TypeError):
                        status_text = "N/A"

                    ui_coin.content = f"Coin: {tx['coin']}"
                    ui_confirmations.content = f"Status: {status_text}"
                    ui_from.content = f"From: {tx['from']}"
                    ui_amount.content = f"Amount: {tx['amount']} {tx['coin']}"
                    result_card.visible = True
                    result_text.content = f"✅ Transaction found on the {coin} blockchain."
                    tx_found = True
                    return

        if not tx_found:
            result_text.content = f"⏳ Checking Solana for SOL..."
            tx = fetch_solana_rpc(txid)
            if tx:
                ui_coin.content = f"Coin: {tx['coin']}"
                ui_confirmations.content = f"Status: {tx['status']}"
                ui_from.content = f"From: {tx['from']}"
                ui_amount.content = f"Amount: {tx['amount']} {tx['coin']}"
                result_card.visible = True
                result_text.content = f"✅ Transaction found on the Solana blockchain."
                return
        
        if is_solana_like and not tx_found:
             if bc_token and bc_token != "YOUR_BLOCKCYPHER_TOKEN_HERE":
                supported_coins = ["BTC", "BCH", "ETH", "LTC", "DOGE", "DASH"]
                for coin in supported_coins:
                    result_text.content = f"⏳ Checking BlockCypher for {coin}..."
                    tx = fetch_blockcypher(coin, txid, bc_token)
                    if tx:
                        confirmations = tx['confirmations']
                        status_text = ""
                        try:
                            num_confirmations = int(confirmations)
                            if num_confirmations >= 6:
                                status_text = f"✅ Confirmed ({num_confirmations} blocks passed)"
                            elif num_confirmations > 0:
                                status_text = f"⏳ Pending ({num_confirmations}/6 blocks)"
                            else:
                                status_text = "⌛ Unconfirmed (In mempool)"
                        except (ValueError, TypeError):
                            status_text = "N/A"

                        ui_coin.content = f"Coin: {tx['coin']}"
                        ui_confirmations.content = f"Status: {status_text}"
                        ui_from.content = f"From: {tx['from']}"
                        ui_amount.content = f"Amount: {tx['amount']} {tx['coin']}"
                        result_card.visible = True
                        result_text.content = f"✅ Transaction found on the {coin} blockchain."
                        tx_found = True
                        return

        result_text.content = "❌ Transaction not found on any supported blockchain."

    token_input = card.create_ui_element(
        UI.Input,
        label="BlockCypher API Token",
        value=settings.get("token", ""),
        full_width=True,
        visible=False
    )
    
    def on_save_settings():
        new_token = token_input.value.strip()
        if new_token:
            settings["token"] = new_token
            save_settings(settings)
            tab.toast(type="SUCCESS", title="Settings Saved", description="API Token has been updated.")
        else:
            tab.toast(type="ERROR", title="Save Error", description="Token cannot be empty.")

    save_button = card.create_ui_element(
        UI.Button, 
        label="Save Token", 
        color="primary", 
        onClick=on_save_settings, 
        visible=False
    )

    def toggle_settings():
        is_visible = not token_input.visible
        token_input.visible = is_visible
        save_button.visible = is_visible

    button_group = card.create_group(type="columns", gap=3, full_width=True)
    button_group.create_ui_element(UI.Button, label="Check TX", color="success", onClick=on_check)
    button_group.create_ui_element(UI.Button, label="Settings", color="primary", variant="solid", onClick=toggle_settings)

    tab.render()

    @bot.command()
    async def txlookup(ctx, transactionId: str):
        if not transactionId:
            await ctx.send("❌ Please provide a transaction ID.", delete_after=10)
            return

        bc_token = settings.get("token")
        is_solana_like = len(transactionId) > 70
        
        if (not bc_token or bc_token == "YOUR_BLOCKCYPHER_TOKEN_HERE") and not is_solana_like:
            await ctx.send("⚠️ Please set a BlockCypher API token for non-Solana transactions.", delete_after=10)
            return

        msg = await ctx.send(f"⏳ Searching for transaction `{transactionId}`...")

        tx_found_cmd = False
        # Check BlockCypher first, unless it looks like a Solana tx
        if not is_solana_like and bc_token and bc_token != "YOUR_BLOCKCYPHER_TOKEN_HERE":
            supported_coins = ["BTC", "BCH", "ETH", "LTC", "DOGE", "DASH"]
            for coin in supported_coins:
                await msg.edit(content=f"⏳ Checking on **{coin}**...")
                tx = fetch_blockcypher(coin, transactionId, bc_token)
                if tx:
                    confirmations = tx['confirmations']
                    status_text = ""
                    try:
                        num_confirmations = int(confirmations)
                        if num_confirmations >= 6:
                            status_text = f"✅ **Confirmed** ({num_confirmations} blocks passed)"
                        elif num_confirmations > 0:
                            status_text = f"⏳ **Pending** ({num_confirmations}/6 blocks)"
                        else:
                            status_text = "⌛ **Unconfirmed** (In mempool)"
                    except (ValueError, TypeError):
                        status_text = "Status: N/A"

                    response = (
                        f"**Transaction Found on {tx['coin']}**\n"
                        f"Status: {status_text}\n"
                        f"From: `{tx['from']}`\n"
                        f"Amount: **{tx['amount']} {tx['coin']}**"
                    )
                    await msg.edit(content=response)
                    tx_found_cmd = True
                    return
        
        if not tx_found_cmd:
            await msg.edit(content=f"⏳ Checking on **SOL** (Solana)...")
            tx = fetch_solana_rpc(transactionId)
            if tx:
                response = (
                    f"**Transaction Found on {tx['coin']}**\n"
                    f"Status: {tx['status']}\n"
                    f"From: `{tx['from']}`\n"
                    f"Amount: **{tx['amount']} {tx['coin']}**"
                )
                await msg.edit(content=response)
                return
        
        if is_solana_like and not tx_found_cmd:
             if bc_token and bc_token != "YOUR_BLOCKCYPHER_TOKEN_HERE":
                supported_coins = ["BTC", "BCH", "ETH", "LTC", "DOGE", "DASH"]
                for coin in supported_coins:
                    await msg.edit(content=f"⏳ Checking on **{coin}**...")
                    tx = fetch_blockcypher(coin, transactionId, bc_token)
                    if tx:
                        confirmations = tx['confirmations']
                        status_text = ""
                        try:
                            num_confirmations = int(confirmations)
                            if num_confirmations >= 6:
                                status_text = f"✅ **Confirmed** ({num_confirmations} blocks passed)"
                            elif num_confirmations > 0:
                                status_text = f"⏳ **Pending** ({num_confirmations}/6 blocks)"
                            else:
                                status_text = "⌛ **Unconfirmed** (In mempool)"
                        except (ValueError, TypeError):
                            status_text = "Status: N/A"

                        response = (
                            f"**Transaction Found on {tx['coin']}**\n"
                            f"Status: {status_text}\n"
                            f"From: `{tx['from']}`\n"
                            f"Amount: **{tx['amount']} {tx['coin']}**"
                        )
                        await msg.edit(content=response)
                        return


        await msg.edit(content=f"❌ Transaction `{transactionId}` not found on any supported blockchain.")

UniversalTxChecker()
