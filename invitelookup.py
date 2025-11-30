import discord
import requests
import json

@nightyScript(
   name="Advanced Invite Lookup",
   author="windowsed",
   description="Fetches comprehensive Discord server invite information with detailed analysis including boost data",
   usage="!invlook <invite_code>"
)
def advancedInviteLookupScript():
   """
   ADVANCED INVITE LOOKUP
   ----------------------
   Fetches comprehensive Discord server invite information using Discord's public API
   with detailed server analytics, invite metadata, and boost information
   
   COMMANDS:
   !invlook <invite_code> - Returns detailed information about the Discord server invite
   
   EXAMPLES:
   !invlook discord.gg/example - Analyzes the invite and returns server details
   !invlook dQw4w9WgXcQ - Looks up invite using just the code
   
   NOTES:
   - Requires manage_messages permission to delete command messages
   - Invite must be valid and publicly accessible
   - Returns comprehensive server statistics and invite metadata
   - Includes Discord Nitro boost information and level
   - Handles various invite URL formats automatically
   """
   @bot.command(
       name="invlook",
       description="Fetches comprehensive Discord server invite information",
       usage="!invlook <invite_code>"
   )
   async def inviteLookupHandler(ctx, *, invite: str):
       try:
           await ctx.message.delete()
           
           # Extract invite code from various URL formats
           invite_code = invite.replace("https://", "").replace("http://", "")
           invite_code = invite_code.replace("discord.gg/", "").replace("discord.com/invite/", "")
           invite_code = invite_code.split("/")[-1].split("?")[0]
           
           # Discord API endpoint with comprehensive data flags
           api_url = f"https://discord.com/api/v10/invites/{invite_code}"
           params = {
               "with_counts": "true",
               "with_expiration": "true"
           }
           
           headers = {
               "User-Agent": "DiscordBot (Advanced Invite Lookup, 1.0)"
           }
           
           response = requests.get(api_url, params=params, headers=headers, timeout=10)
           
           if response.status_code == 200:
               data = response.json()
               
               # Extract server information
               guild_data = data.get("guild", {})
               inviter_data = data.get("inviter", {})
               channel_data = data.get("channel", {})
               
               # Build comprehensive server information
               server_name = guild_data.get("name", "Unknown Server")
               server_id = guild_data.get("id", "N/A")
               server_description = guild_data.get("description", "No description available")
               server_icon = guild_data.get("icon")
               server_banner = guild_data.get("banner")
               server_splash = guild_data.get("splash")
               verification_level = guild_data.get("verification_level", 0)
               nsfw_level = guild_data.get("nsfw_level", 0)
               server_features = guild_data.get("features", [])
               
               # BOOST INFORMATION - NEW ADDITIONS
               premium_subscription_count = guild_data.get("premium_subscription_count", 0)
               premium_tier = guild_data.get("premium_tier", 0)
               
               # Inviter information
               inviter_username = inviter_data.get("username", "Unknown")
               inviter_discriminator = inviter_data.get("discriminator", "0000")
               inviter_id = inviter_data.get("id", "N/A")
               inviter_avatar = inviter_data.get("avatar")
               
               # Channel information
               channel_name = channel_data.get("name", "Unknown Channel")
               channel_id = channel_data.get("id", "N/A")
               channel_type = channel_data.get("type", 0)
               
               # Member counts and statistics
               online_members = data.get("approximate_presence_count", 0)
               total_members = data.get("approximate_member_count", 0)
               
               # Invite metadata
               invite_code_clean = data.get("code", invite_code)
               invite_uses = data.get("uses", "N/A")
               invite_max_uses = data.get("max_uses", "N/A")
               invite_max_age = data.get("max_age", "N/A")
               invite_temporary = data.get("temporary", False)
               invite_created_at = data.get("created_at", "N/A")
               invite_expires_at = data.get("expires_at", "Never")
               
               # Verification level mapping
               verification_levels = {
                   0: "None",
                   1: "Low - Verified email",
                   2: "Medium - Registered for 5+ minutes",
                   3: "High - Member for 10+ minutes",
                   4: "Very High - Verified phone number"
               }
               
               # NSFW level mapping
               nsfw_levels = {
                   0: "Default",
                   1: "Explicit",
                   2: "Safe",
                   3: "Age Restricted"
               }
               
               # Channel type mapping
               channel_types = {
                   0: "Text Channel",
                   1: "DM",
                   2: "Voice Channel",
                   3: "Group DM",
                   4: "Category",
                   5: "News Channel",
                   10: "News Thread",
                   11: "Public Thread",
                   12: "Private Thread",
                   13: "Stage Channel",
                   14: "Directory",
                   15: "Forum"
               }
               
               # BOOST LEVEL MAPPING AND CALCULATIONS - NEW ADDITIONS
               boost_level_names = {
                   0: "No Level",
                   1: "Level 1",
                   2: "Level 2", 
                   3: "Level 3"
               }
               
               # Calculate boost level requirements and progress
               boost_requirements = {
                   1: 2,   # Level 1 requires 2 boosts
                   2: 7,   # Level 2 requires 7 boosts  
                   3: 14   # Level 3 requires 14 boosts
               }
               
               # Determine next level progress
               next_level = premium_tier + 1 if premium_tier < 3 else None
               boosts_needed_for_next = 0
               boost_progress_text = ""
               
               if next_level and next_level in boost_requirements:
                   boosts_needed_for_next = boost_requirements[next_level] - premium_subscription_count
                   if boosts_needed_for_next > 0:
                       boost_progress_text = f" ({boosts_needed_for_next} more needed for {boost_level_names[next_level]})"
                   else:
                       boost_progress_text = f" (Eligible for {boost_level_names[next_level]})"
               elif premium_tier == 3:
                   boost_progress_text = " (Maximum level reached)"
               
               # Generate boost emoji based on level
               boost_emoji = {
                   0: "🔹",
                   1: "✨", 
                   2: "💎",
                   3: "👑"
               }.get(premium_tier, "🔹")
               
               # Calculate activity ratio
               activity_ratio = (online_members / total_members * 100) if total_members > 0 else 0
               
               # Build inviter display name
               inviter_display = f"{inviter_username}#{inviter_discriminator}" if inviter_discriminator != "0" else inviter_username
               
               # Build server icon URL
               server_icon_url = None
               if server_icon:
                   server_icon_url = f"https://cdn.discordapp.com/icons/{server_id}/{server_icon}.png?size=256"
               
               # Process server features for raw display
               features_text = ""
               if server_features:
                   features_text = ", ".join(server_features)
               else:
                   features_text = "No special features enabled"
               
               # Build comprehensive message content
               message_content = f"""# 📋 Server Invite Analysis

**{server_name}**
*{server_description}*

## 🏢 Server Details
- **Server ID:** `{server_id}`
- **Verification Level:** {verification_levels.get(verification_level, 'Unknown')}
- **NSFW Level:** {nsfw_levels.get(nsfw_level, 'Unknown')}

## 👥 Member Statistics
- **Total Members:** {total_members:,}
- **Online Members:** {online_members:,}
- **Activity Ratio:** {activity_ratio:.1f}%

## {boost_emoji} Boost Information
- **Boost Count:** {premium_subscription_count} boosts
- **Boost Level:** {boost_level_names.get(premium_tier, 'Unknown')}{boost_progress_text}
- **Premium Tier:** {premium_tier}/3"""

               # Add boost perks information based on level
               if premium_tier >= 1:
                   message_content += f"\n- **Level 1 Perks:** Enhanced audio quality, custom server invite background, animated server icon"
               if premium_tier >= 2:
                   message_content += f"\n- **Level 2 Perks:** 150 emoji slots, 1080p 60fps streams, custom server banner, 50MB upload limit"
               if premium_tier >= 3:
                   message_content += f"\n- **Level 3 Perks:** 250 emoji slots, custom server invite link, 100MB upload limit, animated banner"

               message_content += f"""

## 📺 Channel Information
- **Channel Name:** #{channel_name}
- **Channel ID:** `{channel_id}`
- **Channel Type:** {channel_types.get(channel_type, 'Unknown')}

## 👤 Invite Creator
- **Username:** {inviter_display}
- **User ID:** `{inviter_id}`

## 🔗 Invite Details
- **Invite Code:** `{invite_code_clean}`
- **Uses:** {invite_uses}/{invite_max_uses if invite_max_uses != 0 else '∞'}"""

               # Add expiration info if available
               if invite_expires_at != "Never":
                   message_content += f"\n- **Expires:** {invite_expires_at}"
               
               # Add temporary flag if applicable
               if invite_temporary:
                   message_content += f"\n- **Temporary Membership:** Yes"
               
               # Add server features section with raw features
               message_content += f"\n\n## ⭐ Server Features\n```\n{features_text}\n```"
               
               # Check for GUILD_TAGS feature and add profile tag if present
               if "GUILD_TAGS" in server_features:
                   profile_data = data.get("profile", {})
                   if profile_data:
                       profile_tag = profile_data.get("tag", "No tag available")
                       message_content += f"\n\n## 🏷️ Server Tag\n**Tag:** {profile_tag}"
               
               # Add server assets information
               assets = []
               if server_icon:
                   assets.append("Server Icon")
               if server_banner:
                   assets.append("Server Banner")
               if server_splash:
                   assets.append("Invite Splash")
               
               if assets:
                   message_content += f"\n\n## 🎨 Server Assets\n- " + "\n- ".join(assets)
                              
               message_content += f"\n\n> Invite analysis completed for `{invite_code_clean}`"
               
               await forwardEmbedMethod(
                   channel_id=ctx.channel.id,
                   content=message_content,
                   title=f"Discord Invite Analysis - {server_name}",
                   image=server_icon_url
               )
               
           elif response.status_code == 404:
               await forwardEmbedMethod(
                   channel_id=ctx.channel.id,
                   content=f"# ❌ Invite Not Found\n\nThe invite code `{invite_code}` could not be found or has expired.\n\n> Please verify the invite code and try again.",
                   title="Error: Invite Not Found"
               )
               
           elif response.status_code == 429:
               await forwardEmbedMethod(
                   channel_id=ctx.channel.id,
                   content="# ⏰ Rate Limited\n\nToo many requests have been made to Discord's API.\n\n> Please wait a moment before trying again.",
                   title="Rate Limit Exceeded"
               )
               
           else:
               await forwardEmbedMethod(
                   channel_id=ctx.channel.id,
                   content=f"# ⚠️ API Error\n\nDiscord API returned an unexpected status code: **{response.status_code}**\n\n> This may indicate a temporary issue with Discord's servers.",
                   title="API Error"
               )
               
       except requests.exceptions.Timeout:
           await forwardEmbedMethod(
               channel_id=ctx.channel.id,
               content="# ⏱️ Request Timeout\n\nThe request to Discord's API timed out.\n\n> This may be due to network connectivity issues. Please try again.",
               title="Request Timeout"
           )
           
       except requests.exceptions.RequestException as req_error:
           await forwardEmbedMethod(
               channel_id=ctx.channel.id,
               content=f"# 🌐 Network Error\n\nA network error occurred while trying to fetch invite information.\n\n**Error Details:**\n```\n{str(req_error)}\n```\n\n> Please check your internet connection and try again.",
               title="Network Error"
           )
           
       except discord.errors.Forbidden:
           await forwardEmbedMethod(
               channel_id=ctx.channel.id,
               content="# 🔒 Permission Error\n\nI don't have the required permissions to perform this action.\n\n**Required Permissions:**\n- Manage Messages (to delete command)\n- Send Messages\n- Embed Links\n\n> Please contact a server administrator to grant these permissions.",
               title="Insufficient Permissions"
           )
           
       except json.JSONDecodeError:
           await forwardEmbedMethod(
               channel_id=ctx.channel.id,
               content="# 📄 JSON Parse Error\n\nReceived invalid JSON response from Discord's API.\n\n> This may indicate a temporary issue with Discord's servers. Please try again later.",
               title="JSON Parse Error"
           )
           
       except KeyError as key_error:
           await forwardEmbedMethod(
               channel_id=ctx.channel.id,
               content=f"# 🔑 Data Parse Error\n\nMissing expected data field in API response.\n\n**Missing Field:** `{str(key_error)}`\n\n> The invite data may be incomplete or in an unexpected format.",
               title="Data Parse Error"
           )
           
       except Exception as general_error:
           await forwardEmbedMethod(
               channel_id=ctx.channel.id,
               content=f"# 💥 Unexpected Error\n\nAn unexpected error occurred while processing the invite lookup.\n\n**Error Details:**\n```\n{str(general_error)}\n```\n\n> Please report this error if it persists.",
               title="Unexpected Error"
           )

advancedInviteLookupScript()