# Thanks for downloading!
# UPDATE 1:
# Added Auto Update Startup:
# Script can now be kept on and will automatically
# update the startup for a new exe incase you update nighty

# shoutout to Luxed for the script, i just improved it. 

@nightyScript(
    name="[V2] Nighty Auto Start",
    author="Flixer",
    description="Make Nighty run automatically on Window's startup",
    usage="Script just needs to be on, it will also replace automatically any new version of nighty to the startup (you have to open the new exe for this)"
)
def add_to_startup():
    startup_folder = os.path.join(
        os.environ["APPDATA"],
        "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
    )
    bat_name = "Nighty_Startup.bat"
    bat_path = os.path.join(startup_folder, bat_name)
    nighty_exe_path = f'"{sys.executable}"'
    bat_content = f"@echo off\nstart \"\" {nighty_exe_path}\nexit\n"
    already_exists = os.path.exists(bat_path)

    with open(bat_path, "w") as bat_file:
        bat_file.write(bat_content)

    if already_exists:
        print("[!] Old Nighty Startup replaced with a new version.")
    else:
        print("[+] Nighty has been added to Windows startup.")

add_to_startup()
