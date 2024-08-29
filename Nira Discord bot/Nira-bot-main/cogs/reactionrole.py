import discord
from discord.ext import commands
from discord import app_commands
import random
import string
import asyncio
from typing import Dict, Any, Set, List, Optional, Tuple
from abc import ABC, abstractmethod
import aiohttp
from database import db

# Rate limits
RATE_LIMIT_INTERVAL = 2
RATE_LIMIT_CLEANUP_INTERVAL = 60


class RolesyncCooldown:

    def __init__(self, rate: int, per: int) -> None:
        self.rate = rate
        self.per = per
        self.last_used: Dict[int, float] = {}

    def __call__(self, ctx: commands.Context) -> bool:
        now = ctx.message.created_at.timestamp()
        bucket = ctx.guild.id if ctx.guild else ctx.author.id
        if bucket in self.last_used:
            last = self.last_used[bucket]
            if now - last < self.per:
                raise commands.CommandOnCooldown(
                    cooldown=commands.Cooldown(self.rate, self.per),
                    retry_after=self.per - (now - last),
                    type=commands.BucketType.guild)
        self.last_used[bucket] = now
        return True


class NavigationView(discord.ui.View):

    def __init__(self, cog: 'ReactionRole', guild: discord.Guild,
                 channel: discord.TextChannel) -> None:
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
        self.channel = channel
        self.current_page = 0
        self.message_ids = self.get_message_ids()

    def get_message_ids(self) -> List[str]:
        return ['overview'] + [
            message_id for message_id, roles_data in self.cog.reaction_roles[
                str(self.guild.id)].items()
            if roles_data[0]['channel_id'] == str(self.channel.id)
        ]

    def update_button_state(self) -> None:
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(
            self.message_ids) - 1

    @discord.ui.button(label="Previous",
                       style=discord.ButtonStyle.primary,
                       row=1)
    async def prev_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button) -> None:
        if self.current_page > 0:
            self.current_page -= 1
            self.update_button_state()
            await self.update_embed(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=1)
    async def next_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button) -> None:
        if self.current_page < len(self.message_ids) - 1:
            self.current_page += 1
            self.update_button_state()
            await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction) -> None:
        if self.current_page == 0:
            embed = await self.cog.create_channel_reaction_roles_embed(
                self.guild, self.channel)
        else:
            message_id = self.message_ids[self.current_page]
            embed = await self.cog.create_message_reaction_roles_embed(
                self.guild, self.channel, message_id)
        await interaction.response.edit_message(embed=embed, view=self)


class ChannelSelect(discord.ui.Select):

    def __init__(self, cog: 'ReactionRole',
                 options: List[discord.SelectOption]) -> None:
        super().__init__(placeholder="Select a channel", options=options)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction) -> None:
        channel_id = int(self.values[0])
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            view = NavigationView(self.cog, interaction.guild, channel)
            overview_embed = await self.cog.create_channel_reaction_roles_embed(
                interaction.guild, channel)
            await interaction.response.edit_message(embed=overview_embed,
                                                    view=view)


class ChannelSelectView(discord.ui.View):

    def __init__(self, cog: 'ReactionRole',
                 options: List[discord.SelectOption]) -> None:
        super().__init__()
        self.add_item(ChannelSelect(cog, options))


class ColorChoice(app_commands.Choice):
    """Defines color choices for reaction role buttons."""
    Red = app_commands.Choice(name="Red", value="red")
    Green = app_commands.Choice(name="Green", value="green")
    Blurple = app_commands.Choice(name="Blurple", value="blurple")
    Gray = app_commands.Choice(name="Gray", value="gray")


class ColorMapping:
    """Maps color names to Discord button styles."""
    MAPPING = {
        "red": discord.ButtonStyle.danger,
        "green": discord.ButtonStyle.success,
        "blurple": discord.ButtonStyle.primary,
        "gray": discord.ButtonStyle.secondary
    }

    @classmethod
    def get_style(cls, color: str) -> discord.ButtonStyle:
        """Get the Discord button style for a given color name."""
        return cls.MAPPING.get(color.lower(), discord.ButtonStyle.primary)


class DataManager(ABC):
    """Abstract base class for data management operations."""

    @staticmethod
    @abstractmethod
    def load_data(file_path: str) -> Any:
        """Load data from a file."""
        pass

    @staticmethod
    @abstractmethod
    def save_data(file_path: str, data: Any) -> None:
        """Save data to a file."""
        pass

    @staticmethod
    @abstractmethod
    async def load_from_db(query: str, *params: Any) -> Any:
        """Load data from a database."""
        pass

    @staticmethod
    @abstractmethod
    async def save_to_db(query: str, *params: Any) -> None:
        """Save data to a database."""
        pass


