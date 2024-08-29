import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from bs4 import BeautifulSoup
import textwrap
from abc import ABC, abstractmethod
import asyncio


class CustomWikipediaAPI:
    BASE_URL = "https://en.wikipedia.org/w/api.php"

    @staticmethod
    async def search(query: str):
        params = {
            "action": "opensearch",
            "search": query,
            "limit": 1,
            "format": "json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(CustomWikipediaAPI.BASE_URL,
                                   params=params) as response:
                data = await response.json()
                return data[1][0] if data[1] else None

    @staticmethod
    async def get_page_info(title: str):
        params = {
            "action": "query",
            "prop": "extracts|info|pageimages",
            "exintro": "true",
            "inprop": "url",
            "pithumbsize": "300",
            "titles": title,
            "format": "json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(CustomWikipediaAPI.BASE_URL,
                                   params=params) as response:
                data = await response.json()
                page = next(iter(data['query']['pages'].values()))

                soup = BeautifulSoup(page.get('extract', ''), 'html.parser')
                summary = soup.get_text()

                return {
                    'title': page['title'],
                    'url': page['fullurl'],
                    'summary': summary,
                    'image_url': page.get('thumbnail', {}).get('source')
                }


class WikiSearcher(ABC):

    @staticmethod
    @abstractmethod
    async def search(query: str):
        pass

    @staticmethod
    @abstractmethod
    async def get_page_info(title: str):
        pass


class WikipediaSearcher(WikiSearcher):

    @staticmethod
    async def search(query: str):
        return await CustomWikipediaAPI.search(query)

    @staticmethod
    async def get_page_info(title: str):
        return await CustomWikipediaAPI.get_page_info(title)


class WikiEmbedCreator:

    @staticmethod
    def create_base_embed(title: str, url: str, image_url: str):
        embed = discord.Embed(title=title, url=url, color=0x3498db)
        if image_url:
            embed.set_thumbnail(url=image_url)
        embed.set_footer(text="Source: Wikipedia")
        return embed

    @staticmethod
    def split_content(content: str, max_chars: int = 2048):
        return textwrap.wrap(content, max_chars, replace_whitespace=False)


class WikiView(discord.ui.View):

    def __init__(self, base_embed: discord.Embed, content_chunks: list):
        super().__init__(timeout=30)
        self.base_embed = base_embed
        self.content_chunks = content_chunks
        self.current_page = 0
        self.update_buttons()
        self.message = None
        self.timer_task = None

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray, row=0)
    async def prev_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await self.change_page(interaction, -1)

    @discord.ui.button(label="1/1",
                       style=discord.ButtonStyle.green,
                       disabled=True,
                       row=0)
    async def page_counter(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        pass

    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray, row=0)
    async def next_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await self.change_page(interaction, 1)

    @discord.ui.button(label="Go to", style=discord.ButtonStyle.blurple, row=1)
    async def goto_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.send_modal(GotoModal(self))

    async def change_page(self, interaction: discord.Interaction, change: int):
        self.current_page = (self.current_page + change) % len(
            self.content_chunks)
        await self.update_view(interaction)

    async def update_view(self, interaction: discord.Interaction):
        self.update_buttons()
        embed = self.base_embed.copy()
        embed.description = self.content_chunks[self.current_page]
        embed.set_footer(
            text=
            f"Page {self.current_page + 1}/{len(self.content_chunks)} | Source: Wikipedia"
        )
        await interaction.response.edit_message(embed=embed, view=self)
        self.reset_timer()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(
            self.content_chunks) - 1
        self.page_counter.label = f"{self.current_page + 1}/{len(self.content_chunks)}"

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    def reset_timer(self):
        if self.timer_task:
            self.timer_task.cancel()
        self.timer_task = asyncio.create_task(self.start_timer())

    async def start_timer(self):
        await asyncio.sleep(30)
        await self.on_timeout()

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        self.reset_timer()
        return True


class GotoModal(discord.ui.Modal, title="Go to Page"):
    page_number = discord.ui.TextInput(label="Page Number",
                                       placeholder="Enter a page number")

    def __init__(self, view: WikiView):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        try:
            page = int(self.page_number.value) - 1
            if 0 <= page < len(self.view.content_chunks):
                self.view.current_page = page
                await self.view.update_view(interaction)
            else:
                await interaction.response.send_message(
                    f"Invalid page number. Please enter a number between 1 and {len(self.view.content_chunks)}.",
                    ephemeral=True)
        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid number.", ephemeral=True)


class Wiki(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.searcher = WikipediaSearcher()
        self.embed_creator = WikiEmbedCreator()
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    @app_commands.command(name="wiki",
                          description="Search Wikipedia for information")
    async def wiki(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        try:
            page_title = await self.searcher.search(query)
            if not page_title:
                await interaction.followup.send(
                    "No results found for your query. Please try a different search term.",
                    ephemeral=True)
                return

            page_info = await self.searcher.get_page_info(page_title)
            base_embed = self.embed_creator.create_base_embed(
                page_info['title'], page_info['url'], page_info['image_url'])
            content_chunks = self.embed_creator.split_content(
                page_info['summary'])

            initial_embed = base_embed.copy()
            initial_embed.description = content_chunks[0]

            if len(content_chunks) == 1:
                # If there's only one page, don't use the WikiView
                initial_embed.set_footer(text="Source: Wikipedia")
                await interaction.followup.send(embed=initial_embed)
            else:
                # If there are multiple pages, use the WikiView
                view = WikiView(base_embed, content_chunks)
                initial_embed.set_footer(
                    text=f"Page 1/{len(content_chunks)} | Source: Wikipedia")
                message = await interaction.followup.send(embed=initial_embed,
                                                          view=view)
                view.message = message
                view.reset_timer()
        except Exception as e:
            await interaction.followup.send(
                f"An error occurred while processing your request: {str(e)}",
                ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Wiki(bot))
