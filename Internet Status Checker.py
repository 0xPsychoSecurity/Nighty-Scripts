import platform
import subprocess
import asyncio
import re

@nightyScript(
    name="Internet Status Checker",
    author="poor69potato.funn",
    description="Checks the ping status of a website, domain, or IP address.",
    usage="!internetstatus <link | domain | IP>"
)
def internetstatus():
    @bot.command(
        usage="<website or IP>",
        description="Ping a link, domain, or IP to check if it's online."
    )
    async def internetstatus(ctx, *, target: str):
        # Remove protocol if present (http/https)
        cleaned = re.sub(r'^https?://', '', target.strip(), flags=re.IGNORECASE)

        # Only extract the domain/IP part (in case user adds /path)
        cleaned = cleaned.split('/')[0]

        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", cleaned]

        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                output = stdout.decode().strip()
                formatted = (
                    "━━━━━━━━━━━━━━━━━━━\n"
                    "🟢 __**Ping Successful!**__\n"
                    f"**Target:** `{cleaned}`\n"
                    "**Details:**\n"
                    "```txt\n"
                    f"{output}\n"
                    "```\n"
                    "━━━━━━━━━━━━━━━━━━━"
                )
                await ctx.send(formatted)
            else:
                await ctx.send(
                    "━━━━━━━━━━━━━━━━━━━\n"
                    "🔴 __**Ping Failed!**__\n"
                    f"**Target:** `{cleaned}`\n"
                    "**Error:** Could not reach the host.\n"
                    "━━━━━━━━━━━━━━━━━━━"
                )

        except Exception as e:
            await ctx.send(
                "━━━━━━━━━━━━━━━━━━━\n"
                "⚠️ __**Error Occurred!**__\n"
                f"**Target:** `{cleaned}`\n"
                f"**Reason:** `{str(e)}`\n"
                "━━━━━━━━━━━━━━━━━━━"
            )

internetstatus()
