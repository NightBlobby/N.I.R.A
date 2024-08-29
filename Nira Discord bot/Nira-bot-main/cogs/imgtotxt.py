import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
from io import BytesIO
from PIL import Image
from typing import Optional, List


class OCRService:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = "https://api.ocr.space/parse/image"

    async def extract_text(self, image_data: bytes) -> dict:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('apikey', self.api_key)
            data.add_field('language', 'eng')
            data.add_field('file',
                           image_data,
                           filename='image.jpg',
                           content_type='image/jpeg')
            data.add_field('detectOrientation', 'true')
            data.add_field('scale', 'true')
            data.add_field('isTable', 'false')
            data.add_field('OCREngine',
                           '2')  # Using the more advanced OCR engine

            async with session.post(self.url, data=data) as response:
                return await response.json()


class GoToPageModal(discord.ui.Modal, title="Go to Page"):
    page_number = discord.ui.TextInput(label="Page Number",
                                       style=discord.TextStyle.short,
                                       placeholder="Enter the page number",
                                       required=True)

    def __init__(self, paginator):
        super().__init__()
        self.paginator = paginator

    async def on_submit(self, interaction: discord.Interaction):
        try:
            page_number = int(self.page_number.value) - 1
            if 0 <= page_number < len(self.paginator.pages):
                self.paginator.current_page = page_number
                await self.paginator.update_embed(interaction)
            else:
                await interaction.response.send_message("Invalid page number.",
                                                        ephemeral=True)
        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid number.", ephemeral=True)


class Paginator(discord.ui.View):

    def __init__(self, interaction: discord.Interaction, pages: List[str],
                 image_url: str):
        super().__init__(timeout=30)  # Timeout after 30 seconds of inactivity
        self.interaction = interaction
        self.pages = pages
        self.image_url = image_url
        self.current_page = 0
        self.message = None
        

    async def update_embed(self,
                           interaction: discord.Interaction,
                           initial: bool = False):
        embed = discord.Embed(title="Image Text Recognition",
                              color=discord.Color.blue())
        embed.set_thumbnail(url=self.image_url)
        embed.add_field(
            name=
            f"Detected Text (Page {self.current_page + 1}/{len(self.pages)})",
            value=self.pages[self.current_page],
            inline=False)

        if initial:
            self.message = await interaction.followup.send(embed=embed,
                                                           view=self)
        else:
            await self.message.edit(embed=embed, view=self)

    @discord.ui.button(label="Prev", style=discord.ButtonStyle.primary)
    async def prev_page(self, button: discord.ui.Button,
                        interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_embed(interaction)
        else:
            await interaction.response.send_message(
                "You're already on the first page.", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_page(self, button: discord.ui.Button,
                        interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.update_embed(interaction)
        else:
            await interaction.response.send_message(
                "You're already on the last page.", ephemeral=True)

    @discord.ui.button(label="Go to", style=discord.ButtonStyle.secondary)
    async def go_to_page(self, button: discord.ui.Button,
                         interaction: discord.Interaction):
        await interaction.response.send_modal(GoToPageModal(self))

    async def on_timeout(self):
        if self.message:
            await self.message.edit(view=None)


class ImageRecognition(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ocr_service = OCRService(os.environ["ITT_KEY"])
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    @app_commands.command(
        name="identify",
        description="Identify text from an image or image URL")
    @app_commands.describe(
        image="Upload an image or provide an image URL",
        url="URL of the image (optional if image is uploaded)")
    async def identify(self,
                       interaction: discord.Interaction,
                       image: Optional[discord.Attachment] = None,
                       url: Optional[str] = None):
        if not image and not url:
            await interaction.response.send_message(
                "Please provide either an image or an image URL.")
            return

        await interaction.response.defer()

        try:
            image_data = await self.get_image_data(image, url)
            result = await self.ocr_service.extract_text(image_data)

            if result.get('IsErroredOnProcessing'):
                error_message = result.get('ErrorMessage', 'Unknown error')
                await interaction.followup.send(
                    f"There was an error processing the image: {error_message}"
                )
                return

            parsed_results = result.get("ParsedResults", [])
            if not parsed_results:
                await interaction.followup.send(
                    "No text could be extracted from the image. Please ensure the image is clear and contains readable text."
                )
                return

            text_detected = parsed_results[0].get("ParsedText", "").strip()
            if not text_detected:
                await interaction.followup.send(
                    "No text was detected in the image. Please try with a different image or ensure the text is clearly visible."
                )
                return

            pages = self.format_text(text_detected)

            if len(pages) > 1:
                paginator = Paginator(interaction, pages,
                                      image.url if image else url)
                await paginator.update_embed(interaction, initial=True)
            else:
                await interaction.followup.send(embed=discord.Embed(
                    title="Image Text Recognition",
                    description=pages[0],
                    color=discord.Color.blue()).set_thumbnail(
                        url=image.url if image else url))
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")
            import traceback
            print(f"Exception occurred: {traceback.format_exc()}")

    async def get_image_data(self, attachment: Optional[discord.Attachment],
                             url: Optional[str]) -> bytes:
        if attachment:
            return await self.process_image(await attachment.read())
        elif url:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise ValueError(
                            f"Failed to fetch image from URL. Status code: {response.status}"
                        )
                    return await self.process_image(await response.read())

    async def process_image(self, image_data: bytes) -> bytes:
        with Image.open(BytesIO(image_data)) as img:
            if img.format not in ['JPEG', 'PNG']:
                buffer = BytesIO()
                img = img.convert('RGB')
                img.save(buffer, format="JPEG", quality=95)
                return buffer.getvalue()
        return image_data

    @staticmethod
    def format_text(text: str) -> List[str]:
        """
        Formats the text to ensure proper spacing, indentation, and readability.
        Splits the text into chunks if it exceeds Discord's character limits per field.
        """
        max_field_length = 1024  # Discord's character limit for a field value
        lines = text.splitlines()
        formatted_chunks = []
        current_chunk = ""

        for line in lines:
            stripped_line = line.rstrip()  # Keep the original line spacing
            if len(current_chunk) + len(
                    stripped_line
            ) + 1 > max_field_length:  # +1 for the newline
                formatted_chunks.append(f"```\n{current_chunk.strip()}```")
                current_chunk = stripped_line + '\n'
            else:
                current_chunk += stripped_line + '\n'

        if current_chunk.strip():  # Add the last chunk if it exists
            formatted_chunks.append(f"```\n{current_chunk.strip()}```")

        return formatted_chunks


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ImageRecognition(bot))
