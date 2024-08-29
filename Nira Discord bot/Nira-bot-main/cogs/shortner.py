import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
from urllib.parse import urlparse
import qrcode
import io
import time
import aiohttp


# Retrieve the Bitly API token from environment variables
BITLY_TOKEN = os.getenv("BITLY_API")

# In-memory storage for user rate limits (user_id -> (last_reset_time, count))
user_rate_limits = {}
RATE_LIMIT = 5  # Max number of URL shortenings per user within the reset interval
RESET_INTERVAL = 60 * 60  # Reset interval in seconds (e.g., 1 hour)


class URLShortener(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    @app_commands.command(
        name="shorten",
        description=
        "Shorten any valid URL using the Bitly API. Optionally generate a QR code and set an expiration time."
    )
    @app_commands.describe(
        url="The URL to shorten",
        generate_qr="Generate a QR code for the shortened URL (true/false)",
        expire_days=
        "Number of days after which the shortened URL will expire (default is no expiry)"
    )
    async def shorten(self,
                      interaction: discord.Interaction,
                      url: str,
                      generate_qr: bool = False,
                      expire_days: int = None):
        """Handles the /shorten command to shorten a given URL."""
        user_id = interaction.user.id

        if not self.is_within_rate_limit(user_id):
            await interaction.response.send_message(
                "You have reached the rate limit. Please try again later.")
            return

        if self.is_already_shortened(url):
            await interaction.response.send_message(
                "Cannot shorten an already shortened URL.")
            return

        shortened_url = self.shorten_url(url, expire_days)
        if shortened_url:
            formatted_url = self.format_shortened_url(shortened_url)
            if generate_qr:
                qr_image = self.generate_qr_code(shortened_url)
                file = discord.File(qr_image, filename="qrcode.png")
                await interaction.response.send_message(
                    content=f"Here is your shortened URL: {formatted_url}",
                    file=file)
            else:
                await interaction.response.send_message(
                    f"Here is your shortened URL: {formatted_url}")
        else:
            await interaction.response.send_message(
                "Failed to shorten the URL. Please ensure it's a valid URL and try again."
            )

    @staticmethod
    def is_already_shortened(url: str) -> bool:
        """Checks if the URL is already a shortened Bitly URL."""
        parsed_url = urlparse(url)
        return parsed_url.netloc in ["bit.ly", "j.mp",
                                     "bitly.is"]  # Common Bitly domains

    @staticmethod
    def shorten_url(url: str, expire_days: int = None) -> str:
        """Shortens the provided URL using the Bitly API with an optional expiration time."""
        headers = {
            "Authorization": f"Bearer {BITLY_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "long_url": url,
            "domain":
            "bit.ly"  # Ensures that the shortened URL uses the bit.ly domain
        }
        if expire_days:
            data["expires_at"] = (time.time() + expire_days * 86400
                                  )  # Convert days to seconds

        try:
            response = requests.post("https://api-ssl.bitly.com/v4/shorten",
                                     json=data,
                                     headers=headers)
            response.raise_for_status()
            return response.json().get("link")
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")  # Logs the error for debugging
            return None

    @staticmethod
    def format_shortened_url(url: str) -> str:
        """Formats the shortened URL to make it look more professional."""
        return f"<{url}>"  # Surround the URL with angle brackets for cleaner display

    @staticmethod
    def generate_qr_code(url: str) -> io.BytesIO:
        """Generates a QR code for the given URL."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf

    def is_within_rate_limit(self, user_id: int) -> bool:
        """Checks if a user is within the rate limit."""
        current_time = time.time()
        if user_id in user_rate_limits:
            last_reset_time, count = user_rate_limits[user_id]
            if current_time - last_reset_time < RESET_INTERVAL:
                if count >= RATE_LIMIT:
                    return False
                user_rate_limits[user_id] = (last_reset_time, count + 1)
            else:
                user_rate_limits[user_id] = (current_time, 1)
        else:
            user_rate_limits[user_id] = (current_time, 1)
        return True


async def setup(bot: commands.Bot) -> None:
    """Registers the URLShortener cog with the bot."""
    await bot.add_cog(URLShortener(bot))
