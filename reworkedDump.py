# UPDATE BY LUXED

# Change Log v1.4.5.1:
# --- New Features ---

# --- Performance & Optimization ---

# --- Fixes ---
# - Fixed the error "NoneType object has no attribute lowe"

# --- Coming Soon (v1.4.6) ---
# New filters for Embeds and Links
# Further optimization of Channel, DM, and Group dump operations.

@nightyScript(
    name="Reworked Dump UI",
    author="Luxed",
    description="Dumps a whole channel, DM or entire server to txt files with filtering options and optional HTML output",
    usage="UI Script"
)
def dump():
    import html

    def build_html_header(title, guild_info, channel_info):
        header = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
        background-color: #2C2F33;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #FFFFFF;
        margin: 0;
        padding: 20px;
        line-height: 1.6;
        }}
        .container {{
        max-width: 900px;
        margin: 0 auto;
        background-color: #23272A;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        overflow: hidden;
        }}
        .header {{
        background-color: #202225;
        padding: 20px;
        text-align: center;
        border-bottom: 1px solid #2C2F33;
        }}
        .header h1 {{
        margin: 0;
        font-size: 2em;
        color: #7289DA;
        }}
        .header p {{
        margin: 8px 0 0 0;
        font-size: 0.95em;
        color: #99AAB5;
        }}
        .search-container {{
        margin: 15px auto;
        max-width: 500px;
        text-align: center;
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #23272A;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }}
        #searchInput {{
        width: 90%;
        padding: 8px;
        border-radius: 4px;
        border: none;
        outline: none;
        font-size: 1em;
        background-color: #2C2F33;
        color: #FFFFFF;
        }}
        .search-navigation {{
        display: flex;
        align-items: center;
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        }}
        .search-count {{
        font-size: 0.8em;
        color: #99AAB5;
        margin-right: 8px;
        }}
        .nav-button {{
        background: #4f545c;
        border: none;
        border-radius: 4px;
        color: white;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        margin: 0 2px;
        }}
        .nav-button:hover {{
        background: #7289DA;
        }}
        .nav-button:disabled {{
        background: #36393f;
        color: #72767d;
        cursor: not-allowed;
        }}
        .messages {{
        padding: 20px;
        }}
        .message {{
        background-color: #2C2F33;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        display: flex;
        align-items: flex-start;
        }}
        .message:nth-child(even) {{
        background-color: #2E3338;
        }}
        .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
        flex-shrink: 0;
        }}
        .msg-content {{
        flex: 1;
        }}
        .meta {{
        font-size: 0.85em;
        margin-bottom: 8px;
        color: #99AAB5;
        }}
        .meta strong {{
        color: #7289DA;
        }}
        .forwarded-indicator {{
            color: #99AAB5;
            font-size: 0.8em;
            margin-bottom: 5px;
            font-style: italic;
        }}
        .content {{
        font-size: 1em;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin-bottom: 10px;
        }}
        .sticker-container {{
            margin-top: 8px;
        }}
        .sticker {{
            width: 200px;
            height: 200px;
            border-radius: 5px;
        }}
        .sticker-unrenderable {{
            background-color: #36393F;
            border: 1px dashed #4A4E58;
            border-radius: 5px;
            padding: 10px;
            font-size: 0.9em;
            text-align: center;
            width: 180px; /* Adjusted for padding */
            display: inline-block;
            color: #DCDDDE;
            font-weight: 500;
        }}
        .reactions-container {{
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 8px;
        }}
        .reaction {{
            display: flex;
            align-items: center;
            background-color: #3C4048;
            border-radius: 16px;
            padding: 4px 8px;
            font-size: 0.9em;
            color: #DCDDDE;
            border: 1px solid #4A4E58;
        }}
        .reaction-emoji {{
            width: 1.2em;
            height: 1.2em;
            margin-right: 6px;
            vertical-align: middle;
        }}
        .reply {{
        background-color: #36393F;
        border-left: 4px solid #43B581;
        padding: 10px;
        margin: 10px 0;
        font-size: 0.9em;
        border-radius: 5px;
        }}
        .attachments {{
        margin-top: 10px;
        padding: 10px;
        background-color: #36393F;
        border-radius: 5px;
        }}
        .attachment {{
        margin: 10px 0;
        }}
        .attachment img, .attachment video, .attachment audio {{
        border-radius: 5px;
        margin-top: 5px;
        max-width: 100%;
        display: block;
        }}
        .attachment a {{
        color: #7289DA;
        text-decoration: none;
        }}
        .attachment a:hover {{
        text-decoration: underline;
        }}
        .footer {{
        background-color: #202225;
        padding: 15px;
        text-align: center;
        font-size: 0.9em;
        color: #99AAB5;
        }}
        a {{
        color: #00B0F4;
        }}

        .emoji {{
            width: 1.375em;
            height: 1.375em;
            margin: 0 0.05em;
            vertical-align: -0.4em;
        }}
        .embed {{
            background-color: #2f3136;
            border-left: 4px solid #4f545c; 
            border-radius: 4px;
            display: flex;
            gap: 16px;
            padding: 8px 16px;
            margin-top: 8px;
        }}
        .embed-content {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex: 1;
            min-width: 0; 
        }}
        .embed-author {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.875em;
            font-weight: 500;
        }}
        .embed-author img {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
        }}
        .embed-author a {{
            color: #ffffff;
            font-weight: 600;
            text-decoration: none;
        }}
        .embed-author a:hover {{
            text-decoration: underline;
        }}
        .embed-title {{
            font-weight: 700;
            color: #ffffff;
        }}
        .embed-title a {{
            color: #00a8fc;
            text-decoration: none;
            font-weight: 700;
        }}
        .embed-title a:hover {{
            text-decoration: underline;
        }}
        .embed-description {{
            font-size: 0.9em;
            color: #dcddde; 
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .embed-fields {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 8px;
        }}
        .embed-field {{
            font-size: 0.9em;
        }}
        .embed-field:not(.embed-field-inline) {{
            grid-column: 1 / -1;
        }}
        .embed-field-name {{
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 2px;
        }}
        .embed-field-value {{
            color: #dcddde;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .embed-thumbnail {{
            flex-shrink: 0;
            align-self: flex-start;
            width: 80px;
            height: 80px;
            object-fit: cover;
            border-radius: 4px;
            margin-top: 8px;
        }}
        .embed-image-container {{
            margin-top: 8px;
        }}
        .embed-image {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        .embed-footer {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.75em;
            color: #c7c9c8;
        }}
        .embed-footer img {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
        <h1>{title}</h1>
        <p>{guild_info}</p>
        <p>{channel_info}</p>
        <p>Dumped at: {datetime.now()}</p>
        </div>
        <div class="search-container">
        <input type="text" id="searchInput" onkeyup="searchMessages()" placeholder="Search messages...">
        <div class="search-navigation">
            <span id="searchCount" class="search-count">0 of 0</span>
            <button id="prevButton" class="nav-button" onclick="prevMatch()" disabled>▲</button>
            <button id="nextButton" class="nav-button" onclick="nextMatch()" disabled>▼</button>
        </div>
        </div>
        <div class="messages">
    """
        return header

    def build_html_footer(processed, dumped):
        footer = f"""
        </div>
        <div class="footer">
        <p>Dump Complete - Processed: {processed} | Dumped: {dumped}</p>
        <p><a href="#top">Back to Top</a></p>
        </div>
    </div>

    <script>
        var currentMatchIndex = 0;
        var foundMessages = [];
        var isSearching = false;

        function updateSearchPosition() {{
        var searchContainer = document.querySelector('.search-container');
        var searchInput = document.getElementById('searchInput');
        if (searchInput.value.trim() !== "") {{
            searchContainer.style.position = "fixed";
            searchContainer.style.top = "20px";
            isSearching = true;
        }} else {{
            searchContainer.style.position = "relative";
            searchContainer.style.top = "auto";
            searchContainer.style.transform = "none";
            searchContainer.style.left = "auto";
            isSearching = false;
        }}
        }}

        function updateSearchCount(current, total) {{
        var countElement = document.getElementById('searchCount');
        var prevButton = document.getElementById('prevButton');
        var nextButton = document.getElementById('nextButton');
        countElement.textContent = total > 0 ? current + " de " + total : "0 de 0";
        prevButton.disabled = total === 0 || current <= 1;
        nextButton.disabled = total === 0 || current >= total;
        }}

        function searchMessages() {{
        var input = document.getElementById('searchInput');
        var filter = input.value.toLowerCase();
        var messages = document.getElementsByClassName('message');
        foundMessages = [];
        currentMatchIndex = 0;
        updateSearchPosition();

        for (var i = 0; i < messages.length; i++) {{
            messages[i].style.display = "";
            messages[i].style.backgroundColor = "";
            messages[i].style.boxShadow = "";
        }}

        if (filter.trim() === "") {{
            updateSearchCount(0, 0);
            return;
        }}

        for (var i = 0; i < messages.length; i++) {{
            var contentElement = messages[i].querySelector('.content');
            var attachmentElement = messages[i].querySelector('.attachments');
            var replyElement = messages[i].querySelector('.reply');
            var replyText = "";

            if (replyElement) {{
            var replyContent = replyElement.textContent || replyElement.innerText;
            var replyMatch = replyContent.match(/Replying to [^\\n]+(\\n|$)/);
            if (replyMatch) {{
                replyText = replyContent.substring(replyMatch[0].length).trim();
            }} else {{
                replyText = replyContent;
            }}
            }}

            var contentText = contentElement ? contentElement.textContent || contentElement.innerText : "";
            var attachmentText = attachmentElement ? attachmentElement.textContent || attachmentElement.innerText : "";
            var searchableText = contentText + " " + replyText + " " + attachmentText;

            if (searchableText.toLowerCase().indexOf(filter) > -1) {{
            messages[i].style.backgroundColor = "#3b4048";
            messages[i].style.boxShadow = "0 0 8px rgba(114, 137, 218, 0.7)";
            foundMessages.push(messages[i]);
            }}
        }}

        updateSearchCount(currentMatchIndex + 1, foundMessages.length);
        navigateToMatch(0);
        }}

        function navigateToMatch(index) {{
        if (foundMessages.length === 0) return;
        if (index < 0) index = 0;
        if (index >= foundMessages.length) index = foundMessages.length - 1;
        currentMatchIndex = index;

        for (var i = 0; i < foundMessages.length; i++) {{
            foundMessages[i].style.backgroundColor = "#3b4048";
        }}

        foundMessages[currentMatchIndex].style.backgroundColor = "#4f545c";
        foundMessages[currentMatchIndex].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        updateSearchCount(currentMatchIndex + 1, foundMessages.length);
        }}

        function nextMatch() {{
        if (currentMatchIndex < foundMessages.length - 1) {{
            navigateToMatch(currentMatchIndex + 1);
        }}
        }}

        function prevMatch() {{
        if (currentMatchIndex > 0) {{
            navigateToMatch(currentMatchIndex - 1);
        }}
        }}

        document.addEventListener('DOMContentLoaded', function () {{
        updateSearchPosition();
        }});
    </script>
    </body>
    </html>
    """
        return footer

    selected_attachment_filters = []

    def get_emoji_html(emoji, is_reaction=False):
        class_name = "reaction-emoji" if is_reaction else "emoji"
        
        if hasattr(emoji, 'url'):
            return f'<img src="{emoji.url}" alt="{getattr(emoji, "name", "emoji")}" class="{class_name}">'

        if isinstance(emoji, str):
            match = re.match(r'<a?:(\w+):(\d+)>', emoji)
            if match:
                name = match.group(1)
                emoji_id = match.group(2)
                is_animated = emoji.startswith('<a:')
                extension = "gif" if is_animated else "png"
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{extension}"
                return f'<img src="{emoji_url}" alt="{name}" class="{class_name}">'
            else:
                return f'<span class="{class_name}">{html.escape(emoji)}</span>'

        return f'<span>{html.escape(str(emoji))}</span>'

    TIMESTAMP_RE = re.compile(r'<t:(\d+):([tTdDfFR])>')
    USER_MENTION_RE = re.compile(r'<@!?(\d+)>')
    ROLE_MENTION_RE = re.compile(r'<@&(\d+)>')
    CHANNEL_MENTION_RE = re.compile(r'<#(\d+)>')
    EMOJI_ANIMATED_RE = re.compile(r'&lt;a:(\w+):(\d+)&gt;')
    EMOJI_STATIC_RE = re.compile(r'&lt;:(\w+):(\d+)&gt;')

    TYPE_EXTENSIONS = {
        "image": ["png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff"],
        "video": ["mp4", "webm", "mov", "avi", "mkv", "flv", "wmv", "m4v"],
        "audio": ["mp3", "wav", "ogg", "flac", "m4a", "aac"],
        "text": ["txt", "md", "log", "json", "xml", "csv", "html", "css", "js"],
        "application": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "pub", "odt","ods", "odp", "rtf",
        "py", "pyw", "mjs", "cjs", "java", "class", "jar", "c", "cpp", "cc", "cxx", "h", "cs", "rb", "php", "phtml", "go",
        "ts", "tsx", "htm", "jsx", "sql", "db"],
        "rar": ["rar"],
        "zip": ["zip", "7z", "gz", "tar"]
    }

    # ---- UI Implementation ----
    def validate_id(new_value, current_input):
        if not new_value.strip():
            current_input.invalid = False
            current_input.error_message = None
            return True
        
        if not new_value.isdigit():
            current_input.invalid = True
            current_input.error_message = "ID must be a number"
            return False
        
        current_input.invalid = False
        current_input.error_message = None
        return True
    
    def validate_limit(new_value, current_input):
        if not new_value.strip():
            current_input.invalid = False
            current_input.error_message = None
            return True
        
        if not new_value.isdigit():
            current_input.invalid = True
            current_input.error_message = "Limit must be a number"
            return False
        
        current_input.invalid = False
        current_input.error_message = None
        return True

    def check_server_id(new_value):
        validate_id(new_value, server_id_input)
        update_dump_button_state()
        update_serverdump_button_state()
    
    def check_channel_id(event):
        dump_button.disabled = True
        
        if not channel_id_input.value:
            channel_id_input.invalid = False
            channel_id_input.error_message = None
            return
            
        try:
            if not channel_id_input.value.isdigit():
                channel_id_input.invalid = True
                channel_id_input.error_message = "Channel ID must be a number"
                return
                
            channel_id_input.invalid = False
            channel_id_input.error_message = None
            dump_button.disabled = False
                
        except Exception as e:
            channel_id_input.invalid = True
            channel_id_input.error_message = f"Invalid channel ID: {str(e)}"
    
    def check_user_id(new_value):
        validate_id(new_value, user_id_input)
        update_dmdump_button_state()
    
    def check_limit(new_value):
        validate_limit(new_value, limit_input)
        save_dump_settings("message_limit", new_value)
    
    def update_dump_button_state():
        if (not server_id_input.invalid and server_id_input.value and 
            not channel_id_input.invalid and channel_id_input.value):
            dump_button.disabled = False
        else:
            dump_button.disabled = True
    
    def update_dmdump_button_state():
        if not user_id_input.invalid and user_id_input.value:
            dmdump_button.disabled = False
        else:
            dmdump_button.disabled = True
    
    def update_serverdump_button_state():
        if not server_id_input.invalid and server_id_input.value:
            serverdump_button.disabled = False
        else:
            serverdump_button.disabled = True

    def process_mentions(content, message):
        if not content:
            return content

        user_mentions = USER_MENTION_RE.findall(content)
        for user_id in user_mentions:
            user = bot.get_user(int(user_id))
            if user:
                content = content.replace(f'<@{user_id}>', f'@{user.display_name}')
                content = content.replace(f'<@!{user_id}>', f'@{user.display_name}')
        
        if hasattr(message.channel, 'guild') and message.channel.guild:
            role_mentions = ROLE_MENTION_RE.findall(content)
            for role_id in role_mentions:
                role = message.channel.guild.get_role(int(role_id))
                if role:
                    content = content.replace(f'<@&{role_id}>', f'@{role.name}')
            
        channel_mentions = CHANNEL_MENTION_RE.findall(content)
        for channel_id in channel_mentions:
            channel = bot.get_channel(int(channel_id))
            if channel:
                content = content.replace(f'<#{channel_id}>', f'#{channel.name}')
                
        return content
    
    def process_all_markdown(text, message):
        if not text:
            return text

        processed_text = process_mentions(text, message)

        def replace_timestamp(match):
            timestamp = int(match.group(1))
            format_code = match.group(2)
            dt_object = datetime.fromtimestamp(timestamp)
            
            format_map = {'t': '%I:%M %p', 'T': '%I:%M:%S %p', 'd': '%m/%d/%Y', 'D': '%B %d, %Y', 'f': '%B %d, %Y %I:%M %p', 'F': '%A, %B %d, %Y %I:%M %p', 'R': '%B %d, %Y %I:%M %p'}
            format_string = format_map.get(format_code, format_map['f']) 
            return dt_object.strftime(format_string)

        processed_text = TIMESTAMP_RE.sub(replace_timestamp, processed_text)
        return processed_text


    def process_text_for_html(text, message):
        if not isinstance(text, str):
            return ''
        
        processed_text = process_all_markdown(text, message)
        processed_text = processed_text.replace("<", "&lt;").replace(">", "&gt;")
        
        processed_text = EMOJI_ANIMATED_RE.sub(
            lambda m: f'<img src="https://cdn.discordapp.com/emojis/{m.group(2)}.gif" alt=":{m.group(1)}:" class="emoji">', 
            processed_text
        )
        processed_text = EMOJI_STATIC_RE.sub(
            lambda m: f'<img src="https://cdn.discordapp.com/emojis/{m.group(2)}.png" alt=":{m.group(1)}:" class="emoji">', 
            processed_text
        )
        
        return processed_text

    def process_embeds(message):
        if not message.embeds:
            return None, None
            
        text_embeds = []
        html_embeds = []
        
        for embed in message.embeds:
            text_embed = "Embed:\n"
            if embed.title: text_embed += f"    Title: {embed.title}\n"
            if embed.description: text_embed += f"    Description: {embed.description}\n"
            text_embeds.append(text_embed)
            
            embed_color = f"#{embed.color.value:06x}" if embed.color else "#4f545c"
            html_embed = f'<div class="embed" style="border-left-color: {embed_color};">'
            
            html_embed += '<div class="embed-content">'
            
            if embed.author:
                html_embed += '<div class="embed-author">'
                if embed.author.icon_url:
                    html_embed += f'<img src="{embed.author.icon_url}" alt="author icon">'
                author_name = process_text_for_html(embed.author.name, message)
                if embed.author.url:
                    html_embed += f'<a href="{embed.author.url}" target="_blank">{author_name}</a>'
                else:
                    html_embed += f'<span>{author_name}</span>'
                html_embed += '</div>'

            if embed.title:
                title_text = process_text_for_html(embed.title, message)
                if embed.url:
                    html_embed += f'<div class="embed-title"><a href="{embed.url}" target="_blank">{title_text}</a></div>'
                else:
                    html_embed += f'<div class="embed-title">{title_text}</div>'

            if embed.description:
                desc_text = process_text_for_html(embed.description, message).replace("\n", "<br>")
                html_embed += f'<div class="embed-description">{desc_text}</div>'
            
            if embed.fields:
                html_embed += '<div class="embed-fields">'
                for field in embed.fields:
                    field_name = process_text_for_html(field.name, message).replace("\n", "<br>")
                    field_value = process_text_for_html(field.value, message).replace("\n", "<br>")
                    field_classes = "embed-field embed-field-inline" if field.inline else "embed-field"
                    html_embed += f'<div class="{field_classes}">'
                    html_embed += f'<div class="embed-field-name">{field_name}</div>'
                    html_embed += f'<div class="embed-field-value">{field_value}</div>'
                    html_embed += '</div>'
                html_embed += '</div>'
            
            if embed.image and embed.image.url:
                html_embed += f'<div class="embed-image-container"><img src="{embed.image.url}" alt="embed image" class="embed-image"></div>'
            
            if embed.footer or embed.timestamp:
                html_embed += '<div class="embed-footer">'
                if embed.footer and embed.footer.icon_url:
                    html_embed += f'<img src="{embed.footer.icon_url}" alt="footer icon">'
                
                footer_text_processed = ""
                if embed.footer and embed.footer.text:
                    footer_text_processed = process_text_for_html(embed.footer.text, message)

                if embed.timestamp:
                    if footer_text_processed:
                        footer_text_processed += f' • {embed.timestamp}'
                    else:
                        footer_text_processed = str(embed.timestamp)

                html_embed += f'<span>{footer_text_processed}</span>'
                html_embed += '</div>'
            
            html_embed += '</div>'

            if embed.thumbnail and embed.thumbnail.url:
                html_embed += f'<img src="{embed.thumbnail.url}" alt="thumbnail" class="embed-thumbnail">'
            
            html_embed += '</div>'
            html_embeds.append(html_embed)
            
        return "\n".join(text_embeds), "\n".join(html_embeds)

    async def execute_dump():
        try:
            if not channel_id_input.value:
                dump_tab.toast(type="ERROR", title="Error", description="Channel ID is required.")
                status_text.content = "Status: Error - Missing Channel ID"
                return
            
            limit_val = int(limit_input.value) if limit_input.value else None
        
        except ValueError:
            status_text.content = "Status: Error - Invalid ID or limit format"
            dump_tab.toast(type="ERROR", title="Error", description="Invalid channel or limit ID format.")
            return

        dump_button.loading = True
        status_text.content = f"Status: Finding channel {channel_id_input.value}..."
        
        # Use the new smart find function
        channel, guild = await find_channel_and_guild(channel_id_input.value)

        if not channel or not guild:
            status_text.content = "Status: Error - Channel not found"
            dump_tab.toast(type="ERROR", title="Error", description="Could not find a channel with that ID in any accessible server.")
            dump_button.loading = False
            return

        status_text.content = f"Status: Dumping channel #{channel.name} from server {guild.name}..."

        try:
            await dump(None, channel, guild, create_html_toggle.checked,
                    limit_val, attachments_only_toggle.checked, save_attachments_toggle.checked)
        except Exception as e:
            status_text.content = f"Status: Error - {str(e)}"
            dump_tab.toast(type="ERROR", title="Error", description=str(e))
        finally:
            dump_button.loading = False

    async def execute_dmdump():
        dmdump_button.loading = True
        status_text.content = "Status: Dumping DM/Group chat..."

        try:
            if not user_id_input.value:
                status_text.content = "Status: Error - No user/group ID provided"
                dump_tab.toast(type="ERROR", title="Error", description="Please enter a user or group ID")
                dmdump_button.loading = False
                return

            user_id = int(user_id_input.value)
            limit_val = int(limit_input.value) if limit_input.value else None

            is_group = False
            is_user = False
            channel = bot.get_channel(user_id)
            
            if channel and isinstance(channel, discord.GroupChannel):
                is_group = True
            elif channel and isinstance(channel, discord.DMChannel):
                 is_user = True
            else:
                try:
                    user = await bot.fetch_user(user_id)
                    if user:
                        is_user = True
                except (discord.NotFound, discord.HTTPException):
                    pass


            if is_group:
                await groupdump(None, user_id, create_html_toggle.checked,
                        limit_val, attachments_only_toggle.checked, save_attachments_toggle.checked)
            elif is_user:
                await dmdump(None, user_id, create_html_toggle.checked,
                            limit_val, attachments_only_toggle.checked, save_attachments_toggle.checked)
            else:
                status_text.content = "Status: User or group chat not found"
                dump_tab.toast(type="ERROR", title="Error", description="User or group chat not found")

        except Exception as e:
            status_text.content = f"Status: Error - {str(e)}"
            dump_tab.toast(type="ERROR", title="Error", description=str(e))
        finally:
            dmdump_button.loading = False
    
    async def execute_serverdump():
        serverdump_button.loading = True
        status_text.content = "Status: Dumping server..."

        try:
            if not server_id_input.value:
                status_text.content = "Status: Error - No server ID provided"
                dump_tab.toast(type="ERROR", title="Error", description="Please enter a server ID")
                return

            server_id = int(server_id_input.value)
            limit_val = int(limit_input.value) if limit_input.value else None

            await serverdump(None, server_id, limit_val,
                           attachments_only_toggle.checked, save_attachments_toggle.checked, create_html_toggle.checked)
        except ValueError:
            status_text.content = "Status: Error - Invalid server ID"
            dump_tab.toast(type="ERROR", title="Error", description="Invalid server ID format")
        except Exception as e:
            status_text.content = f"Status: Error - {str(e)}"
            dump_tab.toast(type="ERROR", title="Error", description=str(e))
        finally:
            serverdump_button.loading = False
    
    def load_dump_settings():
        json_dir = Path(getScriptsPath()) / "json"
        json_dir.mkdir(exist_ok=True)
        settings_file = json_dir / "dump_settings.json"
        
        if not settings_file.exists():
            return {
                "create_html": False,
                "save_attachments": False,
                "attachment_filters": [],
                "message_limit": ""
            }
        
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "create_html": False,
                "save_attachments": False,
                "attachment_filters": [],
                "message_limit": ""
            }

    def log_failed_channel(failed_dumps_folder, channel, reason):
        try:
            os.makedirs(failed_dumps_folder, exist_ok=True)
            error_filename = f"FAILED - #{fix_filename(channel.name)} ({channel.id}).txt"
            error_filepath = os.path.join(failed_dumps_folder, error_filename)
            
            with open(error_filepath, "w", encoding="utf-8") as error_log:
                error_log.write(f"Failed to dump channel: #{channel.name} (ID: {channel.id})\n")
                error_log.write(f"Reason: {reason}\n")
        except Exception as e:
            print(f"CRITICAL: Could not write to FAILED DUMPS log for channel {channel.id}. Error: {e}")

    def save_dump_settings(key, value):
        settings = load_dump_settings()
        settings[key] = value
        
        json_dir = Path(getScriptsPath()) / "json"
        json_dir.mkdir(exist_ok=True)
        settings_file = json_dir / "dump_settings.json"
        
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

    def create_dump_folders():
        exe_dir = os.path.dirname(sys.executable)
        dumps_dir = os.path.join(exe_dir, "dumps")
        
        if not os.path.exists(dumps_dir):
            os.makedirs(dumps_dir)
            
        servers_dir = os.path.join(dumps_dir, "servers")
        dms_dir = os.path.join(dumps_dir, "dms")
        groups_dir = os.path.join(dumps_dir, "groups")
        
        for folder in [servers_dir, dms_dir, groups_dir]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                
        return {
            "main": dumps_dir,
            "servers": servers_dir,
            "dms": dms_dir,
            "groups": groups_dir
        }

    def load_channel_db():
        json_dir = Path(getScriptsPath()) / "json"
        db_file = json_dir / "channels_db.json"
        if not db_file.exists():
            return {"channel_to_server_map": {}, "server_info": {}}
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"channel_to_server_map": {}, "server_info": {}}

    def save_channel_db(db):
        json_dir = Path(getScriptsPath()) / "json"
        db_file = json_dir / "channels_db.json"
        try:
            with open(db_file, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=4)
        except Exception as e:
            print(f"[Reworked Dump] Error saving channel DB: {e}")

    def update_channel_db(db, channel):
        if not channel or not hasattr(channel, 'guild'):
            return db
            
        channel_id_str = str(channel.id)
        server = channel.guild
        server_id_str = str(server.id)

        needs_save = False
        if channel_id_str not in db["channel_to_server_map"]:
            db["channel_to_server_map"][channel_id_str] = server_id_str
            needs_save = True
        
        if server_id_str not in db["server_info"]:
            db["server_info"][server_id_str] = server.name
            needs_save = True

        if needs_save:
            save_channel_db(db)
            
        return db

    async def find_channel_and_guild(channel_id_str):
        try:
            channel_id = int(channel_id_str)
        except ValueError:
            return None, None

        # 1. Cache Check
        channel = bot.get_channel(channel_id)
        if channel and hasattr(channel, 'guild'):
            update_channel_db(load_channel_db(), channel)
            return channel, channel.guild

        # 2. Database Check
        db = load_channel_db()
        if channel_id_str in db["channel_to_server_map"]:
            server_id_str = db["channel_to_server_map"][channel_id_str]
            guild = bot.get_guild(int(server_id_str))
            if guild:
                try:
                    channel = guild.get_channel(channel_id) or await guild.fetch_channel(channel_id)
                    return channel, guild
                except (discord.NotFound, discord.Forbidden):
                    pass 

        # 3. API Check
        try:
            channel = await bot.fetch_channel(channel_id)
            if channel and hasattr(channel, 'guild'):
                update_channel_db(db, channel) 
                return channel, channel.guild
        except (discord.NotFound, discord.Forbidden):
            return None, None
            
        return None, None 

    def fix_filename(name):
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        
        for char in invalid_chars:
            name = name.replace(char, '_')
            
        fix = ""
        for char in name:
            if ord(char) < 32 or ord(char) > 126:
                fix += '_'
            else:
                fix += char
                
        fix = fix.strip('. ')
        
        if not fix:
            fix = "unnamed"
            
        return fix

    def open_dumps_folder():
        try:
            folders = create_dump_folders()
            dumps_dir = folders["main"]
            
            if os.path.exists(dumps_dir):
                os.startfile(dumps_dir)
                dump_tab.toast(type="INFO", title="Folder Opened", description=f"Dumps folder opened: {dumps_dir}")
            else:
                dump_tab.toast(type="ERROR", title="Error", description=f"Dumps folder does not exist: {dumps_dir}")
        except Exception as e:
            dump_tab.toast(type="ERROR", title="Error", description=f"Could not open dumps folder: {str(e)}")

    # ---- Create UI elements ----
    dump_tab = Tab(name="Reworked Dump", title="Reworked Dump", icon="cloud")
    container = dump_tab.create_container(type="rows")
    
    # ---- Main card ----
    main_card = container.create_card(height="full", width="full", gap=4)
    main_card.create_ui_element(UI.Text, content="Reworked Dump", size="xl", weight="bold")
    
    # --- Load saved settings at the beginning ---
    saved_settings = load_dump_settings()

    # ---- Server and channel inputs ----
    server_channel_group = main_card.create_group(type="columns", gap=3, full_width=True)
    server_items = []
    for guild in bot.guilds:
        server_items.append({
            "id": str(guild.id),
            "title": f"{guild.name} ({guild.id})"
        })
    
    server_id_input = server_channel_group.create_ui_element(
        UI.Input,
        label="Server ID",
        placeholder="Enter server ID",
        show_clear_button=True,
        onInput=check_server_id,
        full_width=True
    )
    
    channel_id_input = server_channel_group.create_ui_element(
        UI.Input,
        label="Channel ID (for channel dump)",
        placeholder="Enter channel or thread ID",
        show_clear_button=True,
        onInput=check_channel_id,
        full_width=True
    )       
    # ---- User input for DM dump ----
    user_group = main_card.create_group(type="columns", gap=3, full_width=True)
    user_id_input = user_group.create_ui_element(
        UI.Input, 
        label="User/Group ID (for DM or Group chat dump)", 
        placeholder="Enter user ID or group chat ID", 
        show_clear_button=True,
        onInput=check_user_id,
        full_width=True
    )
    
    limit_input = user_group.create_ui_element(
        UI.Input, 
        label="Message Limit (optional)", 
        placeholder="Number of messages to fetch", 
        show_clear_button=True,
        value=saved_settings.get("message_limit", ""),
        onInput=check_limit,
        full_width=True
    )
    
    options_group = main_card.create_group(type="columns", gap=3, full_width=True)
    
    def on_html_toggle_change(checked):
        save_dump_settings("create_html", checked)

    create_html_toggle = options_group.create_ui_element(
        UI.Toggle, 
        label="Create HTML Output", 
        checked=saved_settings.get("create_html", False), 
        onChange=on_html_toggle_change
    )
    
    attachments_only_toggle = options_group.create_ui_element(
        UI.Toggle, 
        label="Attachments Only", 
        checked=False
    )

    def on_save_attachments_toggle_change(checked):
        save_dump_settings("save_attachments", checked)

    save_attachments_toggle = options_group.create_ui_element(
        UI.Toggle,
        label="Save Attachments",
        checked=saved_settings.get("save_attachments", False),
        onChange=on_save_attachments_toggle_change
    )
    
    attachment_types = [
        {"id": "image", "title": "Images"},
        {"id": "video", "title": "Videos"},
        {"id": "audio", "title": "Audio"},
        {"id": "text", "title": "Text Files"},
        {"id": "application", "title": "Applications/Documents"},
        {"id": "rar", "title": "RAR Files"},
        {"id": "zip", "title": "ZIP Files"}
    ]
    
    selected_attachment_filters = saved_settings.get("attachment_filters", [])

    def update_attachment_filter_selection(selected: list):
        nonlocal selected_attachment_filters
        selected_attachment_filters = selected
        save_dump_settings("attachment_filters", selected)

    attachment_type_select = options_group.create_ui_element(
        UI.Select,
        label="Attachment Filter",
        items=attachment_types,
        mode="multiple",  
        selected_items=selected_attachment_filters, 
        onChange=update_attachment_filter_selection,
        full_width=True
    )
    
    def save_last_dump_info(dump_type, path):
        json_dir = Path(getScriptsPath()) / "json"
        json_dir.mkdir(exist_ok=True)
        settings_file = json_dir / "last_dump_info.json"
        info = {
            "type": dump_type,
            "path": path,
            "timestamp": datetime.now().isoformat()
        }
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(info, f, indent=4)
        except Exception as e:
            print(f"[Reworked Dump] Could not save last dump info: {e}")

    def open_last_dump():
        json_dir = Path(getScriptsPath()) / "json"
        info_file = json_dir / "last_dump_info.json"
        
        if not info_file.exists():
            dump_tab.toast(type="INFO", title="No History", description="No previous dump has been recorded.")
            return

        try:
            with open(info_file, "r", encoding="utf-8") as f:
                info = json.load(f)

            dump_type = info.get("type")
            base_path = info.get("path")

            if not dump_type or not base_path:
                dump_tab.toast(type="ERROR", title="Error", description="Last dump information is corrupted or missing.")
                return

            if dump_type == "server":
                if os.path.exists(base_path):
                    os.startfile(base_path)
                    dump_tab.toast(type="SUCCESS", title="Folder Opened", description="Successfully opened server dump folder.")
                else:
                    dump_tab.toast(type="ERROR", title="Not Found", description=f"The folder for the last server dump could not be found at: {base_path}")
            else:  # For "channel", "dm", "group"
                html_path = f"{base_path}.html"
                txt_path = f"{base_path}.txt"
                containing_folder = os.path.dirname(base_path)

                if os.path.exists(html_path):
                    os.startfile(html_path)  # Open the file
                    os.startfile(containing_folder) # Open the folder  
                    dump_tab.toast(type="SUCCESS", title="Dump Opened", description=f"Opened file '{os.path.basename(html_path)}' and its folder.")
                elif os.path.exists(txt_path):
                    os.startfile(txt_path)  # Open the file
                    os.startfile(containing_folder)  # Open the folder 
                    dump_tab.toast(type="SUCCESS", title="Dump Opened", description=f"Opened file '{os.path.basename(txt_path)}' and its folder.")
                else:
                    dump_tab.toast(type="ERROR", title="Not Found", description=f"The last dump file could not be found for base path: {base_path}")

        except Exception as e:
            dump_tab.toast(type="ERROR", title="Error", description=f"Could not open last dump: {str(e)}")

    buttons_group = main_card.create_group(type="columns", gap=3, full_width=True)
    
    dump_button = buttons_group.create_ui_element(
        UI.Button, 
        label="Dump Channel", 
        disabled=True, 
        full_width=False, 
        color="primary",
        onClick=execute_dump
    )
    
    dmdump_button = buttons_group.create_ui_element(
        UI.Button, 
        label="Dump DM/Group", 
        disabled=True, 
        full_width=False, 
        color="primary",
        onClick=execute_dmdump
    )
    
    serverdump_button = buttons_group.create_ui_element(
        UI.Button, 
        label="Dump Server", 
        disabled=True, 
        full_width=False, 
        color="primary",
        onClick=execute_serverdump
    )
    
    open_folder_button = buttons_group.create_ui_element(
        UI.Button,
        label="Open Dumps Folder",
        disabled=False,
        full_width=False,
        color="primary",
        onClick=open_dumps_folder
    )

    open_last_dump_button = buttons_group.create_ui_element(
        UI.Button,
        label="Open Last Dump",
        disabled=False,
        full_width=False,
        color="primary",
        onClick=open_last_dump
    )

    status_text = main_card.create_ui_element(
        UI.Text,
        content="Status: Ready",
        color="var(--text-muted)"
    )

    def create_server_metadata_file(guild, dump_folder_path):
        metadata_path = os.path.join(dump_folder_path, "info.json")
        
        metadata = {
            "server_info": {
                "id": str(guild.id),
                "name": guild.name,
                "owner_id": str(guild.owner_id),
                "created_at": guild.created_at.isoformat(),
                "member_count": guild.member_count,
                "icon_url": str(guild.icon.url) if guild.icon else None,
                "banner_url": str(guild.banner.url) if guild.banner else None,
                "description": guild.description
            },
            "roles": sorted([
                {
                    "id": str(role.id),
                    "name": role.name,
                    "color": str(role.color),
                    "position": role.position,
                } for role in guild.roles
            ], key=lambda r: r['position'], reverse=True),
            "emojis": [
                {
                    "id": str(emoji.id),
                    "name": emoji.name,
                    "url": str(emoji.url),
                    "animated": emoji.animated
                } for emoji in guild.emojis
            ],
            "stickers": [
                {
                    "id": str(sticker.id),
                    "name": sticker.name,
                    "format": str(sticker.format),
                    "url": str(sticker.url)
                } for sticker in guild.stickers
            ],
            "channel_structure": {
                "categories": [
                    {
                        "id": str(category.id),
                        "name": category.name,
                        "position": category.position,
                        "channels": sorted([
                            { "id": str(ch.id), "name": ch.name, "type": str(ch.type) }
                            for ch in category.channels
                        ], key=lambda c: c.get('name') or '')
                    } for category in sorted(guild.categories, key=lambda c: c.position)
                ],
                "no_category_channels": sorted([
                    { "id": str(ch.id), "name": ch.name, "type": str(ch.type) }
                    for ch in guild.channels if ch.category is None and not isinstance(ch, discord.CategoryChannel)
                ], key=lambda c: c.get('name') or '')
            },
            "dump_info": {
                "dumped_at": datetime.now().isoformat()
            }
        }
        
        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)
        except Exception:
            print(f"[Reworked Dump] Failed to create metadata file for {guild.name}: {e}")

    # ---- This is the universal helper function for message processing ----
    async def process_message_to_formats(message, is_server_dump_format=False):
        is_forward = message.flags.forwarded
        is_reply = message.type == discord.MessageType.reply

        referenced_message = None
        if (is_forward or is_reply) and message.reference and message.reference.message_id:
            try:
                ref_channel = bot.get_channel(message.reference.channel_id) or message.channel
                referenced_message = await ref_channel.fetch_message(message.reference.message_id)
            except Exception:
                referenced_message = None

        content_source = referenced_message if is_forward and referenced_message else message
        if not content_source:
            content_source = message

        # --- Text Block ---
        msg_block_parts = []
        if is_server_dump_format:
            msg_block_parts.append(f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {message.author} ({message.author.id})")
            if is_forward:
                msg_block_parts.append(" [Forwarded]")
            elif is_reply and referenced_message:
                msg_block_parts.append(f" [Replying to @{referenced_message.author.name}]")
            msg_block_parts.append(":\n")

            if is_reply and referenced_message:
                replied_content_text = process_all_markdown(referenced_message.content, referenced_message)
                if replied_content_text:
                    indented_content = '\n'.join([f'  > {line}' for line in replied_content_text.split('\n')])
                    msg_block_parts.append(f"{indented_content}\n")

            processed_content = process_all_markdown(content_source.content, content_source)
            msg_block_parts.append(f"{processed_content if processed_content else '[No Content]'}\n")
            
            text_embeds, _ = process_embeds(content_source)
            if text_embeds:
                msg_block_parts.append(text_embeds + "\n")

            if content_source.reactions:
                reactions_list = [f"{r.emoji}({r.count})" for r in content_source.reactions]
                msg_block_parts.append("  Reactions: " + ", ".join(reactions_list) + "\n")

            if content_source.attachments:
                att_list = [f"  > Attachment: {att.filename} ({att.url})" for att in content_source.attachments]
                msg_block_parts.append("\n".join(att_list) + "\n")
            msg_block_parts.append("-" * 60 + "\n")
        else:
            msg_block_parts.append(f"Message ID : {message.id}\n")
            msg_block_parts.append(f"Time       : {message.created_at}\n")
            msg_block_parts.append(f"Author     : {message.author} (ID: {message.author.id})\n")

            if is_forward:
                msg_block_parts.append("[Forwarded]\n")
            elif is_reply and referenced_message:
                msg_block_parts.append(f"[Replying to: {referenced_message.author} (ID: {referenced_message.id})]\n")
                replied_content_text = process_all_markdown(referenced_message.content, referenced_message)
                if replied_content_text:
                    indented_content = '\n'.join([f'    > {line}' for line in replied_content_text.split('\n')])
                    msg_block_parts.append(f"{indented_content}\n")
                replied_text_embeds, _ = process_embeds(referenced_message)
                if replied_text_embeds:
                    indented_embeds = '\n'.join([f'    {line}' for line in replied_text_embeds.split('\n')])
                    msg_block_parts.append(f"{indented_embeds}\n")
                if referenced_message.attachments:
                    msg_block_parts.append("    Attachments:\n" + "".join([f"        - {att.filename}: {att.url}\n" for att in referenced_message.attachments]))

            processed_content = process_all_markdown(content_source.content, content_source)
            text_embeds, _ = process_embeds(content_source)
            msg_block_parts.append(f"Content    :\n\n{processed_content if processed_content else ''}\n\n")

            if content_source.stickers:
                msg_block_parts.append("".join([f"STICKER: {sticker.name}\n" for sticker in content_source.stickers]) + "\n")
            if content_source.attachments:
                msg_block_parts.append("Attachments:\n" + "".join([f"    - {att.filename}: {att.url}\n" for att in content_source.attachments]))
            else:
                msg_block_parts.append("Attachments: [None]\n")
            if text_embeds:
                msg_block_parts.append(text_embeds + "\n")
            if content_source.reactions:
                reactions_list = [f"{r.emoji}({r.count})" for r in content_source.reactions]
                msg_block_parts.append("Reactions: " + ", ".join(reactions_list) + "\n")
            msg_block_parts.append(f"\n{'-'*60}\n\n")

        text_block = "".join(msg_block_parts)

        # --- HTML Block ---
        html_parts = []
        avatar_url = message.author.display_avatar.url
        html_parts.append(f'<div class="message"><img src="{avatar_url}" alt="avatar" class="avatar"><div class="msg-content"><div class="meta">')
        html_parts.append(f'<strong>{process_text_for_html(message.author.display_name, message)}</strong> <span>({message.author.id})</span> • {message.created_at} • ID: {message.id}')
        html_parts.append('</div>')

        if is_forward:
            html_parts.append('<div class="forwarded-indicator">↪ Forwarded</div>')

        if is_reply and referenced_message:
            html_parts.append('<div class="reply">')
            try:
                replied_author = process_text_for_html(referenced_message.author.display_name, referenced_message)
                replied_content = process_text_for_html(referenced_message.content, referenced_message).replace("\n", "<br>")
                html_parts.append(f"<strong>Replying to {replied_author}:</strong><br>{replied_content}")
                if referenced_message.attachments:
                    html_parts.append("<div class=\"attachments\" style='margin-top: 5px;'>")
                    for att in referenced_message.attachments:
                        html_parts.append(f'<div class="attachment" style=\'margin: 5px 0;\'><a href="{att.url}" target="_blank">{att.filename}</a></div>')
                    html_parts.append("</div>")
                _, replied_html_embeds = process_embeds(referenced_message)
                if replied_html_embeds:
                    html_parts.append("".join(replied_html_embeds))
                if referenced_message.reactions:
                    html_parts.append('<div class="reactions-container" style="padding-top: 5px; margin-top: 5px; border-top: 1px solid #4A4E58;">')
                    for reaction in referenced_message.reactions:
                        emoji_html = get_emoji_html(reaction.emoji, is_reaction=True)
                        html_parts.append(f'<div class="reaction">{emoji_html}<span>{reaction.count}</span></div>')
                    html_parts.append('</div>')
            except Exception:
                html_parts.append("<em>Could not fetch all reply info</em>")
            html_parts.append("</div>")

        if (is_reply or is_forward) and not referenced_message:
            html_parts.append('<div class="content"><em>[Could not fetch original message]</em></div>')
        else:
            html_content_text = process_text_for_html(content_source.content, content_source).replace("\n", "<br>")
            html_parts.append(f'<div class="content">{html_content_text if html_content_text.strip() else ""}</div>')
            if content_source.stickers:
                sticker_html_parts = []
                for sticker in content_source.stickers:
                    if sticker.url and sticker.url.endswith('.json'):
                        sticker_html_parts.append(f'<div class="sticker-unrenderable">Animated Sticker: {html.escape(sticker.name)}<br>(Cant View)</div>')
                    elif sticker.url:
                        sticker_html_parts.append(f'<img src="{sticker.url}" alt="Sticker: {sticker.name}" class="sticker" title="Sticker: {sticker.name}">')

                if sticker_html_parts:
                    html_parts.append('<div class="sticker-container">' + "".join(sticker_html_parts) + '</div>')

            _, html_embeds = process_embeds(content_source)
            if html_embeds:
                html_parts.append("".join(html_embeds))
            if content_source.attachments:
                html_parts.append('<div class="attachments"><strong>Attachments:</strong><br>')
                for att in content_source.attachments:
                    content_type = getattr(att, 'content_type', '').lower()
                    if content_type.startswith('image/'):
                        html_parts.append(f'<div class="attachment"><a href="{att.url}" target="_blank"><img src="{att.url}" alt="{att.filename}" style="max-width: 500px; border-radius: 5px;"></a></div>')
                    elif content_type.startswith('video/'):
                        html_parts.append(f'<div class="attachment"><video controls style="max-width: 500px;"><source src="{att.url}" type="{content_type}"></video><div><a href="{att.url}" target="_blank">{att.filename}</a></div></div>')
                    elif content_type.startswith('audio/'):
                        html_parts.append(f'<div class="attachment"><audio controls style="width: 100%;"><source src="{att.url}" type="{content_type}"></audio><div><a href="{att.url}" target="_blank">{att.filename}</a></div></div>')
                    else:
                        html_parts.append(f'<div class="attachment"><a href="{att.url}" target="_blank">{att.filename}</a></div>')
                html_parts.append("</div>")
            if content_source.reactions:
                html_parts.append('<div class="reactions-container">')
                for reaction in content_source.reactions:
                    emoji_html = get_emoji_html(reaction.emoji, is_reaction=True)
                    html_parts.append(f'<div class="reaction">{emoji_html}<span>{reaction.count}</span></div>')
                html_parts.append('</div>')

        html_parts.append("</div></div>")
        html_block = "".join(html_parts)
        
        return text_block, html_block

    # ---- Original Command Functions (Modified for UI) ----
    async def dump(ctx, channel, guild, create_html: bool = False, limit: int = None, attachments_only: bool = False, save_attachments: bool = False):
        if not channel or not guild or not hasattr(channel, 'history'):
            status_text.content = "Status: Invalid channel or server provided."
            dump_tab.toast(type="ERROR", title="Error", description="An invalid channel or server object was provided for dumping.")
            return

        folders = create_dump_folders()
        safe_server_name = fix_filename(guild.name)
        safe_channel_name = fix_filename(channel.name)
        
        server_base_folder = os.path.join(folders["servers"], f"{safe_server_name} ({guild.id})")
        channel_dumps_folder = os.path.join(server_base_folder, "Channel_Dumps")
        os.makedirs(channel_dumps_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{safe_channel_name}_{channel.id}_{timestamp}"
        log_file_path = os.path.join(channel_dumps_folder, f"{base_filename}.txt")
        
        log_file = open(log_file_path, "w", encoding="utf-8")
        
        header_text = (f"{'='*60}\nChat Dump\n{'='*60}\n"
                    f"Server    : {guild.name} (ID: {guild.id})\n"
                    f"Channel   : {channel.name} (ID: {channel.id})\n"
                    f"Timestamp : {datetime.now()}\n"
                    f"Filters   : Attachments Only = {attachments_only}, Attachment Type = {selected_attachment_filters}, Limit = {limit}, Save Attachments = {save_attachments}\n"
                    f"{'-'*60}\n\n")
        log_file.write(header_text)

        html_file = None
        if create_html:
            html_file_path = os.path.join(channel_dumps_folder, f"{base_filename}.html")
            html_header = build_html_header(title=f"Chat Dump - {channel.name}", guild_info=f"Server: {guild.name} (ID: {guild.id})", channel_info=f"Channel: {channel.name} (ID: {channel.id})")
            html_file = open(html_file_path, "w", encoding="utf-8")
            html_file.write(html_header)

        processed = 0
        dumped = 0

        messages_to_process = []
        limit_val = limit

        if limit_val:
            recent_messages = [msg async for msg in channel.history(limit=limit_val)]
            messages_to_process = recent_messages[::-1]
        else:
            messages_to_process = [msg async for msg in channel.history(limit=None, oldest_first=True)]

        for message in messages_to_process:
            processed += 1
            
            content_source = message.reference.resolved if (message.flags.forwarded and message.reference) else message
            if not content_source: content_source = message
            
            if attachments_only:
                if not content_source.attachments:
                    continue
                if selected_attachment_filters:
                    has_matching_attachment = False
                    for att in content_source.attachments:
                        if att.filename:
                            file_ext = os.path.splitext(att.filename.lower())[1][1:]
                            for a_filter in selected_attachment_filters:
                                if a_filter in TYPE_EXTENSIONS and file_ext in TYPE_EXTENSIONS[a_filter]:
                                    has_matching_attachment = True
                                    break
                            if has_matching_attachment:
                                break
                    if not has_matching_attachment:
                        continue
            
            dumped += 1
            text_block, html_block = await process_message_to_formats(message)
            log_file.write(text_block)

            if html_file:
                html_file.write(html_block)

        footer_text = (f"\n{'='*60}\nDump Complete\nTotal messages processed: {processed}\nTotal messages dumped   : {dumped}\n{'='*60}\n")
        log_file.write(footer_text)
        log_file.close()

        if html_file:
            html_file.write(build_html_footer(processed, dumped))
            html_file.close()

        base_path_no_ext = os.path.join(channel_dumps_folder, base_filename)
        save_last_dump_info("channel", base_path_no_ext)

        if create_html:
            dump_tab.toast(type="SUCCESS", title="Dump Complete", description="Text and HTML dumps saved successfully")
        else:
            dump_tab.toast(type="SUCCESS", title="Dump Complete", description="Text dump saved successfully")
        status_text.content = f"Status: Dump complete. Processed {processed} messages."

    # ---- DM Dump ----
    async def dmdump(ctx, user_id: int, create_html: bool = False, limit: int = None, attachments_only: bool = False, save_attachments: bool = False):
        try:
            user = await bot.fetch_user(user_id)
            if not user:
                status_text.content = "Status: User not found"
                dump_tab.toast(type="ERROR", title="Error", description="User not found")
                return
            dm_channel = user.dm_channel or await user.create_dm()
        except Exception as e:
            status_text.content = f"Status: Error opening DM channel: {e}"
            dump_tab.toast(type="ERROR", title="Error", description=f"Error opening DM channel: {e}")
            return

        folders = create_dump_folders()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        safe_username = fix_filename(user.display_name)
        
        user_folder = os.path.join(folders["dms"], f"{safe_username} ({user.id})")
        os.makedirs(user_folder, exist_ok=True)
            
        base_filename = f"{safe_username}_{user.id}_{timestamp}"
        log_file_path = os.path.join(user_folder, f"{base_filename}.txt")
        log_file = open(log_file_path, "w", encoding="utf-8")
        
        header_text = (f"{'='*60}\nDM Chat Dump\n{'='*60}\n"
            f"User      : {user} (ID: {user.id})\n"
            f"Timestamp : {datetime.now()}\n"
            f"Filters   : Attachments Only = {attachments_only}, Save Attachments = {save_attachments}\n"
            f"{'-'*60}\n\n")
        log_file.write(header_text)

        html_file = None
        if create_html:
            html_file_path = os.path.join(user_folder, f"{base_filename}.html")
            html_header = build_html_header(
                title=f"DM Chat Dump - {user.display_name}",
                guild_info=f"User: {user} (ID: {user.id})",
                channel_info="Direct Message"
            )
            html_file = open(html_file_path, "w", encoding="utf-8")
            html_file.write(html_header)
        
        processed = 0
        dumped = 0
        
        messages_to_process = []
        limit_val = limit

        if limit_val:
            recent_messages = [msg async for msg in dm_channel.history(limit=limit_val)]
            messages_to_process = recent_messages[::-1]
        else:
            messages_to_process = [msg async for msg in dm_channel.history(limit=None, oldest_first=True)]

        for message in messages_to_process:
            processed += 1
            
            content_source = message.reference.resolved if (message.flags.forwarded and message.reference) else message
            if not content_source: content_source = message

            if attachments_only:
                if not content_source.attachments:
                    continue
                if selected_attachment_filters:
                    has_matching_attachment = False
                    if att.filename:
                            file_ext = os.path.splitext(att.filename.lower())[1][1:]
                            for a_filter in selected_attachment_filters:
                                if a_filter in TYPE_EXTENSIONS and file_ext in TYPE_EXTENSIONS[a_filter]:
                                    has_matching_attachment = True
                                    break
                            if has_matching_attachment:
                                break
                    if not has_matching_attachment:
                        continue
            
            dumped += 1
            text_block, html_block = await process_message_to_formats(message)
            log_file.write(text_block)

            if html_file:
                html_file.write(html_block)

        footer_text = (f"\n{'='*60}\nDump Complete\nTotal messages processed: {processed}\nTotal messages dumped   : {dumped}\n{'='*60}\n")
        log_file.write(footer_text)
        log_file.close()

        if html_file:
            html_file.write(build_html_footer(processed, dumped))
            html_file.close()

        base_path_no_ext = os.path.join(user_folder, base_filename)
        save_last_dump_info("dm", base_path_no_ext)

        if create_html:
            dump_tab.toast(type="SUCCESS", title="DM Dump Complete", description="Text and HTML dumps saved successfully")
        else:
            dump_tab.toast(type="SUCCESS", title="DM Dump Complete", description="Text dump saved successfully")
        
        status_text.content = f"Status: DM Dump complete. Processed {processed} messages."

    # ---- Group Chat Dump ----
    async def groupdump(ctx, group_id: int, create_html: bool = False, limit: int = None, attachments_only: bool = False, save_attachments: bool = False):
        try:
            channel = await bot.fetch_channel(group_id)
            if not hasattr(channel, 'recipients'):
                status_text.content = "Status: ID does not belong to a group chat."
                return
        except Exception as e:
            status_text.content = f"Status: Error fetching group chat: {e}"
            return

        folders = create_dump_folders()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        group_name = channel.name if channel.name else f"Group_{channel.id}"
        safe_group_name = fix_filename(group_name)
        
        group_folder = os.path.join(folders["groups"], f"{safe_group_name} ({channel.id})")
        os.makedirs(group_folder, exist_ok=True)
        
        base_filename = f"{safe_group_name}_{channel.id}_{timestamp}"
        log_file_path = os.path.join(group_folder, f"{base_filename}.txt")
        log_file = open(log_file_path, "w", encoding="utf-8")
            
        recipients_str = ", ".join([f"{user.display_name}" for user in channel.recipients])
        header_text = (f"{'='*60}\nGroup Chat Dump\n{'='*60}\n"
            f"Group     : {group_name} (ID: {channel.id})\n"
            f"Members   : {recipients_str}\n"
            f"Timestamp : {datetime.now()}\n"
            f"{'-'*60}\n\n")
        log_file.write(header_text)

        html_file = None
        if create_html:
            html_file_path = os.path.join(group_folder, f"{base_filename}.html")
            html_header = build_html_header(
                title=f"Group Chat Dump - {group_name}",
                guild_info=f"Group ID: {channel.id}",
                channel_info=f"Members: {recipients_str}"
            )
            html_file = open(html_file_path, "w", encoding="utf-8")
            html_file.write(html_header)
        
        processed, dumped = 0, 0
        
        messages_to_process = []
        limit_val = limit

        if limit_val:
            recent_messages = [msg async for msg in channel.history(limit=limit_val)]
            messages_to_process = recent_messages[::-1]
        else:
            messages_to_process = [msg async for msg in channel.history(limit=None, oldest_first=True)]

        for message in messages_to_process:
            processed += 1
            
            content_source = message.reference.resolved if (message.flags.forwarded and message.reference) else message
            if not content_source: content_source = message

            if attachments_only:
                if not content_source.attachments: continue
                if selected_attachment_filters:
                    has_matching_attachment = False
                    if att.filename:
                            file_ext = os.path.splitext(att.filename.lower())[1][1:]
                            for a_filter in selected_attachment_filters:
                                if a_filter in TYPE_EXTENSIONS and file_ext in TYPE_EXTENSIONS[a_filter]:
                                    has_matching_attachment = True
                                    break
                            if has_matching_attachment: break
                    if not has_matching_attachment: continue
            
            dumped += 1
            text_block, html_block = await process_message_to_formats(message)
            log_file.write(text_block)
            
            if html_file:
                html_file.write(html_block)

        log_file.close()

        if html_file:
            html_file.write(build_html_footer(processed, dumped))
            html_file.close()

        base_path_no_ext = os.path.join(group_folder, base_filename)
        save_last_dump_info("group", base_path_no_ext)
        
        status_text.content = "Group dump complete."
        dump_tab.toast(type="SUCCESS", title="Group Dump Complete", description="Dump saved successfully.")

    # ---- Dump for Servers ----
    async def serverdump(ctx, server_id: int, limit: int = None, attachments_only: bool = False, save_attachments: bool = False, create_html: bool = False):
        guild = bot.get_guild(server_id)
        if not guild:
            status_text.content = "Status: Server not found"
            dump_tab.toast(type="ERROR", title="Error", description="Server not found")
            return

        safe_ui_server_name = guild.name.replace('\\', '\\\\').replace("'", "\\'")
        folders = create_dump_folders()
        safe_server_name = fix_filename(guild.name)

        server_base_folder = os.path.join(folders["servers"], f"{safe_server_name} ({guild.id})")
        os.makedirs(server_base_folder, exist_ok=True)
        
        full_dumps_folder = os.path.join(server_base_folder, "Full_Server_Dumps")
        os.makedirs(full_dumps_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        server_dump_folder = os.path.join(full_dumps_folder, f"{safe_server_name}_{guild.id}_{timestamp}")
        os.makedirs(server_dump_folder, exist_ok=True)
        
        create_server_metadata_file(guild, server_dump_folder)
        
        failed_dumps_folder = os.path.join(server_dump_folder, "FAILED DUMPS")
        
        status_text.content = f"Dumping server {safe_ui_server_name}... this may take a while."
        
        category_folders = {}
        for category in guild.categories:
            safe_category_name = fix_filename(f"{category.position:02d}_{category.name}")
            category_path = os.path.join(server_dump_folder, safe_category_name)
            os.makedirs(category_path, exist_ok=True)
            category_folders[category.id] = category_path
            
        no_category_folder = os.path.join(server_dump_folder, "_Uncategorized")
        os.makedirs(no_category_folder, exist_ok=True)

        for channel in sorted(guild.text_channels, key=lambda c: c.position):
            if not channel.permissions_for(guild.me).read_messages:
                log_failed_channel(failed_dumps_folder, channel, "No permissions or not a text channel.")
                continue
                
            safe_ui_channel_name = channel.name.replace('\\', '\\\\').replace("'", "\\'")
            status_text.content = f"Dumping channel: #{safe_ui_channel_name}"
            
            channel_folder = category_folders.get(channel.category_id, no_category_folder)
            
            try:
                log_file_path = os.path.join(channel_folder, f"#{fix_filename(channel.name)}.txt")
                log_file = open(log_file_path, "w", encoding="utf-8")
                log_file.write(f"--- DUMP OF CHANNEL: #{channel.name} (ID: {channel.id}) ---\n\n")

                html_file = None
                if create_html:
                    html_file_path = os.path.join(channel_folder, f"#{fix_filename(channel.name)}.html")
                    html_header = build_html_header(
                        title=f"Chat Dump - {channel.name}",
                        guild_info=f"Server: {guild.name} (ID: {guild.id})",
                        channel_info=f"Channel: {channel.name} (ID: {channel.id})"
                    )
                    html_file = open(html_file_path, "w", encoding="utf-8")
                    html_file.write(html_header)

                processed_count, dumped_count = 0, 0
                
                messages_to_process = []
                limit_val = limit
                
                if limit_val:
                    recent_messages = [msg async for msg in channel.history(limit=limit_val)]
                    messages_to_process = recent_messages[::-1]
                else:
                    messages_to_process = [msg async for msg in channel.history(limit=None, oldest_first=True)]

                for message in messages_to_process:
                    processed_count += 1
                    
                    content_source = message.reference.resolved if (message.flags.forwarded and message.reference) else message
                    if not content_source: content_source = message

                    if attachments_only:
                        if not content_source.attachments: continue
                        if selected_attachment_filters:
                            has_matching_attachment = False
                            for att in content_source.attachments:
                                if att.filename:
                                    file_ext = os.path.splitext(att.filename.lower())[1][1:]
                                    for a_filter in selected_attachment_filters:
                                        if a_filter in TYPE_EXTENSIONS and file_ext in TYPE_EXTENSIONS[a_filter]:
                                            has_matching_attachment = True
                                            break
                                    if has_matching_attachment: break
                            if not has_matching_attachment: continue
                    
                    dumped_count += 1
                    text_block, html_block = await process_message_to_formats(message, is_server_dump_format=True)
                    log_file.write(text_block)

                    if html_file:
                        html_file.write(html_block)

                log_file.close()

                if html_file:
                    html_file.write(build_html_footer(processed_count, dumped_count))
                    html_file.close()

            except Exception as e:
                reason = f"An unexpected error occurred: {str(e)}"
                log_failed_channel(failed_dumps_folder, channel, reason)
                if 'log_file' in locals() and not log_file.closed: log_file.close()
                if 'html_file' in locals() and html_file and not html_file.closed: html_file.close()
                continue 
                
        save_last_dump_info("server", server_dump_folder)
        status_text.content = "Server dump complete."
        dump_tab.toast(type="SUCCESS", title="Server Dump Complete", description=f"All accessible channels from {safe_ui_server_name} have been dumped.")

    dump_tab.render()
dump()