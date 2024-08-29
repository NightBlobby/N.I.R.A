import os
import logging
import discord
from discord.ext import commands
import asyncio
from aiohttp import ClientSession
from typing import Any
from webserver import keep_alive
import aiohttp

# -------------------------
# Logging Configuration
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


# -------------------------
# Bot Class Definition
# -------------------------
class Bot(commands.Bot):

    def __init__(self, command_prefix: str, intents: discord.Intents,
                 session: ClientSession, **kwargs: Any) -> None:
        super().__init__(command_prefix=self.get_prefix,
                         intents=intents,
                         **kwargs)
        self.session = session
        self.default_prefix = command_prefix

    async def setup_hook(self) -> None:
        try:
            await self.load_extension("jishaku")
            logger.info("Extension 'jishaku' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load extension 'jishaku': {e}")
        await self.load_all_cogs()

    async def load_all_cogs(self) -> None:
        cog_files = [f for f in os.listdir('./cogs') if f.endswith('.py')]
        await asyncio.gather(*(self.load_cog(f) for f in cog_files))

    async def load_cog(self, filename: str) -> None:
        cog_name = f'cogs.{filename[:-3]}'
        try:
            await self.load_extension(cog_name)
            logger.info(f"{cog_name} loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load {cog_name}: {e}")

    async def on_ready(self) -> None:
        if self.user is None:
            logger.error("Bot user is not set. This should not happen.")
            return
        logger.info(f'Bot is ready as {self.user} (ID: {self.user.id}).')
        await self.tree.sync()

    async def on_error(self, event_method: str, *args: Any,
                       **kwargs: Any) -> None:
        logger.error('Unhandled exception in %s.', event_method, exc_info=True)

    async def close(self) -> None:
        await super().close()

    async def get_prefix(self, message: discord.Message) -> str:
        if not message.guild:
            return self.default_prefix

        prefix_cog = self.get_cog('PrefixCog')
        if prefix_cog:
            return await prefix_cog.get_prefix(message)
        return self.default_prefix


# -------------------------
# Main Function and Execution
# -------------------------
async def main() -> None:
    intents = discord.Intents.all()
    intents.message_content = True
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set.")
        return

    async with ClientSession() as session:
        bot = Bot(command_prefix=".",
                  case_insensitive=True,
                  intents=intents,
                  session=session)
        try:
            await bot.start(token)
        except discord.LoginFailure:
            logger.error("Invalid bot token provided.")
        except Exception as e:
            logger.error(f"An error occurred during bot startup: {e}")
        finally:
            if bot.is_closed():
                logger.warning("Bot has been disconnected.")
            await session.close()


if __name__ == "__main__":
    keep_alive()  # Start the webserver for keeping the bot alive
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown initiated by user.")
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
