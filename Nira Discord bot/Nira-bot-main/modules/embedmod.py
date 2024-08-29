import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
from discord import ButtonStyle, Interaction
from utils.helpembed import get_help_embed
import asyncio
import re
from discord.utils import format_dt
from datetime import timedelta
from math import ceil
from typing import Optional


class BaseView(discord.ui.View):

    def __init__(self,
                 bot: commands.Bot,
                 embed: discord.Embed = None,
                 current_page: int = 1,
                 total_pages: int = 16):
        super().__init__(timeout=None)
        self.bot = bot
        self.embed = embed
        self.current_page = current_page
        self.total_pages = total_pages

    def add_navigation_buttons(self) -> None:
        if self.current_page > 1:
            self.add_item(PreviousButton(self.current_page, self.total_pages))
        if self.current_page < self.total_pages:
            self.add_item(NextButton(self.current_page, self.total_pages))
        self.add_item(JumpToPageButton())

    def add_embed_buttons(self) -> None:
        self.add_item(SendButton(self.embed))
        self.add_item(SendToButton(self.embed))
        self.add_item(ResetButton(self.embed))
        self.add_item(FieldsButton())
        self.add_item(PlusButton(self.embed))
        self.add_item(MinusButton(self.embed))
        self.add_item(HelpButton())
        self.add_item(EditFieldButton(self.embed, self.bot))


class BaseButton(discord.ui.Button):

    def __init__(self,
                 label: str,
                 style: ButtonStyle,
                 emoji: str = None,
                 row: int = None,
                 disabled: bool = False):
        super().__init__(label=label,
                         style=style,
                         emoji=emoji,
                         row=row,
                         disabled=disabled)

    async def callback(self, interaction: Interaction) -> None:
        await self.handle_callback(interaction)

    async def handle_callback(self, interaction: Interaction) -> None:
        raise NotImplementedError(
            "Subclasses must implement handle_callback method")


class BaseModal(discord.ui.Modal):

    def __init__(self, title: str, *args, **kwargs):
        super().__init__(title=title, *args, **kwargs)

    async def on_submit(self, interaction: Interaction) -> None:
        await self.handle_submit(interaction)

    async def handle_submit(self, interaction: Interaction) -> None:
        raise NotImplementedError(
            "Subclasses must implement handle_submit method")


class AuthorModal(BaseModal):

    def __init__(self,
                 embed: discord.Embed,
                 bot: commands.Bot,
                 is_edit: bool = False):
        super().__init__(title="Configure Author")
        self.embed = embed
        self.bot = bot
        self.is_edit = is_edit
        self.author = TextInput(label="Author Name",
                                default=self.embed.author.name
                                if is_edit and self.embed.author else None)
        self.author_url = TextInput(label="Author URL",
                                    required=False,
                                    default=self.embed.author.url
                                    if is_edit and self.embed.author else None)
        self.author_icon_url = TextInput(
            label="Author Icon URL",
            required=False,
            default=self.embed.author.icon_url
            if is_edit and self.embed.author else None)
        self.add_item(self.author)
        self.add_item(self.author_url)
        self.add_item(self.author_icon_url)

    async def handle_submit(self, interaction: discord.Interaction) -> None:
        await self._validate_and_set_author(interaction)

    async def _validate_and_set_author(
            self, interaction: discord.Interaction) -> None:
        if self.author_url.value and not self.bot.get_cog(
                "EmbedCreator").is_valid_url(self.author_url.value):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description=
                    f"Invalid URL in Author URL: {self.author_url.value}",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        if self.author_icon_url.value and not self.bot.get_cog(
                "EmbedCreator").is_valid_url(self.author_icon_url.value):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description=
                    f"Invalid URL in Author Icon URL: {self.author_icon_url.value}",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        self.embed.set_author(
            name=self.author.value,
            url=self.author_url.value or None,
            icon_url=self.author_icon_url.value or None,
        )
        await interaction.response.edit_message(content="✅ Author configured.",
                                                embed=self.embed,
                                                view=create_embed_view(
                                                    self.embed,
                                                    interaction.client))


