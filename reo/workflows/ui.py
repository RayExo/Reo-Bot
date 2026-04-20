from PIL import Image, ImageDraw, ImageFont
import datetime
import requests
from io import BytesIO
from pathlib import Path
import time

from reo.console.logging import logger

REO_DIR = Path(__file__).resolve().parents[1]
STYLE_DIR = REO_DIR / "style"
FONTS_DIR = REO_DIR / "fonts"

def get_ui_profile(
        avatar_url: str = None,
        banner_url: str = None,
        display_name: str = None,
        username: str = None,
        userid: str = None,
        coin: int = None,
        created_at: datetime.datetime = None,
        badges: list = []
    ):
    template_image = Image.open(STYLE_DIR / "templates" / "profile_template.png").convert("RGBA")
    icon_frame = Image.open(STYLE_DIR / "templates" / "icon_frame.png").convert("RGBA")
    coin_image = Image.open(STYLE_DIR / "templates" / "coin.png").convert("RGBA")

    # Get the avatar image from the URL and open by Image.open get image and ?size=512 to get the image in 512x512
    params = {"size": 512}
    avatar_image = Image.open(requests.get(avatar_url, stream=True, params=params).raw).convert("RGBA")
    if banner_url:
        banner_image = Image.open(requests.get(banner_url, stream=True, params=params).raw).convert("RGBA")
    else:
        banner_image = Image.new("RGBA", (680, 240), (0, 0, 0, 255))

    # Resize the banner image without distortion
    banner_image = banner_image.resize((680, 240))
    template_image.paste(banner_image, (0, 0), banner_image)




    # Make avatar image circular
    avatar_image = avatar_image.resize((200, 200))

    mask = Image.new('L', (200, 200), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + (200, 200), fill=256)

    # Apply the mask to the avatar image
    avatar_image.putalpha(mask)

    # Create a new image for the combined result
    combined_image = template_image.copy()

    # Paste the avatar onto the combined image
    avatar_position = (40, 150)
    combined_image.paste(avatar_image, avatar_position, avatar_image)

    # Add the icon frame
    icon_frame = icon_frame.resize((200, 200))
    combined_image.paste(icon_frame, avatar_position, icon_frame)



    if len(display_name) > 30:
        display_name = display_name[:30] + ".."

    # Add the display name
    display_name_x = 34
    display_name_y = 365
    display_name_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 35)
    display_name_color = (255, 255, 255)
    draw = ImageDraw.Draw(combined_image)
    draw.text((display_name_x, display_name_y), display_name, display_name_color, font=display_name_font)


    if len(username) > 18:
        username = username[:18] + ".."
    # Add the username
    username_x = 34
    username_y = 410
    username_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 25)
    username_color = (255, 255, 255)
    draw.text((username_x, username_y), username, username_color, font=username_font)

    
    if len(userid) > 20:
        userid = userid[:20] + ".."
    # get the x position of the userid 
    # Add the userid in the right side of username

    userid_x = 34
    userid_y = 445
    userid_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 20)
    userid_color = (255, 255, 255)
    draw.text((userid_x, userid_y), userid, userid_color, font=userid_font)


    def format_balance(balance):
        balance = float(balance)
        suffixes = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No']
        magnitude = 0
        
        while abs(balance) >= 1000 and magnitude < len(suffixes) - 1:
            magnitude += 1
            balance /= 1000.0
        
        return f'{balance:.1f}{suffixes[magnitude]}'
    
    coin = format_balance(coin)

    coin_text = f"{coin}"
    # Calculate coin text bounding box
    coin_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 20)
    coin_bbox = draw.textbbox((0, 0), coin_text, font=coin_font)

    # Extract width and height from the bounding box
    coin_width = coin_bbox[2] - coin_bbox[0]
    coin_height = coin_bbox[3] - coin_bbox[1]
    image_width = combined_image.width

    # Position the coin text from the right side of the image
    coin_x = image_width - coin_width - 80
    coin_y = 429
    coin_color = (255, 215, 0)

    # Draw the coin text on the image
    draw.text((coin_x, coin_y), coin_text, coin_color, font=coin_font)


    # in the right side of the coin text image of name coin.png
    
    coin_image = coin_image.resize((25, 25))
    coin_image_x = image_width - coin_image.width - 50
    combined_image.paste(coin_image, (coin_image_x, 428), coin_image)
    



    # set UTC the created_at
    created_at_text = f"Created At: {created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"

    created_at_x = 60
    created_at_y = 790
    created_at_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 30)
    created_at_color = (255, 255, 255)
    draw.text((created_at_x, created_at_y), created_at_text, created_at_color, font=created_at_font)



    
    if len(badges) > 7:
        badges = badges[:7]
    badges_images = [Image.open(STYLE_DIR / "badges" / f"{badge}.png").convert("RGBA").resize((50,50)) for badge in badges]
    combined_badges = Image.new("RGBA", (50*len(badges), 50), (255, 255, 255, 0))
    for i, badge in enumerate(badges_images):
        combined_badges.paste(badge, (i*50, 0), badge)
    combined_image.paste(combined_badges, (278, 273), combined_badges)

    byte = BytesIO()
    combined_image.save(byte, format="PNG")
    byte.seek(0)

    return byte