class DatabaseManager(DataManager):

    @staticmethod
    async def load_from_db(query: str, *params: Any) -> Any:
        """Load data from a database."""
        return await db.fetch(query, *params)

    @staticmethod
    async def save_to_db(query: str, *params: Any) -> None:
        """Save data to a database."""
        await db.execute(query, *params)


class ReactionRoleManager:
    """Manages reaction role operations, reducing code duplication."""

    def __init__(self, cog: commands.Cog) -> None:
        self.cog = cog

    async def add_buttons_to_message(self, message: discord.Message,
                                     roles_data: List[Dict[str, Any]]) -> None:
        """Add reaction role buttons to a message."""
        guild = message.guild
        view = discord.ui.View(timeout=None)
        for role_data in roles_data:
            role = guild.get_role(int(role_data['role_id']))
            emoji = role_data['emoji']
            color = discord.ButtonStyle(int(role_data['color']))
            custom_id = role_data['custom_id']
            link = role_data.get('link')
            if link and link.lower().startswith(
                ('http://', 'https://', 'discord:')):
                button = discord.ui.Button(url=link, emoji=emoji)
            else:
                button = discord.ui.Button(style=color,
                                           emoji=emoji,
                                           custom_id=custom_id)
                button.callback = self.create_button_callback(role)
            view.add_item(button)
        await message.edit(view=view)

    def create_button_callback(self, role: discord.Role) -> discord.ui.Button:

        async def button_callback(interaction: discord.Interaction) -> None:
            if not self.cog.check_rate_limit(interaction.user.id):
                await interaction.response.send_message(
                    "You're doing that too fast. Please wait a moment.",
                    ephemeral=True)
                return
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"Role {role.name} removed!", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"Role {role.name} assigned!", ephemeral=True)

        return button_callback

    async def handle_message_deletion(self, message: discord.Message) -> None:
        """Handle message deletion events."""
        guild_id = str(message.guild.id)
        message_id = str(message.id)
        if guild_id in self.cog.reaction_roles and message_id in self.cog.reaction_roles[
                guild_id]:
            self.cog.delete_reaction_role(guild_id, message_id)