class BodyModal(BaseModal):

    def __init__(self,
                 embed: discord.Embed,
                 bot: commands.Bot,
                 is_edit: bool = False):
        super().__init__(title="Configure Body")
        self.embed = embed
        self.bot = bot
        self.is_edit = is_edit
        self.titl = TextInput(label="Title",
                              max_length=256,
                              default=self.embed.title if is_edit else None,
                              required=False)
        self.description = TextInput(
            label="Description",
            max_length=4000,
            style=discord.TextStyle.paragraph,
            default=self.embed.description if is_edit else None)
        self.url = TextInput(label="URL",
                             required=False,
                             default=self.embed.url if is_edit else None)
        self.color = TextInput(label="Color (hex code, name, or 'random')",
                               required=False,
                               default=self.embed.color.value
                               if is_edit and self.embed.color else None)
        self.add_item(self.titl)
        self.add_item(self.description)
        self.add_item(self.url)
        self.add_item(self.color)

    async def handle_submit(self, interaction: discord.Interaction) -> None:
        await self._validate_and_set_body(interaction)

    async def _validate_and_set_body(self,
                                     interaction: discord.Interaction) -> None:
        if self.url.value and not self.bot.get_cog(
                "EmbedCreator").is_valid_url(self.url.value):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description=f"Invalid URL in Body URL: {self.url.value}",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        if self.color.value:
            if self.color.value.lower() == "random":
                self.embed.color = discord.Color.random()
            elif self.bot.get_cog("EmbedCreator").is_valid_hex_color(
                    self.color.value):
                self.embed.color = discord.Color(
                    int(self.color.value.strip("#"), 16))
            else:
                color = self.bot.get_cog("EmbedCreator").get_color_from_name(
                    self.color.value)
                if color:
                    self.embed.color = color
                else:
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title="Error",
                            description=
                            f"Invalid color value: {self.color.value}",
                            color=discord.Color.red(),
                        ),
                        ephemeral=True,
                    )
                    return

        self.embed.title = self.titl.value
        self.embed.description = self.description.value or None
        self.embed.url = self.url.value or None

        await interaction.response.edit_message(content="✅ Body configured.",
                                                embed=self.embed,
                                                view=create_embed_view(
                                                    self.embed,
                                                    interaction.client))


class ImagesModal(BaseModal):

    def __init__(self,
                 embed: discord.Embed,
                 bot: commands.Bot,
                 is_edit: bool = False):
        super().__init__(title="Configure Images")
        self.embed = embed
        self.bot = bot
        self.is_edit = is_edit
        self.image_url = TextInput(label="Image URL",
                                   required=False,
                                   default=self.embed.image.url
                                   if is_edit and self.embed.image else None)
        self.thumbnail_url = TextInput(
            label="Thumbnail URL",
            required=False,
            default=self.embed.thumbnail.url
            if is_edit and self.embed.thumbnail else None)
        self.add_item(self.image_url)
        self.add_item(self.thumbnail_url)

    async def handle_submit(self, interaction: discord.Interaction) -> None:
        await self._validate_and_set_images(interaction)

    async def _validate_and_set_images(
            self, interaction: discord.Interaction) -> None:
        if self.image_url.value and not self.bot.get_cog(
                "EmbedCreator").is_valid_url(self.image_url.value):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description=
                    f"Invalid URL in Image URL: {self.image_url.value}",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        if self.thumbnail_url.value and not self.bot.get_cog(
                "EmbedCreator").is_valid_url(self.thumbnail_url.value):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description=
                    f"Invalid URL in Thumbnail URL: {self.thumbnail_url.value}",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        self.embed.set_image(url=self.image_url.value or None)
        self.embed.set_thumbnail(url=self.thumbnail_url.value or None)

        await interaction.response.edit_message(content="✅ Images configured.",
                                                embed=self.embed,
                                                view=create_embed_view(
                                                    self.embed,
                                                    interaction.client))