from PIL import Image, ImageDraw, ImageFont

    # # Load the background image
    # background_image_path = 'background.jpg'  # Replace with your background image path
    # background = Image.open(background_image_path)


def create_ping_table(bot_ping, db_ping, cache_ping):
    try:
        start_time = time.time()
        # create background black 
        background = Image.new('RGB', (500, 500), (0, 0, 0))

        # Define dimensions and padding
        padding = 10
        row_height = 40
        header_height = row_height  # Top row height
        column_count = 3  # Number of columns
        column_width = 200  # Column width

        # Calculate total table width and height
        table_width = column_count * column_width
        table_height = 2 * row_height  # Two rows: headers and values
        image_width = table_width + 2 * padding
        image_height = table_height + 2 * padding

        # Resize background image to fit the new dimensions
        background = background.resize((image_width, image_height))  # Resize to fit table size with padding

        # Create a drawing context on the resized background image
        draw = ImageDraw.Draw(background)

        # Load fonts
        try:
            text_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 24)  # Bold font
        except IOError:
            text_font = ImageFont.load_default()

        # Define the metrics
        columns = ["Bot Ping", "Storage Ping", "Cache Ping"]
        values = [f"{bot_ping} ms", f"{db_ping} ms", f"{cache_ping} ms"]

        # Ping color ranges
        def get_ping_color(ping_value):
            try:
                ping = int(float(ping_value.split()[0]))  # Extract the integer value from the string
            except ValueError as e:
                logger.error(f"Error converting ping value to integer: {e}")
                return (255, 255, 255)  # White for invalid ping

            if ping < 50:
                return (0, 255, 0)  # Green for low ping
            elif ping < 100:
                return (255, 255, 0)  # Yellow for moderate ping
            elif ping < 150:
                return (255, 165, 0)  # Orange for high ping
            else:
                return (255, 0, 0)  # Red for very high ping

        # Colors
        border_color = (255, 255, 255)  # White border

        # Calculate the table position
        table_left = padding
        table_top = padding
        table_width = column_count * column_width
        table_height = 2 * row_height

        # Draw the table headers with borders
        for i, column in enumerate(columns):
            x = table_left + i * column_width
            y = table_top
            # Draw borders
            draw.line([(x, y), (x + column_width, y)], fill=border_color, width=3)  # Top border
            draw.line([(x + column_width, y), (x + column_width, y + header_height)], fill=border_color, width=3)  # Right border
            draw.line([(x, y), (x, y + header_height)], fill=border_color, width=3)  # Left border
            # Calculate text size and position for centering
            bbox = draw.textbbox((x, y), column, font=text_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x + (column_width - text_width) / 2
            text_y = y + (header_height - text_height) / 2
            draw.text((text_x, text_y), column, fill=border_color, font=text_font)  # Text

        # Draw the table values with borders
        for i, value in enumerate(values):
            x = table_left + i * column_width
            y = table_top + header_height
            # Get color based on the ping value
            text_color = get_ping_color(value)
            # Draw borders
            draw.line([(x, y), (x + column_width, y)], fill=border_color, width=3)  # Bottom border
            draw.line([(x + column_width, y), (x + column_width, y + row_height)], fill=border_color, width=3)  # Right border
            draw.line([(x, y), (x, y + row_height)], fill=border_color, width=3)  # Left border
            # Calculate text size and position for centering
            bbox = draw.textbbox((x, y), value, font=text_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x + (column_width - text_width) / 2
            text_y = y + (row_height - text_height) / 2
            draw.text((text_x, text_y), value, fill=text_color, font=text_font)  # Text

        # Draw the bottom border of the last row
        draw.line([(table_left, table_top + header_height + row_height), (table_left + table_width, table_top + header_height + row_height)], fill=border_color, width=3)  # Bottom border

        # Draw the left border of the entire table
        draw.line([(table_left, table_top), (table_left, table_top + table_height)], fill=border_color, width=3)  # Left border

        byte = BytesIO()
        background.save(byte, format="PNG")
        byte.seek(0)
        #time in ms
        logger.info(f"Time taken: {round(time.time() - start_time, 2)} seconds to create the ping table image")
        return byte
    except Exception as e:
        logger.error(f"Error creating ping table: {e}")
        return None

def create_relation_percentage_banner(
    user1_avatar_url: str,
    user2_avatar_url: str,
    percentage: int
):
    def get_image(url):
        # Modify the URL to ensure size=128
        url = url.replace("?size=1024", "?size=128") if "?size=1024" in url else url + "?size=128"
        # Download the image and convert to RGB
        return Image.open(requests.get(url, stream=True).raw).convert("RGBA")

    user1_avatar = get_image(user1_avatar_url)
    user2_avatar = get_image(user2_avatar_url)

    # Load background and convert to RGBA mode to handle transparency
    background_image = Image.open(STYLE_DIR / "templates" / "relationship_percentage_background.gif").convert("RGBA")

    # Resize the avatars
    user1_avatar = user1_avatar.resize((100, 100))
    user2_avatar = user2_avatar.resize((100, 100))

    # Calculate positions for the avatars
    user1x = 50
    user2x = background_image.size[0] - 50 - user2_avatar.size[0]

    # Calculate the height for the avatars
    avatar_height = (background_image.size[1] - user1_avatar.size[1]) // 2

    # Paste the avatars onto the background image using their alpha channel as the mask
    background_image.paste(user1_avatar, (user1x, avatar_height), user1_avatar)
    background_image.paste(user2_avatar, (user2x, avatar_height), user2_avatar)

    # Choose the heart image (broken or full heart)
    heart_image = (
        Image.open(STYLE_DIR / "templates" / "heart.png").convert("RGBA")
        if percentage > 50
        else Image.open(STYLE_DIR / "templates" / "broken_heart.png").convert("RGBA")
    )
    heart_image = heart_image.resize((150, 150))

    # Calculate the position for the heart image
    heartx = (background_image.size[0] - heart_image.size[0]) // 2
    hearty = (background_image.size[1] - heart_image.size[1]) // 2

    # Paste the heart image with transparency onto the background image
    background_image.paste(heart_image, (heartx, hearty), heart_image)

    # Prepare the text
    width, height = background_image.size
    text = f"{percentage}%"
    font = ImageFont.truetype(str(FONTS_DIR / "ProtestGuerrilla-Regular.ttf"), 50)

    # Get text size
    bbox = font.getbbox(text)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Calculate text position
    x = (width - text_width) // 2
    y = height // 2 - text_height

    # Draw text on the image
    draw = ImageDraw.Draw(background_image)
    color = (255, 255, 255)  # White color
    draw.text((x, y), text, fill=color, font=font)

    byte = BytesIO()
    background_image.save(byte, format="PNG")
    byte.seek(0)
    return byte



def convert_ms_to_beautiful_time(ms: int) -> str:
    """Convert milliseconds to a human-readable time format."""
    try:
        seconds = ms // 1000
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        months, weeks = divmod(weeks, 4)

        time_parts = []
        if months: time_parts.append(f"{months}M")
        if weeks: time_parts.append(f"{weeks}W")
        if days: time_parts.append(f"{days}D")
        if hours: time_parts.append(f"{hours}h")
        if minutes: time_parts.append(f"{minutes}m")
        if seconds: time_parts.append(f"{seconds}s")

        return ' '.join(time_parts) or "0s"
    except Exception as e:
        return "Unknown"

def load_image_from_url(url: str) -> Image.Image:
    """Load an image from a URL and convert it to RGBA."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses
        return Image.open(response.raw).convert("RGBA")
    except Exception as e:
        print(f"Error loading image: {e}")
        return Image.new("RGBA", (200, 200), (255, 255, 255, 0))  # Placeholder image on error

def draw_rounded_rectangle(draw: ImageDraw.Draw, box: tuple, radius: int, color: tuple):
    """Draw a rounded rectangle on the provided draw object."""
    draw.rounded_rectangle(box, radius=radius, fill=color)

def load_image_from_url(url: str) -> Image.Image:
    """Load an image from a URL and convert it to RGBA."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses
        return Image.open(response.raw).convert("RGBA")
    except Exception as e:
        print(f"Error loading image: {e}")
        return Image.new("RGBA", (200, 200), (255, 255, 255, 0))  # Placeholder image on error

def draw_rounded_rectangle(draw: ImageDraw.Draw, box: tuple, radius: int, color: tuple):
    """Draw a rounded rectangle on the provided draw object."""
    draw.rounded_rectangle(box, radius=radius, fill=color)

def create_simple_music_banner(
    music_thumbnail_url: str,
    music_title: str,
    music_author: str,
    music_duration: int,
    current_position: int
):
    try:
        from PIL import ImageFilter

        width, height = 1200, 300

        def fit_text(drawer, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
            text = text or 'Unknown'
            if drawer.textlength(text, font=font) <= max_width:
                return text
            while len(text) > 1 and drawer.textlength(f"{text}...", font=font) > max_width:
                text = text[:-1]
            return f"{text}..."

        raw_thumb = load_image_from_url(music_thumbnail_url)
        background = raw_thumb.resize((width, height), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=25))
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 200))
        combined_image = Image.alpha_composite(background, overlay)
        draw = ImageDraw.Draw(combined_image)

        art_size = 200
        art_x, art_y = 50, 50
        
        artwork = raw_thumb.resize((art_size, art_size), Image.LANCZOS)
        mask = Image.new('L', (art_size, art_size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, art_size, art_size], radius=15, fill=255)
        combined_image.paste(artwork, (art_x, art_y), mask=mask)

        try:
            title_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 36)
            artist_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 24)
            time_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 20)
        except Exception:
            title_font = ImageFont.load_default()
            artist_font = ImageFont.load_default()
            time_font = ImageFont.load_default()

        info_x = art_x + art_size + 40
        max_text_width = width - info_x - 50
        draw.text((info_x, 60), fit_text(draw, music_title, title_font, max_text_width), fill=(255, 255, 255, 255), font=title_font)
        draw.text((info_x, 110), fit_text(draw, music_author, artist_font, max_text_width), fill=(180, 180, 180, 255), font=artist_font)

        bar_x = info_x
        bar_y = 160
        bar_width = max_text_width
        bar_height = 12
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], radius=6, fill=(255, 255, 255, 40))

        progress_ratio = max(0.0, min(1.0, (current_position / music_duration) if music_duration > 0 else 0.0))
        progress_width = int(bar_width * progress_ratio)
        if progress_width > 0:
            draw.rounded_rectangle([bar_x, bar_y, bar_x + progress_width, bar_y + bar_height], radius=6, fill=(255, 255, 255, 255))

        current_time = convert_ms_to_beautiful_time(max(current_position, 0))
        total_time = convert_ms_to_beautiful_time(max(music_duration, 0))
        draw.text((bar_x, bar_y + 28), current_time, fill=(200, 200, 200, 255), font=time_font)
        total_width = int(draw.textlength(total_time, font=time_font))
        draw.text((bar_x + bar_width - total_width, bar_y + 28), total_time, fill=(200, 200, 200, 255), font=time_font)

        byte = BytesIO()
        combined_image.save(byte, format='PNG')
        byte.seek(0)
        return byte

    except Exception as e:
        logger.error(f'Error creating simple music banner: {e}')
        return None


def create_music_controller_image(
    music_thumbnail_url: str,
    music_title: str,
    music_author: str,
    music_album: str,
    music_duration: int,
    current_position: int,
    volume: int,
    queue_size: int = 0,
    is_paused: bool = False,
    autoplay_enabled: bool = False,
    loop_enabled: bool = False
):
    return create_simple_music_banner(
        music_thumbnail_url=music_thumbnail_url,
        music_title=music_title,
        music_author=music_author,
        music_duration=music_duration,
        current_position=current_position
    )
