@nightyScript(
    name="PC Info & Stats",
    author="LeoApple", 
    description="Commands .pcspecs and .pcstats to display hardware specs and live usage without external packages.",
    usage="<p>pcspecs | <p>pcstats [-r <seconds>]"
)
def pc_info_script():
    """
    PC INFO & STATS (NightyScript)
    ------------------------------
    Provides hardware specifications (.pcspecs) and live usage snapshot(s) (.pcstats).

    COMMANDS:
    <p>pcspecs               - Show CPU, RAM, GPU, OS, and disks overview
    <p>pcstats               - Show a single snapshot of CPU/RAM and (if available) GPU usage
    <p>pcstats -r <seconds>  - Post multiple snapshots over <seconds> (interval ~2s)
    <p>computerstats         - Send spoofed PC specs with an image link.
    NOTES:
    - GPU metrics require 'nvidia-smi' (NVIDIA). Without it, only GPU names are shown (if detectable).
    - Uses only Python standard library + Nighty built-ins.
    - Embeds are sent via forwardEmbedMethod; private mode is temporarily disabled per docs.
    """

    import asyncio
    import os
    import platform
    import re
    import shutil
    import subprocess
    from datetime import datetime

    # ---------- helpers ----------

    def _fmt_bytes(n: int) -> str:
        if n is None:
            return "N/A"
        step = 1024.0
        units = ["B","KB","MB","GB","TB","PB"]
        f = float(n)
        i = 0
        while f >= step and i < len(units)-1:
            f /= step
            i += 1
        return f"{f:.2f} {units[i]}"

    async def _run_shell(cmd: str):
        try:
            p = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            out, err = await p.communicate()
            return (p.returncode, out.decode(errors="ignore").strip(), err.decode(errors="ignore").strip())
        except Exception as e:
            return (1, "", str(e))

    async def _run_exec(*args: str):
        try:
            p = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            out, err = await p.communicate()
            return (p.returncode, out.decode(errors="ignore").strip(), err.decode(errors="ignore").strip())
        except Exception as e:
            return (1, "", str(e))

    def _is_windows(): return platform.system().lower().startswith("win")
    def _is_linux():   return platform.system().lower().startswith("lin")
    def _is_macos():   return platform.system().lower().startswith("darwin")

    # ---------- collectors: specs ----------

    async def get_cpu_name():
        if _is_windows():
            rc,out,err = await _run_shell('powershell -NoProfile -Command "(Get-CimInstance Win32_Processor).Name -join \', \'"')
            return out or platform.processor() or "Unknown CPU"
        if _is_linux():
            try:
                with open("/proc/cpuinfo","r",encoding="utf-8",errors="ignore") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":",1)[1].strip()
            except:
                pass
            rc,out,err = await _run_exec("lscpu")
            if out:
                m = re.search(r"Model name:\s+(.*)", out)
                if m: return m.group(1).strip()
            return platform.processor() or "Unknown CPU"
        if _is_macos():
            rc,out,err = await _run_exec("sysctl","-n","machdep.cpu.brand_string")
            return out or platform.processor() or "Unknown CPU"
        return platform.processor() or "Unknown CPU"

    async def get_total_ram_bytes():
        if _is_windows():
            rc,out,err = await _run_shell('powershell -NoProfile -Command "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"')
            try: return int(out.strip())
            except: return None
        if _is_linux():
            try:
                with open("/proc/meminfo","r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            return int(line.split()[1]) * 1024
            except:
                pass
            rc,out,err = await _run_exec("free","-b")
            if out:
                for line in out.splitlines():
                    if line.lower().startswith("mem:"):
                        parts = [p for p in line.split() if p.isdigit()]
                        if parts: return int(parts[0])
            return None
        if _is_macos():
            rc,out,err = await _run_exec("sysctl","-n","hw.memsize")
            try: return int(out.strip())
            except: return None
        return None

    async def get_gpus_list():
        if _is_windows():
            rc,out,err = await _run_shell('powershell -NoProfile -Command "(Get-CimInstance Win32_VideoController).Name -join \', \'"')
            if out: return [s.strip() for s in out.split(",") if s.strip()]
        if _is_linux():
            rc,out,err = await _run_exec("lspci")
            names=[]
            if out:
                for line in out.splitlines():
                    if "VGA compatible controller" in line or "3D controller" in line:
                        names.append(line.split(":",2)[-1].strip())
            if names: return names
        if _is_macos():
            rc,out,err = await _run_exec("system_profiler","SPDisplaysDataType")
            names=[]
            if out:
                for line in out.splitlines():
                    if "Chipset Model:" in line:
                        names.append(line.split(":",1)[1].strip())
            if names: return names
        # last resort: nvidia-smi
        rc,out,err = await _run_exec("nvidia-smi","--query-gpu=name","--format=csv,noheader")
        if rc==0 and out:
            return [s.strip() for s in out.splitlines() if s.strip()]
        return []

    async def get_disks():
        items=[]
        if _is_windows():
            for letter in [f"{chr(c)}:\\" for c in range(67, 91)]:  # C:\..Z:\
                if os.path.exists(letter):
                    try:
                        total, used, free = shutil.disk_usage(letter)
                        items.append((letter, total, free))
                    except:
                        pass
        else:
            mounts = set(["/"])
            try:
                with open("/proc/mounts","r") as f:
                    for line in f:
                        parts=line.split()
                        if len(parts)>=2 and parts[1].startswith("/"):
                            mounts.add(parts[1])
            except:
                pass
            for m in sorted(mounts):
                try:
                    total, used, free = shutil.disk_usage(m)
                    items.append((m, total, free))
                except:
                    pass
        return items

    # ---------- collectors: stats ----------

    async def get_cpu_usage_percent():
        if _is_windows():
            cmd = 'powershell -NoProfile -Command "(Get-CimInstance Win32_Processor).LoadPercentage | Measure -Average | Select -ExpandProperty Average"'
            rc,out,err = await _run_shell(cmd)
            try: return float(out.strip())
            except: return None
        if _is_linux():
            rc,out,err = await _run_exec("top","-bn1")
            if out:
                m = re.search(r"Cpu\(s\):\s*([\d.,]+)\s*us,\s*([\d.,]+)\s*sy,\s*([\d.,]+)\s*ni,\s*([\d.,]+)\s*id", out)
                if m:
                    idle = float(m.group(4).replace(",","."));  return max(0.0, 100.0 - idle)
            return None
        if _is_macos():
            rc,out,err = await _run_shell('top -l 1 | grep "CPU usage"')
            if out:
                m = re.search(r"CPU usage:\s*([\d.]+)% user,\s*([\d.]+)% sys,\s*([\d.]+)% idle", out)
                if m:
                    idle = float(m.group(3));  return max(0.0, 100.0 - idle)
            return None
        return None

    async def get_ram_usage():
        total = await get_total_ram_bytes()
        used = None
        if _is_windows():
            rc,out,err = await _run_shell('powershell -NoProfile -Command "(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty FreePhysicalMemory)"')
            try:
                free_kb = int(out.strip())
                if total is not None: used = total - (free_kb*1024)
            except: pass
        elif _is_linux():
            try:
                meminfo={}
                with open("/proc/meminfo","r") as f:
                    for line in f:
                        k,v = line.split(":",1); meminfo[k.strip()] = v.strip()
                def _kb(key): return int(meminfo.get(key,"0 kB").split()[0])
                if total:
                    free = (_kb("MemFree")+_kb("Buffers")+_kb("Cached"))*1024
                    used = total - free
            except: pass
        else:  # macOS
            rc_ps,psize,_ = await _run_exec("sysctl","-n","hw.pagesize")
            rc_vm,out,_ = await _run_exec("vm_stat")
            try:
                pagesize=int(psize.strip())
                stats={}
                for line in out.splitlines():
                    if ":" in line:
                        k,v = line.split(":",1)
                        v=int(v.strip().strip(".").replace(".",""))
                        stats[k.strip()] = v
                free_pages = stats.get("Pages free",0)+stats.get("Pages speculative",0)
                free = free_pages*pagesize
                if total: used = total - free
            except: pass
        return used, total

    async def get_gpu_stats_nvidia():
        rc,out,err = await _run_exec("nvidia-smi","--query-gpu=name,utilization.gpu,memory.used,memory.total","--format=csv,noheader,nounits")
        gpus=[]
        if rc==0 and out:
            for line in out.splitlines():
                parts=[p.strip() for p in line.split(",")]
                if len(parts)>=4:
                    name, util, mu, mt = parts[:4]
                    try:
                        gpus.append({
                            "name": name,
                            "util": float(util),
                            "mem_used": int(float(mu))*1024*1024,
                            "mem_total": int(float(mt))*1024*1024
                        })
                    except: pass
        return gpus

    # ---------- embed sender (per docs) ----------

    async def send_embed(ctx, title, content):
        # Temporarily disable private mode so embed can be sent, then restore.
        current_private = getConfigData().get("private")
        updateConfigData("private", False)
        try:
            await forwardEmbedMethod(
                channel_id=ctx.channel.id,
                title=title,
                content=content
            )
        finally:
            updateConfigData("private", current_private)

    # ---------- commands ----------

    @bot.command(
        name="pcspecs",
        aliases=["pcspec","specs"],
        usage="",
        description="Show CPU, RAM, GPU, OS, and disk overview."
    )
    async def pcspecs_cmd(ctx, *, args: str = ""):
        await ctx.message.delete()
        os_name = f"{platform.system()} {platform.release()} ({platform.version()})"
        cpu_name = await get_cpu_name()
        logical = os.cpu_count() or 0
        total_ram = await get_total_ram_bytes()
        gpus = await get_gpus_list()
        disks = await get_disks()

        lines = []
        lines.append("# PC Specifications")
        lines.append(f"**OS:** {os_name}")
        lines.append(f"**CPU:** {cpu_name}  \n**Threads:** {logical}")
        lines.append(f"**RAM:** {_fmt_bytes(total_ram) if total_ram else 'Unknown'}")
        lines.append("**GPU(s):** " + (", ".join(gpus) if gpus else "Unknown / not detected"))

        if disks:
            lines.append("\n## Disks")
            for mount,total,free in disks:
                used = total - free
                lines.append(f"- `{mount}`  Total: {_fmt_bytes(total)} | Used: {_fmt_bytes(used)} | Free: {_fmt_bytes(free)}")

        lines.append(f"\n_Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC_")
        await send_embed(ctx, "PC Specs", "\n".join(lines))
    @bot.command(
        name="computerstats",
        aliases=["computerstat"],
        usage="",
        description="Send fixed PC specs with an image link."
    )
    async def computerstats_cmd(ctx, *, args: str = ""):
        await ctx.message.delete()

        lines = [
            "PC Specs",
            "",
            "- **OS:** `Microsoft Windows 11 Pro`",
            "- **CPU:** `AMD Threadripper 3990X 2.9 GHz 64-Core`",
            "- **GPU:** `EVGA FTW3 ULTRA GAMING GeForce RTX 3090 Ti 24 GB, AMD Radeon Graphics (Integrated)`",
            "- **RAM:** `G.Skill Ripjaws V 64 GB (4 x 16 GB) DDR4-3200 (38.3GB usable) 3800 MHz`",
            "- **Storage:** `2TB NVMe SSD, Seagate Nytro Enterprise 16TB`",
        ]

        # send specs in the embed
        await send_embed(ctx, "PC Specs", "\n".join(lines))
    
    @bot.command(
        name="pcusage",
        aliases=["pcstats"],
        usage="[-r <seconds>]",
        description="Show current CPU/RAM and (if available) GPU usage. With -r, post multiple snapshots."
    )
    async def pcusage_cmd(ctx, *, args: str = ""):
        await ctx.message.delete()

        parts = (args or "").strip().split()
        run_seconds = 0
        if "-r" in parts:
            try:
                i = parts.index("-r")
                run_seconds = max(0, int(parts[i+1]))
            except:
                run_seconds = 0

        interval = 2
        end_time = (asyncio.get_event_loop().time() + run_seconds) if run_seconds > 0 else None
        snap = 1

        while True:
            cpu = await get_cpu_usage_percent()
            ram_used, ram_total = await get_ram_usage()

            gpu_lines=[]
            nvgpus = await get_gpu_stats_nvidia()
            if nvgpus:
                for g in nvgpus:
                    gpu_lines.append(f"- **{g['name']}**  Util: {g['util']:.0f}%  VRAM: {_fmt_bytes(g['mem_used'])}/{_fmt_bytes(g['mem_total'])}")
            else:
                names = await get_gpus_list()
                gpu_lines.append("- " + (", ".join(names) if names else "(No GPU metrics available)"))

            out = []
            out.append("# PC Live Stats")
            out.append(f"**CPU:** {cpu:.1f}% usage" if cpu is not None else "**CPU:** N/A")
            out.append(f"**RAM:** {_fmt_bytes(ram_used)} / {_fmt_bytes(ram_total)}" if (ram_used is not None and ram_total is not None) else "**RAM:** N/A")
            out.append("**GPU:**")
            out.extend(gpu_lines)
            out.append(f"\n_Snapshot #{snap} — {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC_")

            await send_embed(ctx, "PC Stats", "\n".join(out))

            if end_time is None or asyncio.get_event_loop().time() >= end_time:
                break
            snap += 1
            await asyncio.sleep(interval)

# required: register on load (per docs)
pc_info_script()
