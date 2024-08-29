import discord
from discord.ext import commands
import traceback
import aiohttp
from difflib import get_close_matches

# Define the embed color
EMBED_COLOR = 0x2f3131
DELETE_AFTER = 10  # Time in seconds after which the error message will delete itself


class Errors(commands.Cog):
    """
    A cog to handle and report errors occurring during command execution.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialize the Errors cog.

        Args:
            bot (commands.Bot): The instance of the bot.
        """
        self.bot = bot
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    async def send_error_embed(self, ctx: commands.Context, title: str,
                               description: str,
                               button_color: discord.ButtonStyle) -> None:
        """
        Send an embed with error information to the context channel.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            title (str): The title of the embed.
            description (str): The description of the embed.
            button_color (discord.ButtonStyle): The color of the help button.
        """
        embed = discord.Embed(title=title,
                              description=f"```py\n{description}```",
                              color=EMBED_COLOR)
        view = discord.ui.View()
        view.add_item(HelpButton(ctx, title, description, button_color))

        try:
            await ctx.send(embed=embed,
                           view=view,
                           ephemeral=True,
                           delete_after=DELETE_AFTER)
        except discord.errors.NotFound:
            # The channel was not found, possibly deleted or bot lacks permissions
            print(
                "Failed to send an error embed because the channel was not found or bot lacks permissions."
            )

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    async def handle_error(self, ctx: commands.Context,
                           error: commands.CommandError, description: str,
                           title: str) -> None:
        """
        Handle sending an error embed based on the error type.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            error (commands.CommandError): The error that was raised.
            description (str): The description of the error.
            title (str): The title of the error.
        """
        button_color = self.get_button_color(title)
        await self.send_error_embed(ctx, title, description, button_color)

    def get_button_color(self, title: str) -> discord.ButtonStyle:
        """
        Get the button color based on the seriousness of the error.

        Args:
            title (str): The title of the error.

        Returns:
            discord.ButtonStyle: The color of the button.
        """
        minor_errors = [
            "Missing Required Argument", "Command Not Found",
            "User Input Error", "Invalid End of Quoted String",
            "Expected Closing Quote", "Unexpected Quote", "Bad Argument"
        ]

        major_errors = [
            "Missing Permissions", "Bot Missing Permissions",
            "Command on Cooldown", "No Private Message", "Check Failure",
            "Disabled Command", "NSFW Channel Required"
        ]

        critical_errors = [
            "Not Owner", "Forbidden", "Not Found", "HTTP Exception",
            "Max Concurrency Reached", "Unexpected Error"
        ]

        if title in minor_errors:
            return discord.ButtonStyle.success  # Green
        elif title in major_errors:
            return discord.ButtonStyle.primary  # Blue
        elif title in critical_errors:
            return discord.ButtonStyle.danger  # Red
        else:
            return discord.ButtonStyle.secondary  # Grey

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context,
                               error: commands.CommandError) -> None:
        """
        Handle errors that occur during command execution.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            error (commands.CommandError): The error that was raised.
        """
        if isinstance(error,
                      discord.errors.HTTPException) and error.status == 429:
            # Log the rate limit issue
            print("Hit rate limit. Retrying after delay.")
            return  # You can also add a retry mechanism here if necessary

        command_name = ctx.command.qualified_name if ctx.command else "Unknown Command"
        command_signature = getattr(ctx.command, 'signature',
                                    '') if ctx.command else ""

        title, description = self.get_error_title_and_description(
            ctx, error, command_name, command_signature)
        await self.handle_error(ctx, error, description, title)

    def get_error_title_and_description(self, ctx: commands.Context,
                                        error: commands.CommandError,
                                        command_name: str,
                                        command_signature: str) -> (str, str):
        """
        Get the title and description for the error embed based on the error type.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            error (commands.CommandError): The error that was raised.
            command_name (str): The name of the command that triggered the error.
            command_signature (str): The command signature.

        Returns:
            tuple: The title and description for the error embed.
        """
        if isinstance(error, commands.MissingRequiredArgument):
            return (
                "Missing Required Argument",
                f"Argument: '{error.param.name}'\nUsage: {ctx.prefix}{command_name} {command_signature}"
            )

        elif isinstance(error, commands.CommandNotFound):
            similar_commands = get_close_matches(
                error.args[0].split()[0],
                [cmd.name for cmd in self.bot.commands],
                n=3,
                cutoff=0.6)
            description = "Command not found. Please check your command and try again."
            if similar_commands:
                description += "\n\nDid you mean?\n" + '\n'.join(
                    similar_commands)
            return ("Command Not Found", description)

        elif isinstance(error, commands.MissingPermissions):
            perms = ', '.join(error.missing_permissions)
            return (
                "Missing Permissions",
                f"You need the following permissions to execute this command: {perms}"
            )

        elif isinstance(error, commands.BotMissingPermissions):
            perms = ', '.join(error.missing_permissions)
            return (
                "Bot Missing Permissions",
                f"I need the following permissions to execute this command: {perms}"
            )

        elif isinstance(error, commands.CommandOnCooldown):
            return (
                "Command on Cooldown",
                f"This command is on cooldown. Try again after {error.retry_after:.2f} seconds."
            )

        elif isinstance(error, commands.NotOwner):
            return ("Not Owner", "Only the bot owner can use this command.")

        elif isinstance(error, commands.NoPrivateMessage):
            return (
                "No Private Message",
                "This command cannot be used in private messages. Please use it in a server channel."
            )

        elif isinstance(error, commands.BadArgument):
            return ("Bad Argument", str(error))

        elif isinstance(error, commands.CheckFailure):
            return ("Check Failure",
                    "You do not have permission to execute this command.")

        elif isinstance(error, commands.DisabledCommand):
            return ("Disabled Command", "This command is currently disabled.")

        elif isinstance(error, commands.UserInputError):
            return ("User Input Error", str(error))

        elif isinstance(error, commands.InvalidEndOfQuotedStringError):
            return ("Invalid End of Quoted String", str(error))

        elif isinstance(error, commands.ExpectedClosingQuoteError):
            return ("Expected Closing Quote", str(error))

        elif isinstance(error, commands.MaxConcurrencyReached):
            return (
                "Max Concurrency Reached",
                f"This command can only be used {error.number} times concurrently."
            )

        elif isinstance(error, commands.UnexpectedQuoteError):
            return ("Unexpected Quote", str(error))

        elif isinstance(error, discord.Forbidden):
            return ("Forbidden", "I do not have permission to do that.")

        elif isinstance(error, discord.NotFound):
            return ("Not Found", "The requested resource was not found.")

        elif isinstance(error, discord.HTTPException):
            return ("HTTP Exception", "An HTTP exception occurred.")

        else:
            # Log the error with traceback
            traceback_str = ''.join(
                traceback.format_exception(type(error), error,
                                           error.__traceback__))
            return ("Unexpected Error", traceback_str)


