import requests
from datetime import datetime

@nightyScript(
    name="Player Info Roblox",
    author="l5se & ChatGPT",
    description="gets some roblox user information | made with chatgpt",
    usage=".r <username|userid>"
)
def RobloxFullUserInfo():

    @bot.command()
    async def r(ctx, userinput=None):
        try:
            await ctx.message.delete()

            if not userinput:
                await ctx.send("Please provide a Roblox username or user ID. Usage: `.r <username|userid>`")
                return

            # Determine if input is user ID or username
            if userinput.isdigit():
                userid = userinput
                # Get username from user ID
                user_res = requests.get(f"https://users.roblox.com/v1/users/{userid}")
                if user_res.status_code != 200:
                    await ctx.send(f"User ID `{userid}` not found.")
                    return
                user_data = user_res.json()
                username = user_data.get("name", "Unknown")
            else:
                # Convert username to user ID
                lookup_url = "https://users.roblox.com/v1/usernames/users"
                payload = {"usernames": [userinput], "excludeBannedUsers": True}
                lookup_res = requests.post(lookup_url, json=payload)
                if lookup_res.status_code != 200:
                    await ctx.send(f"Failed to lookup username `{userinput}`.")
                    return
                lookup_data = lookup_res.json()
                if not lookup_data.get("data"):
                    await ctx.send(f"Username `{userinput}` not found.")
                    return
                userid = str(lookup_data["data"][0]["id"])
                username = userinput
                # Also get full user data here for created date and description
                user_res = requests.get(f"https://users.roblox.com/v1/users/{userid}")
                if user_res.status_code != 200:
                    await ctx.send(f"User ID `{userid}` not found.")
                    return
                user_data = user_res.json()

            # User data fallback if not fetched yet (for user ID case)
            if 'user_data' not in locals():
                user_res = requests.get(f"https://users.roblox.com/v1/users/{userid}")
                if user_res.status_code != 200:
                    await ctx.send(f"User ID `{userid}` not found.")
                    return
                user_data = user_res.json()

            created = user_data.get("created", "N/A")
            description = user_data.get("description")
            if not description or description.strip() == "":
                description = "This user has no description."

            # Format join date (try ISO parse, fallback raw)
            try:
                dt = datetime.fromisoformat(created.rstrip("Z"))
                created_fmt = dt.strftime("%B %d, %Y")
            except Exception:
                created_fmt = created

            # Favorite games
            fav_res = requests.get(
                f"https://games.roblox.com/v2/users/{userid}/favorite/games?accessFilter=2&limit=10&sortOrder=Desc"
            )
            favorite_games = []
            if fav_res.status_code == 200:
                fav_data = fav_res.json()
                if "data" in fav_data and len(fav_data["data"]) > 0:
                    for game in fav_data["data"]:
                        favorite_games.append(game.get("name", "Unknown"))
            fav_games_text = ", ".join(favorite_games) if favorite_games else "No favorite games found."

            # Created games
            created_games_res = requests.get(
                f"https://games.roblox.com/v2/users/{userid}/games?accessFilter=2&limit=10&sortOrder=Asc"
            )
            created_games = []
            if created_games_res.status_code == 200:
                created_games_data = created_games_res.json()
                if "data" in created_games_data and len(created_games_data["data"]) > 0:
                    for game in created_games_data["data"]:
                        game_name = game.get("name", "Unknown")
                        place_id = game.get("rootPlace", {}).get("id", "Unknown")
                        visits = game.get("placeVisits", 0)
                        created_games.append(f"{game_name} (Place ID: {place_id}) - {visits} visits")
            created_games_text = ", ".join(created_games) if created_games else "No created games found."

            # Inventory visibility
            inv_res = requests.get(f"https://inventory.roblox.com/v1/users/{userid}/can-view-inventory")
            if inv_res.status_code == 200:
                can_view = inv_res.json().get("canView", False)
                inventory_status = "🟩 Public" if can_view else "🟥 Private"
            else:
                inventory_status = "Unknown"

            # Body type (R6/R15)
            avatar_res = requests.get(f"https://avatar.roblox.com/v1/users/{userid}/avatar")
            if avatar_res.status_code == 200:
                avatar_data = avatar_res.json()
                body_type = avatar_data.get("playerAvatarType", "Unknown")
            else:
                body_type = "Unknown"

            # Thumbnail (420x420)
            thumb_res = requests.get(
                f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={userid}&size=420x420&format=Png&isCircular=false"
            )
            thumbnail_url = None
            if thumb_res.status_code == 200:
                thumb_data = thumb_res.json()
                if (
                    "data" in thumb_data
                    and len(thumb_data["data"]) > 0
                    and "imageUrl" in thumb_data["data"][0]
                ):
                    thumbnail_url = thumb_data["data"][0]["imageUrl"]

            # Construct the message
            msg = (
                f"**User:** {username} ({userid})\n"
                f"**Join Date:** {created_fmt}\n"
                f"**Description:** {description}\n"
                f"**Favorite Games:** {fav_games_text}\n"
                f"**Inventory:** {inventory_status}\n"
                f"**Created Games:** {created_games_text}\n"
                f"**Body Type:** {body_type}"
            )

            await ctx.send(msg)
            if thumbnail_url:
                await ctx.send(thumbnail_url)

        except Exception as e:
            await ctx.send(f"Error fetching user info: {e}")
            print(f"Error: {e}")

RobloxFullUserInfo()