class ReactionRole(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.role_manager = ReactionRoleManager(self)
        self.reaction_roles: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.tracked_messages: Set[str] = set()
        self.bot.loop.create_task(self.setup_reaction_roles())
        self.rate_limit_dict: Dict[int, float] = {}
        self.bot.loop.create_task(self.cleanup_rate_limit_dict())
        self.bot.loop.create_task(
            db.initialize())  # Initialize the database pool
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self) -> None:
        """Cleanup resources when the cog is unloaded."""
        await self.session.close()
        await db.close()

    def check_rate_limit(self, user_id: int) -> bool:
        """Check if a user has exceeded the rate limit for button clicks."""
        current_time = asyncio.get_event_loop().time()
        if user_id in self.rate_limit_dict:
            last_time = self.rate_limit_dict[user_id]
            if current_time - last_time < RATE_LIMIT_INTERVAL:
                return False
        self.rate_limit_dict[user_id] = current_time
        return True

    async def cleanup_rate_limit_dict(self) -> None:
        """Periodically clean up the rate limit dictionary to prevent memory leaks."""
        while not self.bot.is_closed():
            current_time = asyncio.get_event_loop().time()
            self.rate_limit_dict = {
                user_id: last_time
                for user_id, last_time in self.rate_limit_dict.items()
                if current_time - last_time < RATE_LIMIT_INTERVAL
            }
            await asyncio.sleep(RATE_LIMIT_CLEANUP_INTERVAL)

    async def save_reaction_roles(self) -> None:
        """Save the current reaction roles data to the database."""
        try:
            # Start a database transaction
            await db.execute("BEGIN")

            # Iterate through the saved reaction roles in memory
            for guild_id, messages in self.reaction_roles.items():
                for message_id, roles_data in messages.items():
                    for role_data in roles_data:
                        # Insert the reaction role data into the database
                        # If a conflict occurs on the (guild_id, message_id, role_id) combination,
                        # update the existing record with the new data
                        await db.execute(
                            """INSERT INTO reaction_roles(guild_id, message_id, role_id, channel_id, emoji, color, custom_id, link)
                               VALUES($1, $2, $3, $4, $5, $6, $7, $8)
                               ON CONFLICT (guild_id, message_id, role_id)
                               DO UPDATE SET channel_id = EXCLUDED.channel_id,
                                             emoji = EXCLUDED.emoji,
                                             color = EXCLUDED.color,
                                             custom_id = EXCLUDED.custom_id,
                                             link = EXCLUDED.link""",
                            # Bind the values for the SQL query
                            str(guild_id),  # Guild ID
                            str(message_id),  # Message ID
                            str(role_data['role_id']),  # Role ID
                            str(role_data['channel_id']),  # Channel ID
                            str(role_data['emoji']),  # Emoji
                            str(role_data['color']),  # Color
                            str(role_data['custom_id']
                                ),  # Custom ID for the button
                            str(role_data.get(
                                'link', ''))  # Optional link for the button
                        )

            # Commit the transaction to save all changes to the database
            await db.execute("COMMIT")

        except Exception as e:
            # If an error occurs, roll back the transaction to prevent partial updates
            await db.execute("ROLLBACK")
            print(f"Error saving reaction roles: {e}")

    async def save_tracked_messages(self) -> None:
        """Save the current tracked messages to the database."""
        try:
            await db.execute("BEGIN")
            await db.execute("DELETE FROM tracked_messages")
            for message_id in self.tracked_messages:
                await db.execute(
                    "INSERT INTO tracked_messages(message_id) VALUES($1) ON CONFLICT (message_id) DO NOTHING",
                    str(message_id))
            await db.execute("COMMIT")
        except Exception as e:
            await db.execute("ROLLBACK")
            print(f"Error saving tracked messages: {e}")

    async def setup_reaction_roles(self) -> None:
        """Setup reaction roles when the bot starts."""
        await self.bot.wait_until_ready()
        to_delete: List[Tuple[str, Optional[str]]] = []

        try:
            reaction_roles_data = await db.fetch("SELECT * FROM reaction_roles"
                                                 )
            tracked_messages_data = await db.fetch(
                "SELECT message_id FROM tracked_messages")
        except Exception as e:
            print(f"Error fetching data: {e}")
            return

        self.reaction_roles = {}
        for record in reaction_roles_data:
            guild_id = str(record['guild_id'])
            message_id = str(record['message_id'])
            if guild_id not in self.reaction_roles:
                self.reaction_roles[guild_id] = {}
            if message_id not in self.reaction_roles[guild_id]:
                self.reaction_roles[guild_id][message_id] = []
            self.reaction_roles[guild_id][message_id].append({
                'role_id':
                str(record['role_id']),
                'channel_id':
                str(record['channel_id']),
                'emoji':
                str(record['emoji']),
                'color':
                str(record['color']),
                'custom_id':
                str(record['custom_id']),
                'link':
                str(record['link']) if record['link'] else None
            })

        self.tracked_messages = set(
            str(record['message_id']) for record in tracked_messages_data)
        for guild_id, messages in self.reaction_roles.items():
            guild = self.bot.get_guild(int(guild_id))
            if guild is None:
                to_delete.append((guild_id, None))
                continue
            for message_id, roles_data in messages.items():
                channel = self.bot.get_channel(int(
                    roles_data[0]['channel_id']))
                if channel:
                    try:
                        message = await channel.fetch_message(int(message_id))
                        await self.role_manager.add_buttons_to_message(
                            message, roles_data)
                        self.tracked_messages.add(str(message_id))
                    except discord.NotFound:
                        to_delete.append((guild_id, message_id))
                await asyncio.sleep(0.1)

        for entry in to_delete:
            guild_id, message_id = entry
            if message_id:
                self.delete_reaction_role(guild_id, message_id)
            else:
                del self.reaction_roles[guild_id]

        await self.save_reaction_roles()
        await self.save_tracked_messages()

    def delete_reaction_role(self, guild_id: str, message_id: str) -> None:
        """Delete a reaction role from the saved data."""
        if guild_id in self.reaction_roles and message_id in self.reaction_roles[
                guild_id]:
            del self.reaction_roles[guild_id][message_id]
            if not self.reaction_roles[guild_id]:
                del self.reaction_roles[guild_id]
        asyncio.create_task(self.save_reaction_roles())
        self.tracked_messages.discard(int(message_id))
        asyncio.create_task(self.save_tracked_messages())

    @commands.Cog.listener()
    async def on_guild_channel_delete(
            self, channel: discord.abc.GuildChannel) -> None:
        """Event listener for channel deletions."""
        guild_id = str(channel.guild.id)
        if guild_id in self.reaction_roles:
            messages_to_delete = [
                message_id for message_id, roles_data in
                self.reaction_roles[guild_id].items()
                if roles_data[0]['channel_id'] == str(channel.id)
            ]
            for message_id in messages_to_delete:
                self.delete_reaction_role(guild_id, message_id)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        """Event listener for message deletions."""
        await self.role_manager.handle_message_deletion(message)

    async def get_emoji_choices(
            self, interaction: discord.Interaction
    ) -> List[app_commands.Choice[str]]:
        """Get a list of custom emoji choices for the guild."""
        return [
            app_commands.Choice(name=emoji.name, value=str(emoji.id))
            for emoji in interaction.guild.emojis
        ][:25]

    @app_commands.command(name="reaction-role",
                          description="Add a reaction role to a message")
    @app_commands.describe(
        message_link="The message link or ID to add the reaction role to",
        role="The role to assign",
        emoji=
        "The emoji to use on the button (can be a Unicode emoji or custom emoji ID)",
        color="The color of the button (optional, default is blurple)",
        link="A URL to make the button a link button (optional)")
    @app_commands.choices(color=[
        ColorChoice.Red, ColorChoice.Green, ColorChoice.Blurple,
        ColorChoice.Gray
    ])
    async def reaction_role(self,
                            interaction: discord.Interaction,
                            message_link: str,
                            role: discord.Role,
                            emoji: str,
                            color: Optional[str] = None,
                            link: Optional[str] = None) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            message_id, channel_id = self.parse_message_link(
                message_link, interaction.channel.id)
            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                raise ValueError("Channel not found.")
            message = await channel.fetch_message(message_id)
            color = ColorMapping.get_style(color if color else "blurple")

            if emoji.isdigit():
                emoji_obj = discord.utils.get(interaction.guild.emojis,
                                              id=int(emoji))
                if not emoji_obj:
                    raise ValueError("Invalid custom emoji ID.")
                emoji = str(emoji_obj)
            guild_id = str(interaction.guild.id)
            message_id = str(message.id)
            if guild_id not in self.reaction_roles:
                self.reaction_roles[guild_id] = {}
            if message_id not in self.reaction_roles[guild_id]:
                self.reaction_roles[guild_id][message_id] = []
            custom_id = ''.join(
                random.choices(string.ascii_letters + string.digits, k=20))
            new_role_data = {
                "role_id": str(role.id),
                "channel_id": str(channel.id),
                "emoji": emoji,
                "color": color.value,
                "custom_id": custom_id,
                "link": link
            }
            self.reaction_roles[guild_id][message_id].append(new_role_data)
            await self.save_reaction_roles()
            await self.role_manager.add_buttons_to_message(
                message, self.reaction_roles[guild_id][message_id])
            self.tracked_messages.add(int(message_id))
            await self.save_tracked_messages()
            await interaction.followup.send(
                "Reaction role added successfully!", ephemeral=True)
        except (ValueError, discord.NotFound, discord.HTTPException) as e:
            await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)

    @staticmethod
    def parse_message_link(message_link: str,
                           default_channel_id: int) -> Tuple[int, int]:
        """Parse a message link or ID to get message and channel IDs."""
        if "/" in message_link:
            message_id = int(message_link.split("/")[-1])
            channel_id = int(message_link.split("/")[-2])
        else:
            message_id = int(message_link)
            channel_id = default_channel_id
        return message_id, channel_id

    @app_commands.command(
        name="reaction-role-summary",
        description=
        "Show a summary of all configured reaction roles and sync data")
    @app_commands.checks.cooldown(1,
                                  10.0,
                                  key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reaction_role_summary(self,
                                    interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        invalid_entries = await self.sync_reaction_roles()
        guild_id = str(interaction.guild.id)
        if guild_id not in self.reaction_roles or not self.reaction_roles[
                guild_id]:
            await interaction.followup.send(
                "No reaction roles configured in this server.", ephemeral=True)
            return
        channel_ids = {
            int(roles_data[0]['channel_id'])
            for roles_data in self.reaction_roles[guild_id].values()
        }
        options = [
            discord.SelectOption(
                label=interaction.guild.get_channel(channel_id).name,
                value=str(channel_id)) for channel_id in channel_ids
            if interaction.guild.get_channel(channel_id)
        ]
        if not options:
            await interaction.followup.send(
                "No valid channels with reaction roles found.", ephemeral=True)
            return
        view = ChannelSelectView(self, options)
        embed = discord.Embed(
            title="📊 __**Reaction Roles Summary**__",
            description=
            "```yaml\nSelect a channel below to view its configured reaction roles:```",
            color=discord.Color.blurple())
        embed.add_field(
            name="📌 __Total Channels__",
            value=f"```css\n{len(options)} channel(s) with reaction roles```",
            inline=False)
        embed.add_field(
            name="ℹ️ __How to Use__",
            value=(
                "1️⃣ Choose a channel from the dropdown menu\n"
                "2️⃣ View the overview and reaction roles for that channel\n"
                "3️⃣ Use navigation buttons to browse multiple messages\n"
                "4️⃣ Manage roles using the `/reaction-role` command"),
            inline=False)
        embed.add_field(
            name="🔄 __Sync Results__",
            value=
            f"```diff\n{'+' if invalid_entries > 0 else '-'}{invalid_entries} invalid entries removed```",
            inline=False)
        embed.set_thumbnail(
            url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(
            text=
            f"Requested by {interaction.user} | Server: {interaction.guild.name}",
            icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @reaction_role_summary.error
    async def reaction_role_summary_error(
            self, interaction: discord.Interaction,
            error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
                ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You don't have the required permissions to use this command.",
                ephemeral=True)
        else:
            await interaction.response.send_message(
                "An error occurred while executing this command.",
                ephemeral=True)

    async def sync_reaction_roles(self) -> int:
        """Sync reaction roles data with current server state."""
        to_delete: List[Tuple[str, Optional[str]]] = []
        for guild_id, messages in self.reaction_roles.items():
            guild = self.bot.get_guild(int(guild_id))
            if guild is None:
                to_delete.append((guild_id, None))
                continue
            for message_id, roles_data in messages.items():
                channel = self.bot.get_channel(int(
                    roles_data[0]['channel_id']))
                if channel:
                    try:
                        await channel.fetch_message(int(message_id))
                    except discord.NotFound:
                        to_delete.append((guild_id, message_id))
                        self.tracked_messages.discard(int(message_id))
                else:
                    to_delete.append((guild_id, message_id))
                    self.tracked_messages.discard(int(message_id))

        for entry in to_delete:
            guild_id, message_id = entry
            if message_id:
                self.delete_reaction_role(guild_id, message_id)
            else:
                del self.reaction_roles[guild_id]

        await self.save_reaction_roles()
        await self.save_tracked_messages()
        return len(to_delete)

    async def create_message_reaction_roles_embed(
            self, guild: discord.Guild, channel: discord.TextChannel,
            message_id: str) -> discord.Embed:
        embed = discord.Embed(
            title=f"🎭 __Reaction Roles in #{channel.name}__",
            description="```yaml\nConfigured reaction roles for message:```",
            color=discord.Color.blurple())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        guild_id = str(guild.id)
        if guild_id not in self.reaction_roles or message_id not in self.reaction_roles[
                guild_id]:
            embed.add_field(name="Error",
                            value="No reaction roles found for this message.",
                            inline=False)
            return embed
        roles_data = self.reaction_roles[guild_id][message_id]
        message_link = f"https://discord.com/channels/{guild_id}/{channel.id}/{message_id}"
        field_value = f"[🔗 Jump to Message]({message_link})\n\n"
        for role_data in roles_data:
            role = guild.get_role(int(role_data['role_id']))
            emoji = role_data['emoji']
            field_value += f"{emoji} {role.mention if role else 'Unknown Role'}\n"
        embed.add_field(name=f"📝 __Message ID: {message_id}__",
                        value=field_value,
                        inline=False)
        embed.set_footer(
            text=f"Use /reaction-role to add or modify roles • {guild.name}",
            icon_url=guild.icon.url if guild.icon else None)
        embed.timestamp = discord.utils.utcnow()
        return embed

    async def create_channel_reaction_roles_embed(
            self, guild: discord.Guild,
            channel: discord.TextChannel) -> discord.Embed:
        embed = discord.Embed(
            title=f"🎭 __Reaction Roles in #{channel.name}__",
            description=
            "```yaml\nOverview of reaction roles in this channel:```",
            color=discord.Color.blurple())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        guild_id = str(guild.id)
        channel_id = str(channel.id)
        message_count = sum(
            1 for roles_data in self.reaction_roles.get(guild_id, {}).values()
            if roles_data[0]['channel_id'] == channel_id)
        role_count = sum(
            len(roles_data)
            for roles_data in self.reaction_roles.get(guild_id, {}).values()
            if roles_data[0]['channel_id'] == channel_id)
        embed.add_field(
            name="📊 __Summary__",
            value=
            f"```css\nTotal Messages: {message_count}\nTotal Roles: {role_count}```",
            inline=False)
        embed.set_footer(
            text=f"Use the navigation buttons to view details • {guild.name}",
            icon_url=guild.icon.url if guild.icon else None)
        embed.timestamp = discord.utils.utcnow()
        return embed


async def setup(bot: commands.Bot) -> None:
    """Setup the ReactionRole cog."""
    await bot.add_cog(ReactionRole(bot))
