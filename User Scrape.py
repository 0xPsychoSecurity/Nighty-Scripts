@nightyScript(
    name="User Scraper",
    author="Syn",
    description="Scrapes all user IDs from a guild and posts them in a txt file.",
    usage="<p>userscrape <guild_id> | <p>userscrape online <guild_id> | <p>userscrape all"
)
def user_scraper_script():

    import json
    from pathlib import Path

    BASE_DIR = Path(getScriptsPath()) / "json"
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    TXT_DIR = Path(getScriptsPath()) / "scrapes"
    TXT_DIR.mkdir(parents=True, exist_ok=True)

    @bot.command(name="userscrape")
    async def userscrape(ctx, *, args: str):
        await ctx.message.delete()

        args = args.strip()
        parts = args.split()

        if not parts:
            await ctx.send("Usage: <p>userscrape <guild_id> | <p>userscrape online <guild_id> | <p>userscrape all", delete_after=5)
            return

        # Handle scraping all guilds
        if len(parts) == 1 and parts[0].lower() == "all":
            mode = "all"
            guilds = bot.guilds

            if not guilds:
                await ctx.send("No guilds found or accessible.", delete_after=5)
                return

            msg = await ctx.send("Scraping members from all guilds...")

            success_count = 0
            skipped_guilds = []

            for guild in guilds:
                try:
                    # Skip guilds where the bot cannot view any channels (avoids "No channels viewable" errors)
                    if not getattr(guild, "text_channels", None):
                        skipped_guilds.append(guild.name)
                        continue

                    if not any(ch.permissions_for(guild.me).view_channel for ch in guild.text_channels):
                        skipped_guilds.append(guild.name)
                        continue

                    user_ids = []

                    # Try to fetch all members (including uncached); fall back to cached members
                    try:
                        members = await guild.fetch_members()
                    except Exception:
                        members = guild.members

                    for member in members:
                        if getattr(member, "bot", False):
                            continue
                        user_ids.append(f"<@{member.id}>")

                    txt_file_path = TXT_DIR / f"{guild.id}_users.txt"
                    with open(txt_file_path, "w", encoding="utf-8") as f:
                        f.write("\n".join(user_ids))

                    await ctx.send(f"Scraped {len(user_ids)} users from **{guild.name}**.", files=[discord.File(txt_file_path)])
                    success_count += 1

                except Exception as e:
                    print(f"Error scraping users for guild {guild.id} ({guild.name}): {e}", type_="ERROR")
                    skipped_guilds.append(guild.name)
                    continue

            await msg.delete()

            # Send a short summary message
            summary = f"Finished scraping all guilds. Successful: {success_count}. Skipped: {len(skipped_guilds)}."
            if skipped_guilds:
                # Only show first few to avoid spam if there are many
                preview = ", ".join(skipped_guilds[:5])
                if len(skipped_guilds) > 5:
                    preview += ", ..."
                summary += f" Skipped guilds (no access or error): {preview}."

            await ctx.send(summary, delete_after=15)

            return

        mode = "all"
        if parts[0].lower() == "online":
            mode = "online"
            if len(parts) < 2:
                await ctx.send("Please provide a guild ID.", delete_after=5)
                return
            guild_id = parts[1]
        else:
            guild_id = parts[0]

        guild_id = guild_id.strip()
        if not guild_id.isdigit():
            await ctx.send("Invalid guild ID.", delete_after=5)
            return

        guild_id_int = int(guild_id)
        guild = bot.get_guild(guild_id_int)
        if not guild:
            await ctx.send("Guild not found or inaccessible.", delete_after=5)
            return

        if mode == "online":
            msg = await ctx.send(f"Scraping **online** members from **{guild.name}**...")
        else:
            msg = await ctx.send(f"Scraping members from **{guild.name}**...")

        user_ids = []
        try:
            # Try to fetch all members (including uncached); fall back to cached members
            try:
                members = await guild.fetch_members()
            except Exception:
                members = guild.members

            # Loop through all members
            for member in members:
                if getattr(member, "bot", False):
                    continue
                if mode == "online" and getattr(member, "status", None) != discord.Status.online:
                    continue
                user_ids.append(f"<@{member.id}>")

            # Save to TXT file
            suffix = "online_users" if mode == "online" else "users"
            txt_file_path = TXT_DIR / f"{guild_id}_{suffix}.txt"
            with open(txt_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(user_ids))

            # Send file in channel
            if mode == "online":
                await ctx.send(f"Scraped {len(user_ids)} online users.", files=[discord.File(txt_file_path)])
            else:
                await ctx.send(f"Scraped {len(user_ids)} users.", files=[discord.File(txt_file_path)])

        except Exception as e:
            print(f"Error scraping users: {e}", type_="ERROR")
            await ctx.send(f"Failed to scrape users: {e}")

        finally:
            await msg.delete()

    @bot.command(name="userscrapetag")
    async def userscrapetag(ctx, *, args: str):
        await ctx.message.delete()

        args = args.strip()
        parts = args.split(maxsplit=1)

        if len(parts) < 2:
            await ctx.send("Usage: <p>userscrapetag <guild_id> <tag_text>", delete_after=5)
            return

        guild_id = parts[0].strip()
        tag_text = parts[1].strip()

        if not guild_id.isdigit():
            await ctx.send("Invalid guild ID.", delete_after=5)
            return

        if not tag_text:
            await ctx.send("Please provide tag text to search for.", delete_after=5)
            return

        guild_id_int = int(guild_id)
        guild = bot.get_guild(guild_id_int)
        if not guild:
            await ctx.send("Guild not found or inaccessible.", delete_after=5)
            return

        msg = await ctx.send(f"Searching for users in **{guild.name}** matching `{tag_text}`...")

        try:
            try:
                members = await guild.fetch_members()
            except Exception:
                members = guild.members

            tag_lower = tag_text.lower()
            results = []

            for member in members:
                if getattr(member, "bot", False):
                    continue

                primary_guild = (
                    getattr(member, "primary_guild", None)
                    or getattr(member, "primaryGuild", None)
                    or getattr(getattr(member, "user", None) or object(), "primary_guild", None)
                    or getattr(getattr(member, "user", None) or object(), "primaryGuild", None)
                )

                if primary_guild is None:
                    continue

                if isinstance(primary_guild, dict):
                    tag_value = primary_guild.get("tag")
                    identity_guild_id = primary_guild.get("identityGuildId") or primary_guild.get("identity_guild_id")
                    identity_enabled = primary_guild.get("identityEnabled") or primary_guild.get("identity_enabled")
                else:
                    tag_value = getattr(primary_guild, "tag", None)
                    identity_guild_id = getattr(primary_guild, "identity_guild_id", None) or getattr(primary_guild, "identityGuildId", None)
                    identity_enabled = getattr(primary_guild, "identity_enabled", None) or getattr(primary_guild, "identityEnabled", None)

                if not tag_value:
                    continue

                if identity_enabled is False:
                    continue

                if identity_guild_id is not None and str(identity_guild_id) != str(guild_id_int):
                    continue

                if tag_lower not in str(tag_value).lower():
                    continue

                username_tag = f"{getattr(member, 'name', '')}#{getattr(member, 'discriminator', '')}"
                results.append(f"{username_tag} | {member.id} | <@{member.id}>")

            if not results:
                await msg.delete()
                await ctx.send(f"No users found in **{guild.name}** matching `{tag_text}`.", delete_after=10)
                return

            safe_tag = "".join(c for c in tag_text if c.isalnum() or c in ("-", "_"))
            if not safe_tag:
                safe_tag = "tag"

            txt_file_path = TXT_DIR / f"{guild_id}_users_{safe_tag}.txt"
            with open(txt_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(results))

            await msg.delete()
            await ctx.send(
                f"Found {len(results)} users in **{guild.name}** matching `{tag_text}`.",
                files=[discord.File(txt_file_path)]
            )

        except Exception as e:
            await msg.delete()
            print(f"Error searching users by tag: {e}", type_="ERROR")
            await ctx.send(f"Failed to search users by tag: {e}", delete_after=10)

user_scraper_script()