#!/usr/bin/env python3
"""
Nighty.exe Force Restart Script
Creates a batch file that records Nighty.exe's running location and restarts it independently.
Nighty Selfbot command only.
"""

import os
import subprocess
import psutil
import sys
import asyncio

# Nighty Selfbot command
@bot.command()
async def forcerestart(ctx):
    """Force restart Nighty.exe by creating and running a batch file."""
    
    def get_nighty_exe_path():
        """Get the exact path where Nighty.exe is currently running from."""
        import psutil
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name']
                    if proc_name and 'nighty.exe' in proc_name.lower():
                        # Try to get executable path
                        exe_path = proc.info['exe']
                        if exe_path:
                            return exe_path
                        else:
                            # Try to get the full executable path
                            try:
                                exe_path = proc.exe()
                                if exe_path:
                                    return exe_path
                            except Exception:
                                pass
                            
                            # If we can't get the path from the process, search for Nighty.exe
                            common_paths = [
                                os.path.join(os.getcwd(), "Nighty.exe"),
                                os.path.join(os.path.dirname(os.getcwd()), "Nighty.exe"),
                                r"C:\Nighty\Nighty.exe",
                                r"C:\Program Files\Nighty\Nighty.exe",
                                r"C:\Program Files (x86)\Nighty\Nighty.exe"
                            ]
                            
                            for path in common_paths:
                                if os.path.exists(path):
                                    return path
                            
                            return None
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            return None
        except Exception:
            return None
    
    def create_restart_batch(nighty_path):
        """Create a batch file that will restart Nighty.exe independently."""
        if not nighty_path:
            return False
        
        # Get directory and filename
        nighty_dir = os.path.dirname(nighty_path)
        nighty_exe = os.path.basename(nighty_path)
        
        # Create batch file in current directory
        batch_path = os.path.join(os.getcwd(), "restart_nighty.bat")
        
        try:
            with open(batch_path, 'w') as f:
                f.write('@echo off\n')
                f.write('title Nighty.exe Restart Process\n')
                f.write('mode con: cols=80 lines=30\n')
                f.write('echo ===================================================\n')
                f.write('echo Nighty.exe Independent Restart Process\n')
                f.write('echo ===================================================\n')
                f.write('echo.\n')
                f.write(f'echo Nighty.exe location: {nighty_path}\n')
                f.write(f'echo Nighty.exe directory: {nighty_dir}\n')
                f.write('echo.\n')
                f.write('echo Killing all Nighty processes...\n')
                f.write('taskkill /im nighty.one /f >nul 2>&1\n')
                f.write('taskkill /im Nighty.exe /f >nul 2>&1\n')
                f.write('echo Processes terminated.\n')
                f.write('echo.\n')
                f.write('echo Waiting 3 seconds for processes to fully terminate...\n')
                f.write('ping -n 3 -w 1000 127.0.0.1 >nul 2>&1\n')
                f.write('echo.\n')
                f.write(f'echo Changing to Nighty.exe directory: {nighty_dir}\n')
                f.write(f'cd /d "{nighty_dir}"\n')
                f.write(f'echo Current directory: %CD%\n')
                f.write('echo.\n')
                f.write('echo Starting Nighty.exe...\n')
                f.write(f'start "" "{nighty_exe}"\n')
                f.write('echo Nighty.exe restart initiated!\n')
                f.write('echo.\n')
                f.write('echo This window will close in 5 seconds...\n')
                f.write('timeout /t 5 /nobreak >nul\n')
                f.write('exit\n')
            
            return batch_path
            
        except Exception:
            return False
    
    try:
        # Send initial message
        msg = await ctx.send("🔍 Searching for Nighty.exe process...")
        await asyncio.sleep(1)
        
        # Get Nighty.exe path
        nighty_path = get_nighty_exe_path()
        
        if not nighty_path:
            await msg.edit(content="❌ Nighty.exe is not currently running!")
            return
        
        await msg.edit(content="✅ Found Nighty.exe process")
        await asyncio.sleep(1)
        
        # Create batch file
        batch_file = create_restart_batch(nighty_path)
        
        if batch_file:
            await msg.edit(content="📁 Created restart batch file")
            await asyncio.sleep(1)
            
            # Start the batch file
            try:
                os.startfile(batch_file)
                await msg.edit(content="🚀 Batch file started! Nighty.exe will restart independently.")
            except Exception as e:
                await msg.edit(content="❌ Error starting batch file")
        else:
            await msg.edit(content="❌ Failed to create batch file!")
            
    except Exception as e:
        await ctx.send("❌ Error during force restart")

