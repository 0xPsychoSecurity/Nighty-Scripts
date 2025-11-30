# Hi user, firts of all thank you for downloading this
# Please start off by using (prefix)helpas
# DO NOT change the code unless you know what you are doing!
# Made with ❤️ by Flixer
@nightyScript(
    name="Auto Message Sender",
    author="Flixer",
    description="Automatically send message to multiple channels with an interval. ID system for each message for easy management to stop or list all the tasks, advanced error logging.",
    usage="asend <interval> <channel> <message>"
)
def autosender():
    tasks = {}
    message_id_counter = 1

    @bot.command(usage="<interval> <channel> <message>", description="Auto-send messages periodically.")
    async def asend(ctx, interval: int, channel: discord.TextChannel, *, message: str):
        nonlocal message_id_counter

        try:
            if interval <= 0:
                await ctx.send("⚠️ The interval must be a positive number greater than 0.")
                return

            if not message:
                await ctx.send("⚠️ You must provide a message to send.")
                return

            message_id = message_id_counter
            message_id_counter += 1

            if ctx.author.id not in tasks:
                tasks[ctx.author.id] = {}

            async def send_message():
                try:
                    while True:
                        await channel.send(message)
                        await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    pass

            task = asyncio.create_task(send_message())
            tasks[ctx.author.id][message_id] = {'task': task, 'channel': channel, 'message': message, 'interval': interval}

            await ctx.send(f"✅ Auto-sending started in {channel.mention} every {interval} seconds. Message ID: {message_id}.")

        except Exception as e:
            logging.error(f"Error in asend command by {ctx.author}: {str(e)}")
            await ctx.send("⚠️ An unexpected error occurred while trying to start the auto-sender task.")

    @bot.command(usage="", description="Stops a specific auto-sender task using its ID.")
    async def stopas(ctx, message_id: int = None):
        try:
            if message_id is None:
                await ctx.send("⚠️ You must provide a message ID to stop a specific auto-sender task.")
                return

            task_info = tasks.get(ctx.author.id, {}).get(message_id)
            if task_info:
                task_info['task'].cancel()
                del tasks[ctx.author.id][message_id]
                await ctx.send(f"✅ Auto-sending task {message_id} stopped.")
            else:
                await ctx.send(f"⚠️ No active task with ID {message_id} found.")

        except Exception as e:
            logging.error(f"Error in stopas command by {ctx.author}: {str(e)}")
            await ctx.send("⚠️ An error occurred while trying to stop the task. Please check the message ID.")

    @bot.command(usage="", description="Lists all active auto-send tasks.")
    async def listauto(ctx):
        try:
            user_tasks = tasks.get(ctx.author.id, {})
            if not user_tasks:
                await ctx.send("⚠️ No active auto-sending tasks.")
                return

            task_list = f"**Active Auto-Sender Tasks for {ctx.author.display_name}:**\n"

            for message_id, task_info in user_tasks.items():
                task_list += (
                    f"\n**Task ID**: {message_id}\n"
                    f"**Channel**: {task_info['channel'].mention}\n"
                    f"**Message**: {task_info['message'][:50]}... (truncated)\n"
                    f"**Interval**: {task_info['interval']} seconds\n"
                    "------------------------"
                )

            await ctx.send(task_list)

        except Exception as e:
            logging.error(f"Error in listauto command by {ctx.author}: {str(e)}")
            await ctx.send("⚠️ An error occurred while trying to list your active tasks.")

    @bot.command(usage="", description="Stops all active auto-sender tasks.")
    async def stopall(ctx):
        try:
            user_tasks = tasks.pop(ctx.author.id, {})
            if not user_tasks:
                await ctx.send("⚠️ No active tasks to stop.")
                return

            for task_info in user_tasks.values():
                task_info['task'].cancel()

            await ctx.send("✅ All auto-sending tasks stopped.")

        except Exception as e:
            logging.error(f"Error in stopall command by {ctx.author}: {str(e)}")
            await ctx.send("⚠️ An error occurred while trying to stop all tasks.")

    @bot.command(usage="", description="Displays information about the auto-sender commands.")
    async def helpas(ctx):
        try:
            help_message = (
                "**Auto Sender Help - Commands List**\n\n"
                "### `asend <interval> <channel> <message>`\n"
                " - Starts an auto-sender task that sends a message periodically in the specified channel.\n"
                "   - `interval` is the number of seconds between each message (positive number).\n"
                "   - `channel` is the channel where the message will be sent.\n"
                "   - `message` is the message that will be sent.\n"
                "### `stopas <message_id>`\n"
                " - Stops the auto-sending task with the given `message_id`.\n"
                "   - Use this command to stop a specific task.\n"
                "### `listauto`\n"
                " - Lists all active auto-sending tasks for the user.\n"
                "   - Shows the task ID, channel, message preview, and interval for each task.\n"
                "### `stopall`\n"
                "   - Stops all active auto-sending tasks for the user.\n\n"
                "\n**Made with ❤️ by Flixer**"
            )

            await ctx.send(help_message)

        except Exception as e:
            logging.error(f"Error in helpas command by {ctx.author}: {str(e)}")
            await ctx.send("⚠️ An error occurred while trying to display help information.")

autosender()
