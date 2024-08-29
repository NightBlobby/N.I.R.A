import discord
from discord.ext import commands
from discord import app_commands
from abc import ABC, abstractmethod

# Import the Database instance from database.py
from database import db


# DatabaseManager interface for abstracting database operations
class DatabaseManager(ABC):

    @abstractmethod
    async def get_prefix(self, guild_id: int) -> str:
        pass

    @abstractmethod
    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        pass


class PostgreSQLManager(DatabaseManager):

    async def initialize(self):
        await db.initialize()

    async def get_prefix(self, guild_id: int) -> str:
        query = 'SELECT prefix FROM guild_prefixes WHERE guild_id = $1'
        result = await db.fetch(query, guild_id)
        return result[0]['prefix'] if result else '.'

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        query = '''
        INSERT INTO guild_prefixes (guild_id, prefix)
        VALUES ($1, $2)
        ON CONFLICT (guild_id) DO UPDATE SET prefix = $2
        '''
        await db.execute(query, guild_id, prefix)


class PrefixCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db_manager = PostgreSQLManager()

    async def cog_load(self):
        await self.db_manager.initialize()

    async def cog_unload(self):
        await db.close()

    @staticmethod
    def is_valid_prefix(prefix: str) -> bool:
        return len(prefix) <= 10 and not any(char.isspace() for char in prefix)

    @app_commands.command(
        name='prefix',
        description='Change or view the bot prefix for this server')
    @app_commands.describe(
        new_prefix='The new prefix to set (leave empty to view current prefix)'
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def change_prefix(self,
                            interaction: discord.Interaction,
                            new_prefix: str = None):
        if new_prefix is None:
            current_prefix = await self.db_manager.get_prefix(
                interaction.guild.id)
            await interaction.response.send_message(
                f"The current prefix is: `{current_prefix}`")
            return

        if not self.is_valid_prefix(new_prefix):
            await interaction.response.send_message(
                "Invalid prefix. It must be 10 characters or less and contain no spaces.",
                ephemeral=True)
            return

        await self.db_manager.set_prefix(interaction.guild.id, new_prefix)
        self.bot.command_prefix = commands.when_mentioned_or(new_prefix)
        await interaction.response.send_message(
            f"Prefix updated to: `{new_prefix}`")

    @change_prefix.error
    async def change_prefix_error(self, interaction: discord.Interaction,
                                  error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You need 'Manage Server' permissions to change the prefix.",
                ephemeral=True)

    async def get_prefix(self, message: discord.Message) -> str:
        if message.guild:
            return await self.db_manager.get_prefix(message.guild.id)
        return '.'  # Default prefix for DMs


async def setup(bot):
    cog = PrefixCog(bot)
    await bot.add_cog(cog)
    bot.get_prefix = cog.get_prefix
