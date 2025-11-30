@nightyScript(
    name="Speedtest",
    author="Boredom",
    description="Run a network speed test and display results in an embed.",
    usage="<p>speedtest"
)
def speedtest_script():
    """
    SPEEDTEST
    ---------
    
    Performs a network speed test to measure ping, download, and upload speeds.
    Results are displayed in an embed with no private information included.
    
    COMMANDS:
    <p>speedtest - Run a network speed test
    
    EXAMPLES:
    <p>speedtest - Run the speed test and display results
    
    NOTES:
    - Uses HTTP requests to public servers to measure speed
    - Does not require any additional downloads
    - Results may vary based on network conditions
    """
    import time
    import random
    import string
    import aiohttp
    import asyncio
    from datetime import datetime
    
    # Define debug logging
    def debug_log(message, type_="INFO"):
        """Log events to console with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [SPEEDTEST] [{type_}] {message}", type_=type_)
    
    # Test URLs - these are public files of various sizes that won't change
    TEST_URLS = [
        "https://speed.cloudflare.com/__down?bytes=1048576",  # 1MB from Cloudflare
        "https://speed.cloudflare.com/__down?bytes=10485760",  # 10MB from Cloudflare
    ]
    
    # Define upload endpoint
    UPLOAD_URL = "https://speed.cloudflare.com/__up"  # Cloudflare speed test upload endpoint
    
    # Ping test URL
    PING_URL = "https://www.cloudflare.com/cdn-cgi/trace"
    
    @bot.command(name="speedtest", description="Run a network speed test")
    async def speedtest_command(ctx, *, args: str = ""):
        """Run a network speed test and display results"""
        await ctx.message.delete()
        
        status_msg = await ctx.send("🔄 Running speed test, please wait...")
        
        try:
            # Run the speed test
            results = await run_speed_test()
            
            # Save current private setting and update it to False (disable private mode)
            current_private = getConfigData().get("private")
            updateConfigData("private", False)
            
            # Create embed content
            title = "📶 Network Speed Test Results"
            content = f"""
            ⏱️ **Ping**: {results['ping']} ms
            ⬇️ **Download**: {results['download']} Mbps
            ⬆️ **Upload**: {results['upload']} Mbps
            
            ℹ️ Test completed at {datetime.now().strftime('%H:%M:%S')}
            """
            
            # Send the embed
            await forwardEmbedMethod(
                channel_id=ctx.channel.id, 
                content=content,
                title=title
            )
            
            # Restore original private setting
            updateConfigData("private", current_private)
            
        except Exception as e:
            debug_log(f"Error during speed test: {str(e)}", type_="ERROR")
            await status_msg.edit(content=f"❌ Error running speed test: {str(e)}")
            return
        finally:
            # Clean up status message
            await status_msg.delete()
    
    async def measure_ping():
        """Measure ping by timing a simple HTTP request"""
        ping_times = []
        
        async with aiohttp.ClientSession() as session:
            for _ in range(3):  # Take multiple samples
                start_time = time.time()
                async with session.get(PING_URL) as response:
                    await response.text()
                    end_time = time.time()
                
                # Calculate round-trip time in milliseconds
                rtt = (end_time - start_time) * 1000
                ping_times.append(rtt)
                await asyncio.sleep(0.5)  # Brief pause between tests
        
        # Return the average ping, rounded to 2 decimals
        return round(sum(ping_times) / len(ping_times), 2)
    
    async def measure_download_speed():
        """Measure download speed by downloading test files"""
        download_speeds = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            for url in TEST_URLS:
                start_time = time.time()
                async with session.get(url) as response:
                    data = await response.read()
                    end_time = time.time()
                
                # Calculate speed in Mbps (Megabits per second)
                # Size in bytes * 8 (to bits) / 1_000_000 (to megabits) / time (seconds)
                file_size = len(data)
                duration = end_time - start_time
                speed_mbps = (file_size * 8) / 1_000_000 / duration
                download_speeds.append(speed_mbps)
        
        # Return the average speed, rounded to 2 decimals
        return round(sum(download_speeds) / len(download_speeds), 2)
    
    async def measure_upload_speed():
        """Measure upload speed by uploading random data"""
        upload_speeds = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Create test data sizes
        test_sizes = [1_000_000, 5_000_000]  # 1MB and 5MB
        
        async with aiohttp.ClientSession(headers=headers) as session:
            for size in test_sizes:
                # Generate random data
                data = ''.join(random.choices(string.ascii_letters + string.digits, k=size)).encode()
                
                start_time = time.time()
                async with session.post(UPLOAD_URL, data=data) as response:
                    await response.text()
                    end_time = time.time()
                
                # Calculate speed in Mbps
                duration = end_time - start_time
                speed_mbps = (size * 8) / 1_000_000 / duration
                upload_speeds.append(speed_mbps)
        
        # Return the average speed, rounded to 2 decimals
        return round(sum(upload_speeds) / len(upload_speeds), 2)
    
    async def run_speed_test():
        """Run the full speed test"""
        debug_log("Starting speed test")
        
        # Measure ping
        debug_log("Measuring ping")
        ping = await measure_ping()
        debug_log(f"Ping: {ping} ms")
        
        # Measure download speed
        debug_log("Measuring download speed")
        download = await measure_download_speed()
        debug_log(f"Download: {download} Mbps")
        
        # Measure upload speed
        debug_log("Measuring upload speed")
        upload = await measure_upload_speed()
        debug_log(f"Upload: {upload} Mbps")
        
        return {
            "ping": ping,
            "download": download,
            "upload": upload
        }
    
    debug_log("Speedtest script initialized")

# Call the function to activate the script
speedtest_script()