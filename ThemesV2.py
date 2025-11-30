@nightyScript(
    name="Custom themes v2 [BETA]", 
    author="nes @ nighty.one",
    description="Temporary builder for themes v2 while awaiting official support in Themes tab.", 
    usage="UI Script"
)
def customThemesV2Builder():
    v2_variants = [
        {"id": "text", "title": "Text", "color": "blue"},
        {"id": "image", "title": "Image", "color": "yellow"},
        {"id": "section", "title": "Section", "color": "orange"},
        {"id": "separator", "title": "Separator", "color": "green"}
    ]
    def isValidUrl(string):
        regex = re.compile(r'^(https?)://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
        return bool(regex.match(string)) or not string
    
    def getCurrentThemes():
        themes = []
        for theme in getThemesData():
            themes.append({"id": theme, "title": theme})
        return themes

    def updateCurrentTheme():
        current_theme.items = getCurrentThemes()

    def resetUIVariant(show_v1=False, show_v2=False, show_content=False, show_separator=False, show_add_btn=False):
        value1_variant.visible = show_v1
        value2_variant.visible = show_v2
        content_display_variant.visible = show_content
        separator_variant.visible = show_separator
        add_variant_btn.visible = show_add_btn

        if not show_v1:
            value1_variant.value = None
            value1_variant.required = False

        if not show_v2:
            value2_variant.value = None
            value2_variant.required = False

    def onSelectedTheme(selected_items):
        try:
            selected_theme = selected_items[0]
            current_theme.items = getCurrentThemes()
            resetUIVariant()
            variant_selector.selected_items = []

            theme_data = getThemeData(theme_name=selected_theme)
            if theme_data.get("v2"):
                display_variants_table.rows = []
                for layout_item in theme_data["v2"]["layout"]:
                    if "section" in layout_item:
                        section_data = layout_item["section"]
                        insertVariantRow("section", section_data["text"], section_data["thumbnail"], extras={})
                    else:
                        for layout_k, layout_v in layout_item.items():
                            insertVariantRow(layout_k, layout_v, " ", extras={})
                build_theme_btn.visible = True
                color_selector.selected_items = [theme_data["v2"]["color"]]
            else:
                display_variants_table.rows = []
                build_theme_btn.visible = False
        except:
            pass

    def onSelectedVariant(selected_items):
        selected_variant = selected_items[0]
        updateCurrentTheme()

        if selected_variant == "text":
            value1_variant.label = "Text"
            value1_variant.required = True
            resetUIVariant(show_v1=True, show_content=True, show_add_btn=True)
        elif selected_variant == "image":
            value1_variant.label = "Image URL"
            value1_variant.required = True
            resetUIVariant(show_v1=True, show_add_btn=True)
        elif selected_variant == "section":
            value1_variant.label = "Text"
            value2_variant.label = "Image URL"
            value1_variant.required = True
            value2_variant.required = False
            resetUIVariant(show_v1=True, show_v2=True, show_content=True, show_add_btn=True)
        else:
            resetUIVariant(show_separator=True, show_add_btn=True)

    def insertVariantRow(variant, value, extra_value=" ", extras={}):
        variant_data = next((variant_type for variant_type in v2_variants if variant_type["id"] == variant), False)
        if variant_data:
            extras["variant"] = variant
            display_variants_table.insert_rows([{
                "id": str(uuid.uuid4()),
                "cells": [
                    {
                        "text": variant_data["title"],
                        "color": variant_data["color"]
                    },
                    {
                        "text": value
                    },
                    {
                        "text": extra_value
                    },
                    extras
                ]
            }],
            position=len(display_variants_table.rows))

    def AddVariant():
        selected_variant = variant_selector.selected_items[0]
        if value1_variant.label == "Text" and selected_variant in ("text", "section"):
            if content_display_variant.checked:
                value1_variant.value = r"{content}"
            if not value1_variant.value:
                return themesV2_tab.toast(type="ERROR", title="Text is missing/empty", description="Input text")
        if value1_variant.label == "Image URL" and selected_variant == "image":
            if not value1_variant.value:
                return themesV2_tab.toast(type="ERROR", title="Image URL is missing/empty", description="Input image url")
            elif not isValidUrl(value1_variant.value):
                return themesV2_tab.toast(type="ERROR", title="Image URL is invalid", description="Input a valid image url")
        if value2_variant.label == "Image URL" and selected_variant == "section":
            if not value2_variant.value:
                return themesV2_tab.toast(type="ERROR", title="Image URL is missing/empty", description="Input image url")
            elif not isValidUrl(value2_variant.value):
                return themesV2_tab.toast(type="ERROR", title="Image URL is invalid", description="Input a valid image url")
        if selected_variant == "separator":
            if not separator_variant.selected_items:
                return themesV2_tab.toast(type="ERROR", title="Separator Type", description="Select a separator type")
            value1_variant.value = separator_variant.selected_items[0]
        insertVariantRow(selected_variant, value1_variant.value, value2_variant.value if value2_variant.value else " ", extras={})
        build_theme_btn.visible = True

    def includesContent(rows):
        return any(
            row["cells"][3].get("variant") in ("text", "section") and "{content}" in row["cells"][1].get("text", "")
            for row in rows
            if len(row.get("cells", [])) >= 4
        )

    def getVariantRow(row_id):
        return next((entry for entry in display_variants_table.rows if entry["id"] == row_id), None)

    def deleteVariant(row_id):
        row = getVariantRow(row_id)
        display_variants_table.delete_rows([row["id"]])
        if not display_variants_table.rows:
            build_theme_btn.visible = False

    def moveUpVariant(row_id):
        rows = display_variants_table.rows
        for index, row in enumerate(rows):
            if row["id"] == row_id and index > 0:
                rows[index], rows[index - 1] = rows[index - 1], rows[index]
                break
        display_variants_table.rows = rows

    def moveDownVariant(row_id):
        rows = display_variants_table.rows
        for index, row in enumerate(rows):
            if row["id"] == row_id and index < len(rows) - 1:
                rows[index], rows[index + 1] = rows[index + 1], rows[index]
                break
        display_variants_table.rows = rows
    
    def buildV2Theme(rows, color):
        layout = []

        for row in rows:
            cells = row["cells"]
            variant = cells[3]["variant"]

            if variant == "image":
                layout.append({"image": cells[1]["text"]})

            elif variant == "separator":
                layout.append({"separator": cells[1]["text"]})

            elif variant == "section":
                layout.append({
                    "section": {
                        "text": cells[1]["text"],
                        "thumbnail": cells[2]["text"]
                    }
                })

            elif variant == "text":
                layout.append({"text": cells[1]["text"]})

        return {
            "enabled": True,
            "color": color,
            "layout": layout
        }

    def buildTheme():
        # logging.info(display_variants_table.rows)
        if includesContent(display_variants_table.rows):
            try:
                v2_theme = buildV2Theme(display_variants_table.rows, color_selector.selected_items[0])
                selected_theme = current_theme.selected_items[0]
                theme_data = getThemeData(theme_name=selected_theme)
                theme_data["v2"] = v2_theme
                json.dump(theme_data, open(f"{getDataPath()}/themes/{selected_theme}.json", 'w', encoding="utf-8", errors="ignore"), indent=2)
                return themesV2_tab.toast(type="SUCCESS", title="Success", description="Theme built!")
            except Exception as e:
                return themesV2_tab.toast(type="ERROR", title="An error occurred", description=e)

    themesV2_tab = Tab(
        name="Themes V2", 
        title="Themes V2 Builder [BETA]", 
        icon="palette"
    )
    wrapper_container = themesV2_tab.create_container(type="columns", gap=2)

    left_container = wrapper_container.create_container(type="rows", gap=2)
    right_container = wrapper_container.create_container(type="columns", gap=5)
    
    currentTheme_card = left_container.create_card(height="auto", width="full", gap=0, disallow_shrink=True)
    currentTheme_card.create_ui_element(UI.Text, content="Applying your theme still happens through the Themes tab.", size="tiny", weight="light", align="center")
    current_theme = currentTheme_card.create_ui_element(UI.Select, label="Editing theme", items=getCurrentThemes(), mode="single", onChange=onSelectedTheme, selected_items=[getConfigData()['theme']], margin="mt-2", full_width=True)

    themeBuilder_card = left_container.create_card(height="full", width="full", gap=2)
    
    def colorUrl(bg, fg="000000"):
        return f"https://dummyimage.com/32x32/{bg.strip('#')}/{fg}&text=+"
    
    color_variants_raw = [
        ("#ffffff", "White", "000000"),
        ("#000000", "Black", "ffffff"),
        ("#ff0000", "Red", "ffffff"),
        ("#8b0000", "Dark Red", "ffffff"),
        ("#ffa500", "Orange", "000000"),
        ("#ff8c00", "Dark Orange", "000000"),
        ("#ffff00", "Yellow", "000000"),
        ("#ffd700", "Gold", "000000"),
        ("#ffffe0", "Light Yellow", "000000"),
        ("#adff2f", "Green Yellow", "000000"),
        ("#008000", "Green", "ffffff"),
        ("#006400", "Dark Green", "ffffff"),
        ("#00ff00", "Lime", "000000"),
        ("#7fff00", "Chartreuse", "000000"),
        ("#32cd32", "Lime Green", "000000"),
        ("#00ffff", "Cyan", "000000"),
        ("#00ced1", "Dark Turquoise", "000000"),
        ("#1e90ff", "Dodger Blue", "ffffff"),
        ("#0000ff", "Blue", "ffffff"),
        ("#00008b", "Dark Blue", "ffffff"),
        ("#4b0082", "Indigo", "ffffff"),
        ("#8a2be2", "Blue Violet", "ffffff"),
        ("#9400d3", "Dark Violet", "ffffff"),
        ("#ff00ff", "Magenta / Fuchsia", "000000"),
        ("#da70d6", "Orchid", "000000"),
        ("#ee82ee", "Violet", "000000"),
        ("#ffc0cb", "Pink", "000000"),
        ("#deb887", "Burlywood", "000000"),
        ("#d2691e", "Chocolate", "ffffff"),
        ("#8b4513", "Saddle Brown", "ffffff"),
        ("#a0522d", "Sienna", "ffffff"),
        ("#cd853f", "Peru", "000000"),
        ("#f4a460", "Sandy Brown", "000000"),
        ("#d2b48c", "Tan", "000000"),
        ("#808080", "Gray", "ffffff"),
        ("#a9a9a9", "Dark Gray", "000000"),
        ("#c0c0c0", "Silver", "000000"),
        ("#d3d3d3", "Light Gray", "000000"),
        ("#f5f5f5", "White Smoke", "000000"),
        ("#ffe4e1", "Misty Rose", "000000"),
        ("#fff0f5", "Lavender Blush", "000000"),
        ("#faf0e6", "Linen", "000000"),
        ("#f0e68c", "Khaki", "000000"),
        ("#fffff0", "Ivory", "000000"),
        ("#f08080", "Light Coral", "000000"),
        ("#e9967a", "Dark Salmon", "000000"),
    ]

    color_variants = [{"id": hex_code, "title": name, "iconUrl": colorUrl(hex_code, fg)} for hex_code, name, fg in color_variants_raw]

    color_selector = currentTheme_card.create_ui_element(UI.Select, label="Select color", items=color_variants, mode="single", full_width=True, selected_items=["#1e90ff"], margin="mt-2")
    # themeBuilder_card.create_ui_element(UI.Text, content="Add variants", size="xl", weight="bold")
    

    
    variant_selector = themeBuilder_card.create_ui_element(UI.Select, label="Select variant", items=v2_variants, mode="single", onChange=onSelectedVariant, full_width=True)
    
    text_group = themeBuilder_card.create_group(type="columns", gap=2, full_width=True)
    value1_variant = text_group.create_ui_element(UI.Input, label="Value 1", show_clear_button=True, visible=False, full_width=True)
    value2_variant = themeBuilder_card.create_ui_element(UI.Input, label="Value 2", show_clear_button=True, visible=False, full_width=True)
    separator_variant = themeBuilder_card.create_ui_element(UI.Select, label="Separator type", items=[{"id": "small", "title": "Small"}, {"id": "large", "title": "Large"}], mode="single", visible=False, full_width=True)
    content_display_variant = text_group.create_ui_element(UI.Toggle, label="Content Display", visible=False)

    add_variant_btn = themeBuilder_card.create_ui_element(UI.Button, label="Add Variant", variant="cta", visible=False, full_width=True, onClick=AddVariant)



    displayBuild_card = right_container.create_card(height="full", width="full", gap=2)

    display_variants_table = displayBuild_card.create_ui_element(UI.Table, selectable=False, search=False, items_per_page=8, columns=[
            { "type": "tag", "label": "Variant" },
            { "type": "text", "label": "Value" },
            { "type": "text", "label": " " },
            { "type": "button", "label": " ", "buttons": [
                { "label": "Move up", "color": "default", "onClick": moveUpVariant },
                { "label": "Move down", "color": "default", "onClick": moveDownVariant },
                { "label": "Delete", "color": "danger", "onClick": deleteVariant },
            ] },
        ],
        rows=[],
    )
    build_theme_btn = displayBuild_card.create_ui_element(UI.Button, label="Build Theme", variant="cta", visible=False, full_width=True, onClick=buildTheme)


    theme_data = getThemeData(theme_name=current_theme.selected_items[0])
    if theme_data.get("v2"):
        display_variants_table.rows = []
        for layout_item in theme_data["v2"]["layout"]:
            if "section" in layout_item:
                section_data = layout_item["section"]
                insertVariantRow("section", section_data["text"], section_data["thumbnail"], extras={})
            else:
                for layout_k, layout_v in layout_item.items():
                    insertVariantRow(layout_k, layout_v, " ", extras={})
        build_theme_btn.visible = True
        color_selector.selected_items = [theme_data["v2"]["color"]]
    else:
        display_variants_table.rows = []
        build_theme_btn.visible = False


    themesV2_tab.render()


customThemesV2Builder()