class FooterModal(BaseModal):

    def __init__(self,
                 embed: discord.Embed,
                 bot: commands.Bot,
                 is_edit: bool = False):
        super().__init__(title="Configure Footer")
        self.embed = embed
        self.bot = bot
        self.is_edit = is_edit
        self.footer = TextInput(label="Footer Text",
                                max_length=2048,
                                default=self.embed.footer.text
                                if is_edit and self.embed.footer else None)
        self.timestamp = TextInput(
            label="Timestamp (YYYY-MM-DD hh:mm or 'auto')",
            required=False,
            default=self.embed.timestamp.strftime("%Y-%m-%d %H:%M")
            if is_edit and self.embed.timestamp else None)
        self.footer_icon_url = TextInput(
            label="Footer Icon URL",
            required=False,
            default=self.embed.footer.icon_url
            if is_edit and self.embed.footer else None)
        self.add_item(self.footer)
        self.add_item(self.timestamp)
        self.add_item(self.footer_icon_url)

    async def handle_submit(self, interaction: discord.Interaction) -> None:
        await self._validate_and_set_footer(interaction)

    async def _validate_and_set_footer(
            self, interaction: discord.Interaction) -> None:
        if self.footer_icon_url.value and not self.bot.get_cog(
                "EmbedCreator").is_valid_url(self.footer_icon_url.value):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description=
                    f"Invalid URL in Footer Icon URL: {self.footer_icon_url.value}",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        self.embed.set_footer(
            text=self.footer.value,
            icon_url=self.footer_icon_url.value or None,
        )

        if self.timestamp.value:
            if self.timestamp.value.lower() == "auto":
                self.embed.timestamp = discord.utils.utcnow()
            else:
                try:
                    self.embed.timestamp = discord.utils.parse_time(
                        self.timestamp.value)
                except ValueError:
                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title="Error",
                            description=
                            f"Invalid timestamp format: {self.timestamp.value}",
                            color=discord.Color.red(),
                        ),
                        ephemeral=True,
                    )
                    return
        else:
            self.embed.timestamp = None

        await interaction.response.edit_message(content="✅ Footer configured.",
                                                embed=self.embed,
                                                view=create_embed_view(
                                                    self.embed,
                                                    interaction.client))


class AddFieldModal(BaseModal):

    def __init__(self, embed: discord.Embed):
        super().__init__(title="Add Field")
        self.embed = embed
        self.field_name = TextInput(label="Field Name")
        self.field_value = TextInput(label="Field Value")
        self.inline = TextInput(label="Inline (True/False)", required=False)
        self.add_item(self.field_name)
        self.add_item(self.field_value)
        self.add_item(self.inline)

    async def handle_submit(self, interaction: discord.Interaction) -> None:
        name = self.field_name.value
        value = self.field_value.value
        inline = self.inline.value.lower(
        ) == "true" if self.inline.value else False
        self.embed.add_field(name=name, value=value, inline=inline)
        await interaction.response.edit_message(content="✅ Field added.",
                                                embed=self.embed,
                                                view=create_embed_view(
                                                    self.embed,
                                                    interaction.client))


