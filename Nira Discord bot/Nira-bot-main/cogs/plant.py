import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import os
import asyncio
from discord.app_commands import Choice
from collections import defaultdict
import time
from PIL import Image
import io


class PlantView(discord.ui.View):

    def __init__(self, pages):
        super().__init__(timeout=60)
        self.pages = pages
        self.current_page = 0
        self.last_interaction = asyncio.get_event_loop().time()

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        self.last_interaction = asyncio.get_event_loop().time()
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_button(self, interaction: discord.Interaction,
                              button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(
                embed=self.pages[self.current_page], view=self)
        else:
            await interaction.response.send_message(
                "You're already on the first page!", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.success)
    async def next_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(
                embed=self.pages[self.current_page], view=self)
        else:
            await interaction.response.send_message("No more pages left!",
                                                    ephemeral=True)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)


class PlantIdentifier(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api_key = os.environ["PLANTNET_API_KEY"]
        self.api_url = "https://my-api.plantnet.org/v2/identify/all"
        self.cooldowns = defaultdict(lambda: 0)
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    async def cooldown_check(self, interaction: discord.Interaction) -> bool:
        current_time = time.time()
        if current_time - self.cooldowns[(interaction.guild_id,
                                          interaction.user.id)] < 5:
            return False
        self.cooldowns[(interaction.guild_id,
                        interaction.user.id)] = current_time
        return True

    @app_commands.command(name="plant",
                          description="Identify a plant from an image")
    @app_commands.describe(
        image="Upload an image of the plant",
        image_url="Or provide a URL to an image of the plant",
        language="Select the language for plant information (default: English)"
    )
    @app_commands.choices(language=[
        Choice(name="English", value="en"),
        Choice(name="French", value="fr"),
        Choice(name="German", value="de"),
        Choice(name="Spanish", value="es")
    ])
    async def identify_plant(self,
                             interaction: discord.Interaction,
                             image: discord.Attachment = None,
                             image_url: str = None,
                             language: str = "en"):
        if not await self.cooldown_check(interaction):
            await interaction.response.send_message(
                "Please wait 5 seconds before using this command again.",
                ephemeral=True)
            return

        if not image and not image_url:
            await interaction.response.send_message(
                "Please provide either an image attachment or an image URL.",
                ephemeral=True)
            return

        await interaction.response.defer()

        try:
            jpg_image = await self.convert_to_jpg(
                image.url if image else image_url)
            plant_data = await self.get_plant_data(jpg_image, language)
            if plant_data and plant_data.get("results"):
                pages = self.create_plant_embeds(
                    plant_data["results"][:5],
                    language)  # Limit to top 5 results
                view = PlantView(pages)
                message = await interaction.followup.send(embed=pages[0],
                                                          view=view)
                view.message = message
                self.bot.loop.create_task(self.check_view_timeout(view))
            else:
                await interaction.followup.send(
                    "Sorry, I couldn't identify the plant in the image.")
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {str(e)}")

    async def check_view_timeout(self, view):
        while not view.is_finished():
            if asyncio.get_event_loop().time() - view.last_interaction > 60:
                await view.on_timeout()
                break
            await asyncio.sleep(1)

    async def convert_to_jpg(self, image_url: str) -> io.BytesIO:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image = Image.open(io.BytesIO(image_data))
                    jpg_image = io.BytesIO()
                    image.convert('RGB').save(jpg_image, format='JPEG')
                    jpg_image.seek(0)
                    return jpg_image
                else:
                    raise Exception("Failed to fetch the image")

    async def get_plant_data(self, jpg_image: io.BytesIO,
                             language: str) -> dict:
        data = aiohttp.FormData()
        data.add_field('images',
                       jpg_image,
                       filename='image.jpg',
                       content_type='image/jpeg')
        params = {
            "api-key": self.api_key,
            "include-related-images": "true",
            "no-reject": "false",
            "lang": language,
            "type": "all"
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.api_url, data=data,
                                        params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
            except aiohttp.ClientError:
                return None

    def create_plant_embeds(self, plant_results: list, language: str) -> list:
        pages = []
        for index, plant_data in enumerate(plant_results, start=1):
            embed = discord.Embed(
                title=f"Plant Identification Result (Guess {index})",
                color=discord.Color.green(),
                description="Here's what I found based on the image:")

            species = plant_data["species"]
            scientific_name = species["scientificNameWithoutAuthor"]
            common_names = species.get("commonNames", ["N/A"])
            family = species["family"].get("scientificNameWithoutAuthor",
                                           "N/A")
            genus = species["genus"].get("scientificNameWithoutAuthor", "N/A")
            confidence = plant_data["score"]

            embed.add_field(name="Scientific Name",
                            value=f"*{scientific_name}*",
                            inline=False)
            embed.add_field(name="Common Name(s)",
                            value=", ".join(common_names[:3]),
                            inline=False)
            embed.add_field(name="Family", value=family, inline=True)
            embed.add_field(name="Genus", value=genus, inline=True)
            embed.add_field(name="Confidence",
                            value=f"{confidence:.2%}",
                            inline=False)

            if "gbif" in species:
                gbif_data = species["gbif"]
                habitat = gbif_data.get("habitat", "N/A")
                uses = gbif_data.get("uses", "N/A")
                embed.add_field(name="Habitat", value=habitat, inline=False)
                embed.add_field(name="Uses", value=uses, inline=False)

            wiki_link = f"https://{language}.wikipedia.org/wiki/{scientific_name.replace(' ', '_')}"
            embed.add_field(name="Learn More",
                            value=f"[Wikipedia]({wiki_link})",
                            inline=False)

            if "images" in plant_data and len(plant_data["images"]) > 0:
                image_url = plant_data["images"][0].get("url", {}).get("m")
                if image_url:
                    embed.set_thumbnail(url=image_url)

            embed.set_footer(
                text=
                f"Data provided by PlantNet | Page {index} of {len(plant_results)}"
            )
            pages.append(embed)

        return pages


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlantIdentifier(bot))
