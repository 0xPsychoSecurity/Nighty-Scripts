@nightyScript(
    name="Global user search", 
    author="nighty.one",
    description="UI Script | Search any user based on their Discord ID", 
    usage="UI Script"
)
def globalUserSearch():
    u_tab = Tab(name='User search', title="Global user search", icon="search")
    u_container = u_tab.create_container(type="columns")
    u_card = u_container.create_card(height="full", width="full", gap=3)

    # text2 = textgroup.create_ui_element(UI.Text, content="Input your email address and press Submit", color="#bcc7d1", size="sm")
    u_group = u_card.create_group(type="columns", gap=3, full_width=True)

    u_card2 = u_container.create_card()
    user_banner_group = u_card2.create_group(type="rows", gap=5)
    user_group = u_card2.create_group(type="columns", gap=5)
    user_av_group = user_group.create_group(type="columns", gap=5)
    user_name_group = user_group.create_group(type="rows", gap=0)
    user_badges_group = user_name_group.create_group(type="columns", gap=0)
    u_info_group = u_card2.create_group(type="rows", gap=0)

    u_input = u_group.create_ui_element(UI.Input, label="User ID", full_width=True, show_clear_button=True, required=True)
    transparent_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/HD_transparent_picture.png/1280px-HD_transparent_picture.png"
    
    ui_banner = user_banner_group.create_ui_element(UI.Image, url=transparent_image, circle=False, shadow=True, width="472px", fill_type="cover", margin='mx-5', visible=False)
    ui_avatar = user_av_group.create_ui_element(UI.Image, url=transparent_image, circle=True, shadow=True, width="100px", fill_type="cover", margin='ml-5', visible=False)
    # ui_avatar_deco = user_av_group.create_ui_element(UI.Image, url=transparent_image, circle=True, shadow=False, width="100px", fill_type="cover")
    ui_badges = []
    for x in range(13):
        ui_badges.append(user_badges_group.create_ui_element(UI.Image, url=transparent_image, circle=False, shadow=False, width="25px", margin="mt-5", visible=False))
    ui_displayname = user_name_group.create_ui_element(UI.Text, content=" ", size="xl", weight="bold", color="#FFFFFF", margin="mt-1", visible=False)
    ui_username = user_name_group.create_ui_element(UI.Text, content=" ", size="tiny", weight="light", color="#666666", visible=False)
    ui_createdat = u_info_group.create_ui_element(UI.Text, content=" ", size="sm", color="#FFFFFF", margin="mt-1", visible=False)
    ui_themecolor1 = u_info_group.create_ui_element(UI.Text, content=" ", size="sm", color="#FFFFFF", margin="mt-1", visible=False)
    ui_themecolor2 = u_info_group.create_ui_element(UI.Text, content=" ", size="sm", color="#FFFFFF", margin="mt-1", visible=False)
    ui_bio = u_info_group.create_ui_element(UI.Text, content=" ", size="sm", color="#FFFFFF", margin="mt-1", visible=False)

    def toggleVisibility(toggle: bool):
        u_input.value = ""
        u_button.disabled = True
        ui_avatar.visible = toggle
        ui_displayname.visible = toggle
        ui_username.visible = toggle
        for badge in ui_badges:
            badge.visible = toggle
            if not toggle:
                badge.url = transparent_image
        ui_createdat.visible = toggle

    async def buttonClick():
        u_button.loading = True
        try:
            user = await bot.fetch_user(int(u_input.value))
            try:
                profile = await user.profile()
            except discord.NotFound:
                profile = None
        except discord.NotFound:
            user = None
        if user:
            toggleVisibility(False)
            
            if user.display_banner:
                ui_banner.visible = True
                ui_banner.url = user.display_banner.url
            else:
                ui_banner.visible = False
            ui_avatar.url = user.display_avatar.url
            ui_displayname.content = user.display_name
            username = user.name
            ui_createdat.content = f'Created on {user.created_at.strftime("%d %B %Y, at %H:%M:%S")}'
            if profile:
                if profile.metadata.pronouns:
                    username = user.name + " • " + profile.metadata.pronouns
                badge_count = 0
                for badge in profile.badges:
                    ui_badges[badge_count].url = badge.url
                    badge_count += 1
                if profile.metadata.theme_colors:
                    themecolor1 = profile.metadata.theme_colors[0]
                    themecolor2 = profile.metadata.theme_colors[1]
                    themecolor1_hex = colour.Color(rgb=(themecolor1.r/255, themecolor1.g/255, themecolor1.b/255)).hex_l
                    themecolor2_hex = colour.Color(rgb=(themecolor2.r/255, themecolor2.g/255, themecolor2.b/255)).hex_l

                    ui_themecolor1.content = "Primary color: " + themecolor1_hex
                    ui_themecolor1.color = str(themecolor1_hex)

                    ui_themecolor2.content = "Accent color: " + themecolor2_hex
                    ui_themecolor2.color = str(themecolor2_hex)
                    ui_themecolor1.visible = True
                    ui_themecolor2.visible = True
                else:
                    ui_themecolor1.visible = False
                    ui_themecolor2.visible = False
                if profile.bio:
                    ui_bio.visible = True
                    ui_bio.content = "Bio: " + profile.bio
                else:
                    ui_bio.visible = False
                  
            ui_username.content = username
            toggleVisibility(True)
            u_button.loading = False
        else:
            u_input.invalid = True
            u_input.error_message = "User not found"
            u_button.loading = False
            u_tab.toast(type="ERROR", title="User not found", description=f"User {u_input.value} not found")
    u_button = u_card.create_ui_element(UI.Button, label='Search', disabled=True, full_width=True, onClick=buttonClick)

    def testOnInput(new_value):
        if new_value == "" or new_value == " ":
            u_button.disabled = True
            u_input.invalid = False
            u_input.error_message = None
            return
        if len(new_value) > 15 and new_value.isdigit():
            u_input.invalid = False
            u_input.error_message = None
            u_button.disabled = False
            return
        u_input.invalid = True
        u_input.error_message = "Invalid User ID"
            

    u_input.onInput = testOnInput

    u_tab.render()

globalUserSearch()
