@nightyScript(
    name="Friend Manager Pro",
    author="X",
    description="Manage your Discord friends with bulk operations and whitelist protection",
    usage="Mass unfriend with safety features and friend list management"
)
def unfriendAllUISafeWithWhitelist():
    whitelist = [1234567890, 9876543210]
    selected_rows = []

    tab = Tab(name="Friend Manager Pro", icon="users")
    main = tab.create_container(type="columns", gap=6)
    
    # Controls
    left = main.create_container(type="rows", gap=6)
    ctrl = left.create_card(type="rows", gap=6)

    ctrl.create_ui_element(UI.Text, content="Friend Manager", size="xl", weight="bold")
    ctrl.create_ui_element(UI.Text, content="Manage friends with whitelist protection", size="sm", color="#A0AEC0")

    refresh_btn = ctrl.create_ui_element(UI.Button, label="Refresh", variant="bordered", color="primary", size="sm")

    def get_options(skip_whitelist=True):
        opts = []
        for f in bot.friends:
            if skip_whitelist and f.id in whitelist:
                continue
            user = getattr(f.user, "name", "Unknown")
            disp = getattr(f.user, "display_name", user)
            disc = getattr(f.user, "discriminator", "0000")
            av = getattr(f.user.display_avatar, "url", "")
            name = f"{disp} (@{user}#{disc})" if disp != user else f"{user}#{disc}"
            opts.append({"id": str(f.id), "title": name, "iconUrl": av})
        return opts

    def get_rows():
        rows = []
        for f in bot.friends:
            user = getattr(f.user, "name", "Unknown")
            disp = getattr(f.user, "display_name", user)
            disc = getattr(f.user, "discriminator", "0000")
            av = getattr(f.user.display_avatar, "url", "")
            protected = f.id in whitelist
            rows.append({
                "id": str(f.id),
                "cells": [
                    {"text": disp, "subtext": f"@{user}#{disc}", "imageUrl": av},
                    {"text": "Protected" if protected else "Unprotected", "color": "green" if protected else "gray"},
                    {}
                ]
            })
        return rows

    friend_sel = ctrl.create_ui_element(UI.Select, label="Friends to Remove", items=get_options(True), 
                                        mode="multiple", description="Pick who to unfriend", full_width=True)

    wl_sel = ctrl.create_ui_element(UI.Select, label="Whitelist", items=get_options(False), mode="multiple",
                                    description="Protected from removal", full_width=True, 
                                    selected_items=[str(x) for x in whitelist])

    confirm = ctrl.create_ui_element(UI.Toggle, label="Confirm: unfriend all non-whitelisted", checked=False)

    btns = ctrl.create_group(type="columns", gap=3)
    unfriend_sel = btns.create_ui_element(UI.Button, label="Remove Selected", variant="solid", 
                                          color="danger", full_width=True)
    unfriend_all = btns.create_ui_element(UI.Button, label="Remove All", variant="solid", 
                                          color="primary", full_width=True, disabled=True)

    status = ctrl.create_ui_element(UI.Text, content="Ready", size="sm", color="#718096")

    ctrl.create_ui_element(UI.Text, content="Stats", size="lg", weight="bold", margin="mt-4")
    stats = ctrl.create_group(type="columns", gap=4)
    total_txt = stats.create_ui_element(UI.Text, content=f"Total: {len(bot.friends)}", size="sm", weight="medium")
    wl_txt = stats.create_ui_element(UI.Text, content=f"Protected: {len(whitelist)}", size="sm", 
                                     weight="medium", color="#48BB78")
    unwl_txt = stats.create_ui_element(UI.Text, content=f"Unprotected: {len(bot.friends) - len(whitelist)}", 
                                       size="sm", weight="medium", color="#F56565")

    # Table
    right = main.create_container(type="rows", gap=6)
    tbl_card = right.create_card(type="rows", gap=4)

    tbl_card.create_ui_element(UI.Text, content="All Friends", size="xl", weight="bold")
    tbl_card.create_ui_element(UI.Text, content="Select friends for bulk actions", size="sm", color="#A0AEC0")

    bulk_btns = tbl_card.create_group(type="columns", gap=3)
    wl_bulk = bulk_btns.create_ui_element(UI.Button, label="Whitelist", variant="bordered", 
                                          color="success", size="sm", disabled=True)
    rm_bulk = bulk_btns.create_ui_element(UI.Button, label="Remove", variant="bordered", 
                                          color="danger", size="sm", disabled=True)
    unwl_bulk = bulk_btns.create_ui_element(UI.Button, label="Unwhitelist", variant="bordered", 
                                            color="default", size="sm", disabled=True)
    
    sel_txt = tbl_card.create_ui_element(UI.Text, content="Nothing selected", size="sm", color="#718096")

    def update_stats():
        total_txt.content = f"Total: {len(bot.friends)}"
        wl_txt.content = f"Protected: {len(whitelist)}"
        unwl_txt.content = f"Unprotected: {len(bot.friends) - len(whitelist)}"

    def refresh_ui():
        friend_sel.items = get_options(True)
        wl_sel.items = get_options(False)
        wl_sel.selected_items = [str(x) for x in whitelist]
        tbl.rows = get_rows()
        update_stats()

    def on_tbl_sel(ids):
        nonlocal selected_rows
        selected_rows = ids
        if not ids:
            sel_txt.content = "Nothing selected"
            sel_txt.color = "#718096"
            wl_bulk.disabled = rm_bulk.disabled = unwl_bulk.disabled = True
        else:
            sel_txt.content = f"{len(ids)} selected"
            sel_txt.color = "#3182CE"
            wl_bulk.disabled = rm_bulk.disabled = unwl_bulk.disabled = False

    async def wl_bulk_click():
        if not selected_rows:
            return
        wl_bulk.loading = True
        cnt = 0
        for fid in selected_rows:
            fid_int = int(fid)
            if fid_int not in whitelist:
                whitelist.append(fid_int)
                cnt += 1
        refresh_ui()
        tbl.selected_rows = []
        wl_bulk.loading = False
        tab.toast(title="Done", description=f"Whitelisted {cnt}", type="SUCCESS")

    async def unwl_bulk_click():
        nonlocal whitelist
        if not selected_rows:
            return
        unwl_bulk.loading = True
        cnt = 0
        for fid in selected_rows:
            fid_int = int(fid)
            if fid_int in whitelist:
                whitelist.remove(fid_int)
                cnt += 1
        refresh_ui()
        tbl.selected_rows = []
        unwl_bulk.loading = False
        tab.toast(title="Done", description=f"Removed {cnt} from whitelist", type="SUCCESS")

    async def rm_bulk_click():
        if not selected_rows:
            return
        rm_bulk.loading = True
        sel_txt.content = f"Removing {len(selected_rows)}..."
        sel_txt.color = "#3182CE"
        ok = fail = skip = 0
        for fid in selected_rows:
            fid_int = int(fid)
            if fid_int in whitelist:
                skip += 1
                continue
            try:
                f = next((x for x in bot.friends if x.id == fid_int), None)
                if f:
                    await f.user.remove_friend()
                    ok += 1
            except:
                fail += 1
        refresh_ui()
        tbl.selected_rows = []
        rm_bulk.loading = False
        msg = f"Removed {ok}"
        if skip:
            msg += f", skipped {skip}"
        if fail:
            msg += f", {fail} failed"
        tab.toast(title="Done" if not fail else "Partial", description=msg, 
                 type="SUCCESS" if not fail else "ERROR")

    wl_bulk.onClick = wl_bulk_click
    unwl_bulk.onClick = unwl_bulk_click
    rm_bulk.onClick = rm_bulk_click

    tbl = tbl_card.create_ui_element(UI.Table,
                                    columns=[
                                        {"type": "text", "label": "Friend"},
                                        {"type": "tag", "label": "Status"},
                                        {"type": "button", "label": "Actions", "buttons": [
                                            {"label": "Whitelist", "color": "default", "onClick": lambda: None},
                                            {"label": "Remove", "color": "danger", "onClick": lambda: None}
                                        ]}
                                    ],
                                    rows=get_rows(),
                                    search=True,
                                    items_per_page=25,
                                    selectable=True)
    
    tbl.onSelectionChange = on_tbl_sel

    async def refresh_click():
        refresh_btn.loading = True
        status.content = "Refreshing..."
        status.color = "#3182CE"
        try:
            refresh_ui()
            status.content = f"Refreshed - {len(bot.friends)} friends"
            status.color = "#38A169"
            tab.toast(title="Refreshed", description="List updated", type="SUCCESS")
        except Exception as e:
            status.content = f"Failed: {str(e)}"
            status.color = "#E53E3E"
            tab.toast(title="Error", description="Refresh failed", type="ERROR")
        refresh_btn.loading = False

    refresh_btn.onClick = refresh_click

    def wl_change(ids):
        nonlocal whitelist
        whitelist = [int(x) for x in ids]
        refresh_ui()

    wl_sel.onChange = wl_change

    def confirm_change(checked):
        unfriend_all.disabled = not checked

    confirm.onChange = confirm_change

    async def unfriend_sel_click():
        ids = friend_sel.selected_items
        if not ids:
            status.content = "Nothing selected"
            status.color = "#E53E3E"
            return
        unfriend_sel.loading = True
        status.content = f"Processing {len(ids)}..."
        status.color = "#3182CE"
        ok = fail = 0
        errs = []
        for fid in ids:
            try:
                f = next((x for x in bot.friends if str(x.id) == fid), None)
                if f and f.id not in whitelist:
                    await f.user.remove_friend()
                    ok += 1
            except Exception as e:
                fail += 1
                errs.append(str(e))
        unfriend_sel.loading = False
        refresh_ui()
        if fail and not ok:
            status.content = f"All failed: {errs[0] if errs else 'unknown'}"
            status.color = "#E53E3E"
            tab.toast(title="Failed", description="Couldn't remove any", type="ERROR")
        else:
            status.content = f"Done: {ok} removed, {fail} failed"
            status.color = "#38A169" if not fail else "#E53E3E"
            tab.toast(title="Done", description=f"Removed {ok}", type="SUCCESS")

    async def unfriend_all_click():
        targets = [f for f in bot.friends if f.id not in whitelist]
        if not targets:
            status.content = "Nobody to remove"
            status.color = "#38A169"
            return
        unfriend_all.loading = True
        status.content = f"Removing {len(targets)}..."
        status.color = "#3182CE"
        ok = fail = 0
        errs = []
        for f in targets:
            try:
                await f.user.remove_friend()
                ok += 1
            except Exception as e:
                fail += 1
                errs.append(str(e))
        unfriend_all.loading = False
        refresh_ui()
        if fail and not ok:
            status.content = f"All failed: {errs[0] if errs else 'unknown'}"
            status.color = "#E53E3E"
            tab.toast(title="Failed", description="Couldn't remove any", type="ERROR")
        else:
            status.content = f"Done: {ok} removed, {fail} failed"
            status.color = "#38A169" if not fail else "#E53E3E"
            tab.toast(title="Done", description=f"Removed {ok}", type="SUCCESS")
        friend_sel.selected_items = []
        confirm.checked = False
        unfriend_all.disabled = True

    unfriend_sel.onClick = unfriend_sel_click
    unfriend_all.onClick = unfriend_all_click

    update_stats()
    tab.render()

unfriendAllUISafeWithWhitelist()