import discord
from abc import ABC, abstractmethod


class EmbedUtilBase(ABC):

    @staticmethod
    @abstractmethod
    def create_embed(title: str, description: str,
                     color: discord.Color) -> discord.Embed:
        pass

    @staticmethod
    @abstractmethod
    def create_command_embed(
        command_name: str,
        description: str,
        usage: str,
        color: discord.Color = discord.Color.blue()) -> discord.Embed:
        pass

    @staticmethod
    @abstractmethod
    def create_category_embed(category: str) -> discord.Embed:
        pass


class HelpEmbedUtil(EmbedUtilBase):

    @staticmethod
    def create_embed(title: str, description: str,
                     color: discord.Color) -> discord.Embed:
        embed = discord.Embed(title=title,
                              description=description,
                              color=color)
        embed.set_thumbnail(url="https://i.imgur.com/LOqyPNj.png")
        embed.set_footer(text="<> - required | [] - optional")
        return embed

    @staticmethod
    def create_command_embed(
        command_name: str,
        description: str,
        usage: str,
        color: discord.Color = discord.Color.blue()) -> discord.Embed:
        embed = HelpEmbedUtil.create_embed(f"Command: {command_name}",
                                           description, color)
        embed.add_field(name="Usage", value=f"```{usage}```", inline=False)
        return embed

    @staticmethod
    def create_category_embed(category: str) -> discord.Embed:
        embed = discord.Embed(title=f"{category} Commands",
                              color=discord.Color.blue())

        commands_info = {
            "General":
            [(".help [command]", "Displays help for a specific command")],
            "Image": [
                ("/plant <[image] or [image url]>",
                 "Identify a plant using an image or image URL."),
                ("/identify <[image] or [image url]>",
                 "Extract text from an image using an image or URL."),
                (".asciify <image link>", "Convert an image into ASCII art."),
                (".emojify <image link> <size>",
                 "Convert an image into a grid of emojis."),
            ],
            "Games": [
                ("/ttt <opponent> [custom emoji 1] [custom emoji 2]",
                 "Play a game of Tic-Tac-Toe with a friend."),
                (".tetris", "Play a game of Tetris within Discord."),
                (".memorygame",
                 "Play a memory game where you match pairs of emojis."),
                (".trivia", "Challenge yourself with a trivia quiz."),
            ],
            "Moderation": [
                ("/kick <user> [reason]", "Kick a user from the server."),
                ("/ban <user> [reason]", "Ban a user from the server."),
                ("/unban <user>", "Unban a previously banned user."),
                ("/nuke",
                 "Delete and recreate a channel with the same properties."),
                ("/purge <no of messages>",
                 "Clear a specified number of messages from a channel."),
                ("/avatar <user>", "Get the avatar of a user."),
                ("/channel_id <channel>",
                 "Get the ID of a specified channel."),
                ("/ping", "Get the bot's latency."),
                ("/warn <member> [reason]", "Warn a member in the server."),
                ("/slowmode <time>",
                 "Set slowmode in a channel for a specified duration."),
                ("/role-add <role> <member> [time]",
                 "Add a role to a member for a specified duration."),
                ("/role-info <role>",
                 "Get detailed information about a specific role."),
                ("/role-list <member>",
                 "List all roles assigned to a member."),
                ("/role-remove <member> <role>",
                 "Remove a specific role from a member."),
            ],
            "Fun": [
                ("/meme [category]",
                 "Fetch a meme from the specified category."),
                ("/wanted <user>",
                 "Place a user's profile picture in a wanted poster."),
                (".joke", "Get a random joke."),
                (".collatz <number>",
                 "Check if a number satisfies the Collatz conjecture."),
                (".pp", "Get a random penis size."),
                (".rng", "Generate a random number between 1 and 1000."),
            ],
        }

        for cmd, desc in commands_info.get(category, []):
            embed.add_field(name=f"`{cmd}`", value=desc, inline=False)

        embed.set_footer(
            text="Use .help <command> to get more info on a specific command.")
        return embed

    @staticmethod
    def create_main_embed() -> discord.Embed:
        embed = discord.Embed(
            title="🔍 Commands Help",
            description=
            ("**Welcome to the N.I.R.A help menu!**\n\n"
             "Use the dropdown below to select a command category. "
             "Each category provides information about the commands available under it.\n\n"
             "You can also use `.help <command>` to get detailed information on a specific command."
             ),
            color=discord.Color.blue())
        embed.set_thumbnail(url="https://i.imgur.com/LOqyPNj.png")
        embed.add_field(
            name="Categories:",
            value=(
                "ℹ️ **General** - General bot commands.\n\n"
                "🖼️ **Image** - Commands related to image manipulation.\n\n"
                "🎮 **Games** - Fun games to play in Discord.\n\n"
                "🛡️ **Moderation** - Moderation tools for server admins.\n\n"
                "🎉 **Fun** - Miscellaneous and fun commands."),
            inline=False)
        embed.add_field(
            name="How to Use:",
            value=
            "Use the dropdown to explore commands, or type `.help <command>` for specific details.",
            inline=False)
        embed.set_footer(text="<> - required | [] - optional")
        return embed