class HelpButton(discord.ui.Button):

    def __init__(self, ctx: commands.Context, title: str, description: str,
                 button_color: discord.ButtonStyle):
        super().__init__(label='Help', emoji='❓', style=button_color)
        self.ctx = ctx
        self.title = title
        self.description = description

    async def callback(self, interaction: discord.Interaction):
        help_message = self.get_help_message(self.title)
        embed = discord.Embed(title=f'Help: {self.title}',
                              description=help_message,
                              color=EMBED_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def get_help_message(self, error_title: str) -> str:
        help_messages = {
            "Missing Required Argument":
            "You missed a required argument for the command. Please check the command syntax and try again.",
            "Command Not Found":
            "The command you entered was not found. Please check the command and try again.",
            "Missing Permissions":
            "You do not have the necessary permissions to execute this command. Please contact a server administrator if you believe this is an error.",
            "Bot Missing Permissions":
            "The bot does not have the necessary permissions to execute this command. Please ensure the bot has the correct permissions.",
            "Command on Cooldown":
            "This command is on cooldown. Please wait a few moments and try again.",
            "Not Owner":
            "Become the owner of the bot to use owner only commands.\nApply here - https://blogs.mtdv.me/articles/owner-applications",
            "No Private Message":
            "This command cannot be used in private messages. Please use it in a server channel.",
            "Bad Argument":
            "There was an issue with the arguments you provided. Please check the command syntax and try again.",
            "Check Failure":
            "You do not meet the requirements to use this command.",
            "Disabled Command":
            "This command is currently disabled.",
            "User Input Error":
            "There was an error with the input you provided. Please check the command syntax and try again.",
            "Invalid End of Quoted String":
            "There was an issue with the quoted string in your command. Please check the command syntax and try again.",
            "Expected Closing Quote":
            "A closing quote was expected but not found. Please check the command syntax and try again.",
            "Max Concurrency Reached":
            "This command can only be used a limited number of times concurrently. Please wait and try again.",
            "Unexpected Quote":
            "An unexpected quote was found in your command. Please check the command syntax and try again.",
            "Invalid Argument":
            "An invalid argument was provided. Please check the command syntax and try again.",
            "NSFW Channel Required":
            "This command can only be used in NSFW channels.",
            "Forbidden":
            "The bot does not have permission to perform this action.",
            "Not Found":
            "The requested resource was not found.",
            "HTTP Exception":
            "An HTTP exception occurred. Please try again later.",
            "Unexpected Error":
            "An unexpected error occurred. Please report the issue to the developers."
        }

        return help_messages.get(
            error_title,
            "This error cannot be fixed by the user. Please report the issue to the developers."
        )


async def setup(bot: commands.Bot) -> None:
    """
    Load the Errors cog.

    Args:
        bot (commands.Bot): The instance of the bot.
    """
    await bot.add_cog(Errors(bot))