class JumpToPageModal(Modal):
    """Modal to input the page number for jumping to a specific help page."""

    def __init__(self) -> None:
        """Initialize the modal with input for the page number."""
        super().__init__(title="Jump to Page")
        self.page_number = TextInput(
            label="Page Number",
            placeholder="Enter a page number between 1 and 16",
            required=True)
        self.add_item(self.page_number)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle the submission of the jump to page modal."""
        try:
            page = int(self.page_number.value)
            if 1 <= page <= 16:
                await interaction.response.edit_message(
                    embed=get_help_embed(page),
                    view=HelpNavigationView(interaction.client, page, 16))
            else:
                await interaction.response.send_message(
                    "Please enter a valid page number (1-16).", ephemeral=True)
        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid page number (1-16).", ephemeral=True)


class ScheduleModal(Modal):

    def __init__(self, embed: discord.Embed, bot: commands.Bot,
                 original_channel: discord.TextChannel):
        super().__init__(title="Schedule Embed")
        self.embed = embed
        self.bot = bot
        self.original_channel = original_channel
        self.schedule_time = TextInput(label="Schedule Time",
                                       placeholder="e.g., 1m, 1h, 1d, 1w",
                                       required=True)
        self.channel = TextInput(
            label="Channel ID (optional)",
            placeholder="Leave blank to use current channel",
            required=False)
        self.add_item(self.schedule_time)
        self.add_item(self.channel)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if not is_embed_configured(self.embed):
            await interaction.response.send_message(
                "Error: The embed has not been configured yet. Please add some content before scheduling.",
                ephemeral=True)
            return

        schedule_time = self.schedule_time.value
        channel_id = self.channel.value
        channel = await self._get_channel(channel_id, interaction)

        if not channel:
            return

        delay = self._parse_schedule_time(schedule_time)
        if delay is None:
            await interaction.response.send_message(
                "Invalid schedule time format. Please use formats like '5m', '2h', '1d', or '1w'.",
                ephemeral=True)
            return

        scheduled_time = discord.utils.utcnow() + delay
        scheduled_time_str = format_dt(scheduled_time, style='R')
        await interaction.response.send_message(
            f"Embed scheduled to be sent in {channel.mention} {scheduled_time_str}",
            ephemeral=True)

        await self._schedule_embed(delay, channel, interaction)

    def _parse_schedule_time(self, schedule_time: str) -> Optional[timedelta]:
        match = re.match(r'^(\d+)([mhdw])$', schedule_time.lower())
        if match:
            amount, unit = match.groups()
            amount = int(amount)
            if unit == 'm':
                return timedelta(minutes=amount)
            elif unit == 'h':
                return timedelta(hours=amount)
            elif unit == 'd':
                return timedelta(days=amount)
            elif unit == 'w':
                return timedelta(weeks=amount)
        return None

    async def _get_channel(
            self, channel_id: str,
            interaction: discord.Interaction) -> Optional[discord.TextChannel]:
        if channel_id:
            try:
                channel = self.bot.get_channel(int(channel_id))
                if not channel:
                    raise ValueError("Invalid channel ID")
            except ValueError:
                await interaction.response.send_message(
                    "Invalid channel ID. Using the current channel instead.",
                    ephemeral=True)
                return self.original_channel
        else:
            return self.original_channel

    async def _schedule_embed(self, delay: timedelta,
                              channel: discord.TextChannel,
                              interaction: discord.Interaction) -> None:
        scheduled_time = discord.utils.utcnow() + delay
        await asyncio.sleep(delay.total_seconds())
        sent_message = await channel.send(embed=self.embed)
        message_link = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{sent_message.id}"
        user = interaction.user
        scheduled_time_str = format_dt(scheduled_time, style='R')
        await user.send(
            f"Your scheduled embed has been sent {scheduled_time_str}! {message_link}"
        )


class PlusButton(BaseButton):

    def __init__(self, embed: discord.Embed):
        super().__init__(label="", style=ButtonStyle.green, emoji="➕", row=2)
        self.embed = embed

    async def handle_callback(self, interaction: Interaction) -> None:
        await interaction.response.send_modal(AddFieldModal(self.embed))


class EditFieldModal(BaseModal):

    def __init__(self, embed: discord.Embed, field_index: int):
        super().__init__(title=f"Edit Field {field_index + 1}")
        self.embed = embed
        self.field_index = field_index
        field = self.embed.fields[field_index]
        self.field_name = TextInput(label="Field Name", default=field.name)
        self.field_value = TextInput(label="Field Value", default=field.value)
        self.inline = TextInput(label="Inline (True/False)",
                                default=str(field.inline),
                                required=False)
        self.add_item(self.field_name)
        self.add_item(self.field_value)
        self.add_item(self.inline)

    async def handle_submit(self, interaction: discord.Interaction) -> None:
        name = self.field_name.value
        value = self.field_value.value
        inline = self.inline.value.lower(
        ) == "true" if self.inline.value else False
        self.embed.set_field_at(self.field_index,
                                name=name,
                                value=value,
                                inline=inline)
        await interaction.response.edit_message(content="✅ Field updated.",
                                                embed=self.embed,
                                                view=create_embed_view(
                                                    self.embed,
                                                    interaction.client))


class MinusButton(BaseButton):

    def __init__(self, embed: discord.Embed):
        super().__init__(label="", style=ButtonStyle.red, emoji="➖", row=2)
        self.embed = embed

    async def handle_callback(self, interaction: Interaction) -> None:
        if not self.embed.fields:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Error",
                    description="No fields available to remove.",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        options = [
            discord.SelectOption(label=f"Field {i + 1}: {field.name}",
                                 value=str(i),
                                 description=field.value[:100])
            for i, field in enumerate(self.embed.fields)
        ]
        view = View(timeout=None)
        select = discord.ui.Select(placeholder="Select a field to remove...",
                                   options=options)
        select.callback = self.remove_field_callback
        view.add_item(select)
        view.add_item(BackButton(self.embed))
        await interaction.response.edit_message(
            content="Select a field to remove:", embed=self.embed, view=view)

    async def remove_field_callback(self, interaction: Interaction) -> None:
        value = interaction.data["values"][0]
        field_index = int(value)
        self.embed.remove_field(field_index)
        if not self.embed.description:
            self.embed.description = "\u200b"  # Zero-width space
        await interaction.response.edit_message(content="✅ Field removed.",
                                                embed=self.embed,
                                                view=create_embed_view(
                                                    self.embed,
                                                    interaction.client))


class BackButton(BaseButton):

    def __init__(self, embed: discord.Embed):
        super().__init__(label="Back", style=ButtonStyle.secondary)
        self.embed = embed

    async def handle_callback(self, interaction: Interaction) -> None:
        await interaction.response.edit_message(
            content="Embed Configuration Preview:",
            embed=self.embed,
            view=create_embed_view(self.embed, interaction.client))


class SendButton(BaseButton):

    def __init__(self, embed: discord.Embed):
        super().__init__(label="Send", style=ButtonStyle.green, emoji="🚀")
        self.embed = embed

    async def handle_callback(self, interaction: Interaction) -> None:
        if not is_embed_configured(self.embed):
            await interaction.response.send_message(embed=discord.Embed(
                title="Error",
                description=
                "The embed has not been configured yet. Please add some content before sending.",
                color=discord.Color.red()),
                                                    ephemeral=True)
            return

        sent_message = await interaction.channel.send(embed=self.embed)
        message_link = f"https://discord.com/channels/{interaction.guild.id}/{interaction.channel.id}/{sent_message.id}"
        await interaction.response.edit_message(
            content=
            f"✅ Embed sent! {message_link}. You can continue editing or send it again.",
            embed=self.embed,
            view=create_embed_view(self.embed, interaction.client))


class ResetButton(BaseButton):

    def __init__(self, embed: discord.Embed):
        super().__init__(label="Reset", style=ButtonStyle.red, emoji="🔄")
        self.embed = embed

    async def handle_callback(self, interaction: Interaction) -> None:
        new_embed = discord.Embed(description="** **")
        new_embed.color = self.embed.color
        self.embed = new_embed
        await interaction.response.edit_message(content="✅ Embed reset.",
                                                embed=self.embed,
                                                view=create_embed_view(
                                                    self.embed,
                                                    interaction.client))


class HelpButton(BaseButton):

    def __init__(self):
        super().__init__(label="Help",
                         style=ButtonStyle.grey,
                         emoji="🔍",
                         row=3)

    async def handle_callback(self, interaction: Interaction) -> None:
        await interaction.response.send_message(embed=get_help_embed(1),
                                                view=HelpNavigationView(
                                                    interaction.client, 1, 10),
                                                ephemeral=True)


class JumpToPageButton(BaseButton):

    def __init__(self):
        super().__init__(label="Jump to Page",
                         style=ButtonStyle.grey,
                         emoji="🔍")

    async def handle_callback(self, interaction: Interaction) -> None:
        await interaction.response.send_modal(JumpToPageModal())


class PreviousButton(BaseButton):

    def __init__(self, current_page: int, total_pages: int):
        super().__init__(label="Previous",
                         style=discord.ButtonStyle.blurple,
                         disabled=current_page == 1)
        self.current_page = current_page
        self.total_pages = total_pages

    async def handle_callback(self, interaction: discord.Interaction) -> None:
        new_page = max(1, self.current_page - 1)
        await interaction.response.edit_message(
            embed=get_help_embed(new_page),
            view=HelpNavigationView(interaction.client, new_page,
                                    self.total_pages))


class NextButton(BaseButton):

    def __init__(self, current_page: int, total_pages: int):
        super().__init__(label="Next",
                         style=discord.ButtonStyle.blurple,
                         disabled=current_page == total_pages)
        self.current_page = current_page
        self.total_pages = total_pages

    async def handle_callback(self, interaction: discord.Interaction) -> None:
        new_page = min(self.total_pages, self.current_page + 1)
        await interaction.response.edit_message(
            embed=get_help_embed(new_page),
            view=HelpNavigationView(interaction.client, new_page,
                                    self.total_pages))


class EditFieldButton(BaseButton):

    def __init__(self, embed: discord.Embed, bot: commands.Bot):
        super().__init__(label="Edit Fields",
                         style=ButtonStyle.grey,
                         emoji="📝",
                         row=2)
        self.embed = embed
        self.bot = bot

    async def handle_callback(self, interaction: Interaction) -> None:
        if not self.embed.fields:
            await interaction.response.send_message(embed=discord.Embed(
                title="Error",
                description="No fields have been added to the embed yet.",
                color=discord.Color.red()),
                                                    ephemeral=True)
            return

        options = [
            discord.SelectOption(label=f"Field {i + 1}: {field.name}",
                                 value=f"field_{i}",
                                 description=field.value[:100])
            for i, field in enumerate(self.embed.fields)
        ]
        view = View(timeout=None)
        select = discord.ui.Select(placeholder="Select a field to edit...",
                                   options=options)
        select.callback = self.edit_field_callback
        view.add_item(select)
        view.add_item(BackButton(self.embed))
        await interaction.response.edit_message(
            content="Select a field to edit:", embed=self.embed, view=view)

    async def edit_field_callback(self, interaction: Interaction) -> None:
        value = interaction.data["values"][0]
        field_index = int(value.split("_")[1])
        await interaction.response.send_modal(
            EditFieldModal(self.embed, field_index))


class SendToButton(BaseButton):

    def __init__(self, embed: discord.Embed):
        super().__init__(label="Send To", style=ButtonStyle.green, emoji="📤")
        self.embed = embed
        self.page = 0  # Current page for pagination

    async def handle_callback(self, interaction: Interaction) -> None:
        if not is_embed_configured(self.embed):
            await interaction.response.send_message(embed=discord.Embed(
                title="Embed Not Configured",
                description=
                "Please configure the embed with some content before attempting to send it.",
                color=discord.Color.red()),
                                                    ephemeral=True)
            return

        channels = [
            channel for channel in interaction.guild.text_channels
            if channel.permissions_for(interaction.user).send_messages
        ]
        if not channels:
            await interaction.response.send_message(
                "You don't have permission to send messages in any channel.",
                ephemeral=True)
            return

        await self._show_channel_page(interaction, channels, self.page)

    async def _show_channel_page(self, interaction: Interaction,
                                 channels: list[discord.TextChannel],
                                 page: int) -> None:
        max_per_page = 25
        start_index = page * max_per_page
        end_index = start_index + max_per_page
        channel_page = channels[start_index:end_index]
        options = [
            discord.SelectOption(label=channel.name, value=str(channel.id))
            for channel in channel_page
        ]
        view = View(timeout=None)
        select = discord.ui.Select(
            placeholder="Select a channel to send the embed to...",
            options=options)
        select.callback = lambda inter: self._send_to_channel_callback(
            inter, channels, page)
        view.add_item(select)

        total_pages = ceil(len(channels) / max_per_page)
        if total_pages > 1:
            if page > 0:
                view.add_item(PreviousPageButton(self, channels, page))
            if page < total_pages - 1:
                view.add_item(NextPageButton(self, channels, page))
        view.add_item(BackButton(self.embed))
        await interaction.response.edit_message(
            content="Select a channel to send the embed to:",
            embed=self.embed,
            view=view)

    async def _send_to_channel_callback(self, interaction: Interaction,
                                        channels: list[discord.TextChannel],
                                        page: int) -> None:
        value = interaction.data["values"][0]
        channel_id = int(value)
        channel = interaction.guild.get_channel(channel_id)
        if channel is None:
            await interaction.response.send_message(
                "The selected channel no longer exists.", ephemeral=True)
            return

        if not is_embed_configured(self.embed):
            await interaction.response.send_message(
                "The embed is not properly configured. Please add some content before sending.",
                ephemeral=True)
            return

        try:
            sent_message = await channel.send(embed=self.embed)
            message_link = f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{sent_message.id}"
            await interaction.response.edit_message(
                content=
                f"✅ Embed sent! {message_link}. You can continue editing or send it again.",
                embed=self.embed,
                view=create_embed_view(self.embed, interaction.client))
        except discord.errors.Forbidden:
            await interaction.response.send_message(
                f"I don't have permission to send messages in #{channel.mention}.",
                ephemeral=True)


class PreviousPageButton(BaseButton):

    def __init__(self, parent: SendToButton,
                 channels: list[discord.TextChannel], current_page: int):
        super().__init__(label="Previous", style=discord.ButtonStyle.blurple)
        self.parent = parent
        self.channels = channels
        self.current_page = current_page

    async def handle_callback(self, interaction: Interaction) -> None:
        self.parent.page = max(0, self.current_page - 1)
        await self.parent._show_channel_page(interaction, self.channels,
                                             self.parent.page)


class NextPageButton(BaseButton):

    def __init__(self, parent: SendToButton,
                 channels: list[discord.TextChannel], current_page: int):
        super().__init__(label="Next", style=discord.ButtonStyle.blurple)
        self.parent = parent
        self.channels = channels
        self.current_page = current_page

    async def handle_callback(self, interaction: Interaction) -> None:
        total_pages = ceil(len(self.channels) / 25)
        self.parent.page = min(total_pages - 1, self.current_page + 1)
        await self.parent._show_channel_page(interaction, self.channels,
                                             self.parent.page)


class FieldsButton(BaseButton):

    def __init__(self):
        super().__init__(label="Fields:",
                         style=ButtonStyle.grey,
                         disabled=True,
                         row=2)

    async def handle_callback(self, interaction: Interaction) -> None:
        # This button is disabled and does nothing, so we don't need to implement any callback logic
        pass


class FieldCountButton(BaseButton):

    def __init__(self, embed: discord.Embed):
        field_count = len(
            embed.fields) if embed and hasattr(embed, 'fields') else 0
        super().__init__(label=f"{field_count}/25 fields",
                         style=ButtonStyle.grey,
                         disabled=True,
                         row=3)
        self.embed = embed

    async def handle_callback(self, interaction: Interaction) -> None:
        # This button is disabled and does nothing, so we don't need to implement any callback logic
        pass


class HelpNavigationView(BaseView):

    def __init__(self,
                 bot: commands.Bot,
                 current_page: int = 1,
                 total_pages: int = 16):
        super().__init__(bot=bot,
                         current_page=current_page,
                         total_pages=total_pages)
        self.add_navigation_buttons()


def create_embed_view(embed: discord.Embed, bot: commands.Bot) -> View:
    view = BaseView(bot, embed)
    select_options = [
        discord.SelectOption(label="Author", value="author", emoji="📝"),
        discord.SelectOption(label="Body", value="body", emoji="📄"),
        discord.SelectOption(label="Images", value="images", emoji="🖼️"),
        discord.SelectOption(label="Footer", value="footer", emoji="🔻"),
        discord.SelectOption(label="Schedule Embed",
                             value="schedule",
                             emoji="🕒"),
    ]
    select = Select(placeholder="Choose a part of the embed to configure...",
                    options=select_options)
    select.callback = bot.get_cog("EmbedCreator").dropdown_callback
    view.add_item(select)
    view.add_item(FieldCountButton(embed))
    view.add_embed_buttons()
    return view


def is_embed_configured(embed: discord.Embed) -> bool:
    return any([
        embed.title, embed.description, embed.fields, embed.author,
        embed.footer, embed.image, embed.thumbnail
    ])
