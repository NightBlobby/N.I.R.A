import discord
from discord.ext import commands
from utils.helputil import HelpEmbedUtil
import aiohttp


class HelpDropdown(discord.ui.Select):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        options = [
            discord.SelectOption(label="General",
                                 description="General bot commands",
                                 emoji="ℹ️"),
            discord.SelectOption(label="Image",
                                 description="Image-related commands",
                                 emoji="🖼️"),
            discord.SelectOption(label="Games",
                                 description="Game commands",
                                 emoji="🎮"),
            discord.SelectOption(label="Moderation",
                                 description="Moderation commands",
                                 emoji="🛡️"),
            discord.SelectOption(label="Fun",
                                 description="Fun and miscellaneous commands",
                                 emoji="🎉"),
        ]
        super().__init__(placeholder="Choose a category... 🗂️",
                         min_values=1,
                         max_values=1,
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = HelpEmbedUtil.create_category_embed(category)
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.add_item(HelpDropdown(bot))


class HelpCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = None
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    @commands.group(invoke_without_command=True)
    async def help(self, ctx, command: str = None):
        if command is None:
            embed = HelpEmbedUtil.create_main_embed()
            await ctx.send(embed=embed, view=HelpView(self.bot))
        else:
            cmd = self.bot.get_command(command)
            if cmd is None:
                await ctx.send("Command not found.")
            else:
                embed = HelpEmbedUtil.create_command_embed(
                    command, cmd.help or "No description available.",
                    f"{ctx.prefix}{cmd.qualified_name} {cmd.signature}")
                await ctx.send(embed=embed)

    @help.command()
    async def plant(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/plant", "Identify a plant using an image or image URL.",
            "/plant <[image] or [image url]>")
        await ctx.send(embed=embed)

    @help.command()
    async def meme(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/meme", "Fetch a meme from the specified category.",
            "/meme [category]")
        await ctx.send(embed=embed)

    @help.command()
    async def identify(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/identify", "Extract text from an image using an image or URL.",
            "/identify <[image] or [image url]>")
        await ctx.send(embed=embed)

    @help.command()
    async def embed(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/embed", "Create an interactive embed within Discord.", ".embed")
        await ctx.send(embed=embed)

    @help.command()
    async def ttt(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/ttt", "Play a game of Tic-Tac-Toe with a friend.",
            "/ttt <opponent> [custom emoji] [custom emoji]")
        await ctx.send(embed=embed)

    @help.command()
    async def tetris(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            ".tetris", "Play a game of Tetris within Discord.", ".tetris")
        await ctx.send(embed=embed)

    @help.command()
    async def memorygame(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/memorygame",
            "Play a memory game where you match pairs of emojis.",
            "/memorygame")
        await ctx.send(embed=embed)

    @help.command()
    async def trivia(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            ".trivia", "Challenge yourself with a trivia quiz.", ".trivia")
        await ctx.send(embed=embed)

    @help.command()
    async def reaction_role(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/reaction-role", "Setup reaction roles with buttons.",
            "/reaction-role <role> [color] [emoji] [link]")
        await ctx.send(embed=embed)

    @help.command()
    async def reaction_role_summary(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/reaction-role-summary",
            "Get a summary of all reaction roles setup in the server.",
            "/reaction-role-summary")
        await ctx.send(embed=embed)

    @help.command()
    async def shorten(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/shorten", "Shorten URLs and optionally generate a QR code.",
            "/shorten <link to shorten> [qrcode true/false]")
        await ctx.send(embed=embed)

    @help.command()
    async def urban(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/urban", "Search any word in the Urban Dictionary.",
            "/urban <word>")
        await ctx.send(embed=embed)

    @help.command()
    async def weather(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/weather", "Get the weather status in your city.",
            "/weather <city>")
        await ctx.send(embed=embed)

    @help.command()
    async def wiki(self, ctx):
        embed = HelpEmbedUtil.create_command_embed("/wiki",
                                                   "Search from Wikipedia.",
                                                   "/wiki <query>")
        await ctx.send(embed=embed)

    @help.command()
    async def kick(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/kick", "Kick a user from the server.", "/kick <user> [reason]")
        await ctx.send(embed=embed)

    @help.command()
    async def ban(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/ban", "Ban a user from the server.", "/ban <user> [reason]")
        await ctx.send(embed=embed)

    @help.command()
    async def unban(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/unban", "Unban a previously banned user.", "/unban <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def nuke(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/nuke", "Delete and recreate a channel with the same properties.",
            "/nuke")
        await ctx.send(embed=embed)

    @help.command()
    async def purge(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/purge", "Clear a specified number of messages from a channel.",
            "/purge <no of messages>")
        await ctx.send(embed=embed)

    @help.command()
    async def avatar(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/avatar", "Get the avatar of a user.", "/avatar <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def channel_id(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/channel_id", "Get the ID of a specified channel.",
            "/channel_id <channel>")
        await ctx.send(embed=embed)

    @help.command()
    async def ping(self, ctx):
        embed = HelpEmbedUtil.create_command_embed("/ping",
                                                   "Get the bot's latency.",
                                                   "/ping")
        await ctx.send(embed=embed)

    @help.command()
    async def wanted(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            ".wanted", "Place a user's profile picture in a wanted poster.",
            ".wanted <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def emojify(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            ".emojify", "Convert an image into a grid of emojis.",
            ".emojify <image link> <size>")
        await ctx.send(embed=embed)

    @help.command()
    async def asciify(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            ".asciify", "Convert an image into ASCII art.",
            ".asciify <image link>")
        await ctx.send(embed=embed)

    @help.command()
    async def joke(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(".joke",
                                                   "Get a random joke.",
                                                   ".joke")
        await ctx.send(embed=embed)

    @help.command()
    async def collatz(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            ".collatz", "Check if a number satisfies the Collatz conjecture.",
            ".collatz <number>")
        await ctx.send(embed=embed)

    @help.command()
    async def pp(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(".pp",
                                                   "Get a random penis size.",
                                                   ".pp")
        await ctx.send(embed=embed)

    @help.command()
    async def rng(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            ".rng", "Generate a random number between 1 and 1000.", ".rng")
        await ctx.send(embed=embed)

    @help.command()
    async def role_info(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/role-info", "Get detailed information about a specific role.",
            "/role-info <role>")
        await ctx.send(embed=embed)

    @help.command()
    async def role_list(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/role-list", "List all roles assigned to a member.",
            "/role-list <member>")
        await ctx.send(embed=embed)

    @help.command()
    async def role_remove(self, ctx):
        embed = HelpEmbedUtil.create_command_embed(
            "/role-remove", "Remove a specific role from a member.",
            "/role-remove <member> <role>")
        await ctx.send(embed=embed)

    async def cog_unload(self):
        self.bot.help_command = self._original_help_command
        await self.session.close()


# Setup the cog
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HelpCog(bot))
