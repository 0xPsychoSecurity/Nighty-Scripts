gtlb_task = None
@nightyScript(
    name="Login Manager", 
    author="nes",
    description='Notify or block login attempts on your account via the gateway. Some may refer to this as an "anti token log". However, it does not protect against HTTP-based attacks, which are the most common method used in token logging. This feature only detects logins made through the gateway (e.g., discord.com/login).', 
    usage='UI script'
)
def gatewayLoginManager():
    global gtlb_task

    async def initializeLoginManager():
        if gtlb_task and not gtlb_task.done():
            gtlb_task.cancel()
            try:
                await gtlb_task
            except asyncio.CancelledError:
                pass

        while not bot.loop.is_running():
            await asyncio.sleep(1)

        os.makedirs(f'{getScriptsPath()}/scriptData', exist_ok=True)
        script_config_path = f"{getScriptsPath()}/scriptData/gatewayLoginManager.json"
        
        def updateSetting(key, value):
            settings = json.load(open(script_config_path, 'r', encoding="utf-8", errors="ignore")) if os.path.exists(script_config_path) else {}
            settings[key] = value
            json.dump(settings, open(script_config_path, 'w', encoding="utf-8", errors="ignore"), indent=2)

        def getSetting(key=None):
            if os.path.exists(script_config_path):
                with open(script_config_path, 'r', encoding="utf-8", errors="ignore") as f:
                    settings = json.load(f)
                return settings.get(key) if key else settings
            return None if key else {}
        
        
        async def fetchCountryFlags():
            async with ClientSession() as session:
                async with session.get("https://restcountries.com/v3.1/all", ssl=False) as response:
                    if response.status == 200:
                        data = await response.json()
                        flag_lookup = {}
                        for country in data:
                            common_name = country.get("name", {}).get("common", "Unknown")
                            official_name = country.get("name", {}).get("official", "Unknown")
                            flag_url = country.get("flags", {}).get("png", "")

                            flag_lookup[common_name] = flag_url
                            flag_lookup[official_name] = flag_url
                        
                        return flag_lookup
                    else:
                        logging.info(f"Failed to fetch countries flags data: {response.status} - {await response.text()}")
                        return {}

        async def fetchCountries():
            async with ClientSession() as session:
                async with session.get("https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/refs/heads/master/json/countries%2Bstates.json", ssl=False) as response:
                    if response.status == 200:
                        text = await response.text()
                        try:
                            data = json.loads(text)
                            country_flags = await fetchCountryFlags()
                            countries = []
                            for country in data:
                                country_name = country["name"]
                                country_data = {"id": country_name, "title": country_name}
                                
                                flag_url = country_flags.get(country_name, None)
                                country_data["iconUrl"] = flag_url if flag_url else "https://mostersstoffer.dk/wp-content/uploads/2021/07/k001-1387.jpg"
                                countries.append(country_data)
                            
                            return sorted(countries, key=lambda x: x["title"])
                        except json.JSONDecodeError as e:
                            logging.info(f"Failed to parse JSON: {e}")
                            return []
                    else:
                        logging.info(f"Failed to fetch countries data: {response.status} - {await response.text()}")
                        return []

        async def fetchStates():
            async with ClientSession() as session:
                async with session.get("https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/refs/heads/master/json/countries%2Bstates.json", ssl=False) as response:
                    if response.status == 200:
                        text = await response.text()
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError as e:
                            logging.info(f"Failed to parse JSON: {e}")
                            return []
                    else:
                        logging.info(f"Failed to fetch states data: {response.status} - {await response.text()}")
                        return []
        

        async def getApiSessions():
            return await bot.http.request(discord.http.Route('GET', "/auth/sessions"))
        
        all_countries = await fetchCountries()
        all_states = await fetchStates()
        startup_sessions = await getApiSessions()

        def getStatesPerCountries(selected_countries):
            country_states = [{"id": "Select states", "title": "Select states"}]
            
            for country in all_states:
                if country["name"] in selected_countries:
                    for state in country["states"]:
                        country_states.append({"id": state, "title": state})

            return country_states
        

        def toggleGTL(checked):
            updateSetting("notify", checked)
            if checked:
                gtla_toggle.checked = (not checked)
                updateSetting("notify+ask", (not checked))

        def toggleGTLA(checked):
            updateSetting("notify+ask", checked)
            if checked:
                gtl_toggle.checked = (not checked)
                gtlb_toggle.checked = (not checked)
                updateSetting("notify", (not checked))
                updateSetting("block", (not checked))
                gtlb_tab.toast(type="ERROR", title="Not Implemented", description="Notify & Ask has still yet to be implemented, for now it will only notify you.")
            currentPass_input.visible = checked

        def toggleGTLB(checked):
            updateSetting("block", checked)
            if checked:
                gtla_toggle.checked = (not checked)
                updateSetting("notify+ask", (not checked))
            currentPass_input.visible = checked
            # newPass_input.visible = checked

        def setCurrentPassword(current_pass):
            updateSetting("password", current_pass)

        def setPassword(new_pass):
            updateSetting("newPassword", new_pass)

        def updateWhitelistedCountries(countries):
            updateSetting("whitelisted_countries", countries)
            state_selection.visible = (len(countries) > 0)
            states_text.visible = (len(countries) > 0)
            state_selection.items = getStatesPerCountries(countries)
            country_selection.selected_items = countries

        def updateWhitelistedStates(states):
            updateSetting("whitelisted_states", states)

        gtlb_tab = Tab(name='Login Manager', title="Login Manager (formerly: Session Manager)", icon="lock")
        gtlb_container = gtlb_tab.create_container(type="rows")
        gtlb_card = gtlb_container.create_card(height="full", width="full", gap=3)

        gtlb_card.create_ui_element(UI.Text, content="New Logins", size="base", weight="bold")

        notify_n_block = gtlb_card.create_group(type="columns", gap=6, full_width=True)
        gtl_toggle = notify_n_block.create_ui_element(UI.Toggle, label="Notify", checked=getSetting("notify"), onChange=toggleGTL)
        gtla_toggle = notify_n_block.create_ui_element(UI.Toggle, label="Notify & Ask", checked=getSetting("notify+ask"), onChange=toggleGTLA)
        gtlb_toggle = notify_n_block.create_ui_element(UI.Toggle, label="Block", checked=getSetting("block"), onChange=toggleGTLB)
        currentPass_input = gtlb_card.create_ui_element(UI.Input, label="Current password (required for blocking)", full_width=True, show_clear_button=True, required=True, visible=getSetting("block") or False, onInput=setCurrentPassword)
        # newPass_input = gtlb_card.create_ui_element(UI.Input, label="Optional password change (leave empty for no change)", full_width=True, show_clear_button=True, required=False, visible=getSetting("block") or False, onInput=setPassword)
        
        gtlb_card.create_ui_element(UI.Text, content="Whitelisted countries", size="base", weight="bold", margin="mt-2")
        country_selection =gtlb_card.create_ui_element(UI.Select, label="Select countries", full_width=True, selected_items=getSetting("whitelisted_countries"), mode="multiple", items=all_countries, onChange=updateWhitelistedCountries)
        
        states_to_select = getStatesPerCountries(country_selection.selected_items)
        states_text = gtlb_card.create_ui_element(UI.Text, visible=(len(country_selection.selected_items) > 0), content="Whitelisted states (If none are selected, entire country will be whitelisted)", size="base", margin="mt-2")
        state_selection = gtlb_card.create_ui_element(UI.Select, label="Select states", full_width=True, visible=(len(country_selection.selected_items) > 0), selected_items=getSetting("whitelisted_states"), mode="multiple", items=states_to_select, disabled_items=["Select states"], onChange=updateWhitelistedStates)


        async def logOutOfSession(session_id, os, platform, location):
            logging.info("Blocking session...")
            if getSetting("password") is None:
                print("Password is missing", type_="ERROR")
                return
            try:
                logoutSession = await bot.http.request(discord.http.Route('POST', "/auth/sessions/logout"), json={"session_id_hashes": [session_id]})
                print(f"Blocked login from {location}", discordChannel=f"{os} | {platform}", type_="SUCCESS")
            except discord.errors.HTTPException as e:
                if e.response.status == 401:
                    error = await e.response.json()
                    if "Two factor is required" in error.get("message"):
                        mfa_data = error.get("mfa", {})
                        mfa_ticket = mfa_data.get("ticket")
                        mfa_methods = mfa_data.get("methods", [])
                        if any(method.get("type") == "password" for method in mfa_methods):
                            try:
                                finish_mfa = await bot.http.request(discord.http.Route('POST', "/mfa/finish"), json={
                                    "ticket": mfa_ticket,
                                    "mfa_type": "password",
                                    "data": getSetting("password")
                                })

                                final_logout = await bot.http.request(discord.http.Route('POST', "/auth/sessions/logout"), json={"session_id_hashes": [session_id]}, headers={
                                    'Accept-Language': 'en-US',
                                    'Cache-Control': 'no-cache',
                                    'Connection': 'keep-alive',
                                    'Origin': 'https://discord.com',
                                    'Pragma': 'no-cache',
                                    'Referer': 'https://discord.com/channels/@me',
                                    'Sec-CH-UA': '"Google Chrome";v="{0}", "Chromium";v="{0}", ";Not-A.Brand";v="24"'.format(bot.http.browser_version.split('.')[0]),
                                    'Sec-CH-UA-Mobile': '?0',
                                    'Sec-CH-UA-Platform': '"Windows"',
                                    'Sec-Fetch-Dest': 'empty',
                                    'Sec-Fetch-Mode': 'cors',
                                    'Sec-Fetch-Site': 'same-origin',
                                    'User-Agent': bot.http.user_agent,
                                    'X-Discord-Locale': bot.http.get_locale(),
                                    'X-Super-Properties': bot.http.encoded_super_properties,
                                    "Cookie": f"__Secure-recent_mfa={finish_mfa['token']}"
                                })
                                print(f"Blocked login from {location}", discordChannel=f"{os} | {platform}", type_="SUCCESS")


                            except discord.errors.HTTPException as e:
                                mfa_error = await e.response.json()
                                print(str(mfa_error), type_="ERROR")


        def isLocationWhitelisted(location, countries, states):
            location_lower = location.lower()
            country = location_lower.strip().split(",")[-1].strip()
            if country in [c.lower() for c in countries]:
                if states:
                    return any(state.lower() in location_lower for state in states)
                else:
                    return True
            else:
                return False
            

        @bot.listen("on_socket_raw_receive")
        async def onSessionDetection(msg):
            msg = discord.utils._from_json(msg)
            if msg.get("t") == "SESSIONS_REPLACE":
                if startup_sessions is None:
                    return

                for session in bot.sessions:
                    if not session.is_current() and session.os != "unknown":
                        new_api_sessions = await getApiSessions()
                        startup_api_sessions, api_sessions = startup_sessions["user_sessions"], new_api_sessions["user_sessions"]
                        whitelisted_countries = getSetting("whitelisted_countries")
                        whitelisted_states = getSetting("whitelisted_states")
                        startup_locations = {s['client_info']['location'] for s in startup_api_sessions}
                        new_sessions = [s for s in api_sessions if not (isLocationWhitelisted(s['client_info']['location'], whitelisted_countries, whitelisted_states) or s['client_info']['location'] in startup_locations)]
                        for sess in new_sessions:
                            location = sess['client_info']['location']
                            if isLocationWhitelisted(location, whitelisted_countries, whitelisted_states) or location in startup_locations:
                                logging.info(f"Location is whitelisted, ignoring.. ({location})")
                                continue
                            if getSetting("notify"):
                                print(f"New login from {location}", discordChannel=f"{sess['client_info']['os']} | {sess['client_info']['platform']}")
                            if getSetting("block"):
                                await logOutOfSession(sess["id_hash"], sess["client_info"]["os"], sess["client_info"]["platform"], location)
                            elif getSetting("notify+ask"):
                                # todo: either using dynamic app notifications, user app buttons, or both
                                print(f"New login from {location}", discordChannel=f"{sess['client_info']['os']} | {sess['client_info']['platform']}")
                                return
                        return

        gtlb_tab.render()

    gtlb_task = bot.loop.create_task(initializeLoginManager())

gatewayLoginManager()