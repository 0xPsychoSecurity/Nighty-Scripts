@nightyScript(
    name="Anti Drag",
    author="Wraith, edited by Syn",
    description="Drag's you back to your previous voice channel if you are dragged. (Doesn't work on servers that dont give the user permission to move members)", 
    usage="Enable/Disable Script"
)
def antiDrag():
    moving = False

    @bot.listen("on_voice_state_update")
    async def onDrag(member, before, after):
        nonlocal moving

        if member.id != bot.user.id:
            return

        # Check permissions first
        if not member.guild.me.guild_permissions.move_members:
            print("You dont have permission to drag yourself.", type_="ERROR")
            return

        # Log voice channel to temporary file for this server
        if before.channel:
            try:
                import os
                import json
                
                # Create temp directory if it doesn't exist
                temp_dir = os.path.join(os.path.dirname(__file__), "temp")
                os.makedirs(temp_dir, exist_ok=True)
                
                # Server-specific file
                server_file = os.path.join(temp_dir, f"voice_channel_{member.guild.id}.json")
                
                # Save channel info
                channel_data = {
                    "channel_id": before.channel.id,
                    "channel_name": before.channel.name,
                    "server_id": member.guild.id,
                    "server_name": member.guild.name
                }
                
                with open(server_file, 'w') as f:
                    json.dump(channel_data, f, indent=2)
                    
                print(f"Logged voice channel {before.channel.name} for server {member.guild.name}", type_="INFO")
                
            except Exception as e:
                print(f"Error logging channel: {e}", type_="ERROR")

        if before.channel and after.channel:
                if moving:
                    return

                try:
                    moving = True
                    print(f"You were dragged to {after.channel.name}, dragging back to {before.channel.name}.", type_="SUCCESS")
                    await member.move_to(before.channel)
                    await asyncio.sleep(0.5)
                    
                    # Delete the temporary file after successful reconnection
                    try:
                        import os
                        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
                        server_file = os.path.join(temp_dir, f"voice_channel_{member.guild.id}.json")
                        if os.path.exists(server_file):
                            os.remove(server_file)
                            print(f"Cleaned up temporary file for server {member.guild.name}", type_="INFO")
                    except Exception as cleanup_error:
                        print(f"Error cleaning up file: {cleanup_error}", type_="ERROR")
                    
                    moving = False
                except discord.HTTPException as er:
                    print(f"Error?: {er}", type_="ERROR")
antiDrag()