import json

# --- Script Definition (Unchanged) ---
@nightyScript(
    name="VirusTotal Scanner",
    author="Gemini PRO x IamN4m3l3ss",
    description="Scans files (up to 650MB) with VirusTotal. Works on messages you reply to and files uploaded in the same message as the command.",
    usage="<p>vtscan, <p>setvtkey"
)
def virusTotalScript():
    """Initializes the script's configuration."""
    if getConfigData().get("virustotal_api_key") is None:
        updateConfigData("virustotal_api_key", "")

# --- Bot Commands ---
@bot.command(name="setvtkey", description="Saves your VirusTotal API key.")
async def set_vt_key(ctx, *, api_key: str):
    await ctx.message.delete()
    updateConfigData("virustotal_api_key", api_key.strip())
    await ctx.send("✅ API key saved.", delete_after=10)

@bot.command(name="vtscan", description="Scans a file attachment using VirusTotal.")
async def scan_file(ctx, *, args: str = ""):
    """Performs the file scan with all logic and imports self-contained."""
    import aiohttp
    import asyncio
    import traceback

    # --- Configuration ---
    VT_API_URL = "https://www.virustotal.com/api/v3"
    MAX_FILE_SIZE = 650 * 1024 * 1024
    LARGE_FILE_THRESHOLD = 32 * 1024 * 1024
    POLL_TIMEOUT_SECONDS = 300
    POLL_INTERVAL_SECONDS = 10
    
    # --- Nested Helper Functions ---
    async def safe_edit(message, content):
        try: await message.edit(content=content)
        except Exception: pass

    async def upload_file_async(session, api_key, file_content, filename):
        form = aiohttp.FormData()
        form.add_field('file', file_content, filename=filename, content_type='application/octet-stream')
        headers = {"x-apikey": api_key}
        upload_url = f"{VT_API_URL}/files"

        if len(file_content) > LARGE_FILE_THRESHOLD:
            async with session.get(f"{VT_API_URL}/files/upload_url", headers=headers, timeout=30) as resp:
                resp.raise_for_status()
                upload_url = (await resp.json()).get("data")
                # --- FIX IS HERE ---
                # The line "headers = {}" was removed. The API key header is
                # required for the final upload POST request.

        async with session.post(upload_url, data=form, headers=headers, timeout=600) as resp:
            if resp.status == 409: return (await resp.json()).get("error", {}).get("code")
            resp.raise_for_status()
            return (await resp.json()).get("data", {}).get("id")

    async def get_report_async(session, api_key, analysis_id):
        endpoint = analysis_id if "files/" in analysis_id else f"analyses/{analysis_id}"
        url = f"{VT_API_URL}/{endpoint}"
        async with session.get(url, headers={'x-apikey': api_key}, timeout=30) as resp:
            return await resp.json() if resp.ok else None

    def format_report(attachment, report_data):
        attrs = report_data["data"].get("attributes", {})
        stats = attrs.get("last_analysis_stats") or attrs.get("stats", {})
        results = attrs.get("last_analysis_results") or attrs.get("results", {})
        file_hash = report_data.get("meta", {}).get("file_info", {}).get("sha256")
        positives = stats.get("malicious", 0) + stats.get("suspicious", 0)

        if positives > 0 and stats.get("malicious", 0) > 0: threat, emoji = "MALICIOUS", "⛔"
        elif positives > 0: threat, emoji = "SUSPICIOUS", "⚠️"
        else: threat, emoji = "CLEAN", "✅"

        detections = [f"{k.ljust(18)}: {v.get('result')}" for k, v in results.items() if v.get('category') in ["malicious", "suspicious"]]
        
        report = [
            "**VirusTotal Scan Report**",
            f"**`FILE INFORMATION`**\n```Name: {attachment.filename}\nSize: {attachment.size / 1024:.2f} KB```",
            f"**`SCAN SUMMARY`**\n```Result:     {positives} / {sum(stats.values())}\nStatus:     {emoji} {threat}\nMalicious:  {stats.get('malicious', 0)}\nSuspicious: {stats.get('suspicious', 0)}```"
        ]
        if detections:
            report.append(f"\n**`POSITIVE DETECTIONS`**\n```" + '\n'.join(detections[:8]) + "```")
            if len(detections) > 8: report.append(f"▫️ *...and {len(detections) - 8} more.*")
        if file_hash:
            report.append(f"\n**Full Report:** https://www.virustotal.com/gui/file/{file_hash}")
        return '\n'.join(report)

    # --- Main Command Logic ---
    await ctx.message.delete()
    api_key = getConfigData().get("virustotal_api_key")
    if not api_key:
        return await ctx.send("❌ **API key not set.** Use `<p>setvtkey`.", delete_after=15)

    attachment = next((a for a in ctx.message.attachments), None) or \
                 (ctx.message.reference and ctx.message.reference.resolved and next((a for a in ctx.message.reference.resolved.attachments), None))

    if not attachment:
        return await ctx.send("❌ **No file found.**", delete_after=15)
    if attachment.size > MAX_FILE_SIZE:
        return await ctx.send(f"⛔ **File too large.** Exceeds {MAX_FILE_SIZE // 1024 // 1024} MB.", delete_after=20)

    status_msg = await ctx.send(f"⏳ Preparing scan for `{attachment.filename}`...")
    try:
        async with aiohttp.ClientSession() as session:
            await safe_edit(status_msg, f"📥 Downloading `{attachment.filename}`...")
            async with session.get(attachment.url) as resp:
                if not resp.ok: return await safe_edit(status_msg, "⛔ **Error:** Failed to download.")
                file_content = await resp.read()

            upload_msg = "⏫ Uploading..." if len(file_content) > LARGE_FILE_THRESHOLD else "📤 Uploading..."
            await safe_edit(status_msg, upload_msg)
            analysis_id = await upload_file_async(session, api_key, file_content, attachment.filename)
            if not analysis_id: return await safe_edit(status_msg, "⛔ **Error:** Failed to upload.")

            report = None
            spinner = ['|', '/', '—', '\\']
            for i in range(POLL_TIMEOUT_SECONDS // POLL_INTERVAL_SECONDS):
                await safe_edit(status_msg, f"🔬 Querying VirusTotal... {spinner[i % 4]}")
                report_data = await get_report_async(session, api_key, analysis_id)
                if report_data and (report_data.get("data",{}).get("attributes",{}).get("status") == "completed" or report_data.get("data",{}).get("attributes",{}).get("last_analysis_stats")):
                    report = report_data
                    break
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
        
        await status_msg.delete()
        if report:
            await forwardEmbedMethod(channel_id=ctx.channel.id, content=format_report(attachment, report))
        else:
            await ctx.send("⌛ **Analysis timed out.** The report took longer than 5 minutes.", delete_after=20)

    except Exception:
        if status_msg: await safe_edit(status_msg, "An unexpected error occurred.")
        print(f"--- SCRIPT ERROR ---\n{traceback.format_exc()}", type_="ERROR")

# Register the script
virusTotalScript()
