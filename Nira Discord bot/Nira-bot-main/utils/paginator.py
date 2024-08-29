from __future__ import annotations
from typing import (
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Any,
    TYPE_CHECKING,
    Sequence,
    Union,
)

import discord
from discord.abc import Messageable
from discord.ext import commands

if TYPE_CHECKING:
    from typing_extensions import Self

    Interaction = discord.Interaction[Any]
    Context = commands.Context[Any]

Page = Union[
    str,
    Sequence[str],
    discord.Embed,
    Sequence[discord.Embed],
    discord.File,
    Sequence[discord.File],
    discord.Attachment,
    Sequence[discord.Attachment],
    dict[str, Any],
]

PageT_co = TypeVar("PageT_co", bound=Page, covariant=True)


class ButtonPaginator(Generic[PageT_co], discord.ui.View):
    message: Optional[Union[discord.Message, discord.WebhookMessage]] = None

    def __init__(
        self,
        pages: Sequence[PageT_co],
        *,
        author_id: Optional[int] = None,
        timeout: Optional[float] = 180.0,
        delete_message_after: bool = False,
        per_page: int = 1,
    ) -> None:
        super().__init__(timeout=timeout)
        self.author_id: Optional[int] = author_id
        self.delete_message_after: bool = delete_message_after

        self.current_page: int = 0
        self.per_page: int = per_page
        self.pages: Any = pages
        total_pages, left_over = divmod(len(self.pages), self.per_page)
        if left_over:
            total_pages += 1

        self.max_pages: int = total_pages
        self._page_kwargs: Dict[str, Any] = {
            "content": None,
            "embeds": [],
            "files": [],
            "view": self
        }

    def stop(self) -> None:
        self.message = None
        super().stop()

    async def interaction_check(self, interaction: Interaction) -> bool:
        if not self.author_id:
            return True

        if self.author_id != interaction.user.id:
            await interaction.response.send_message(
                "You cannot interact with this menu.", ephemeral=True)
            return False

        return True

    def get_page(self,
                 page_number: int) -> Union[PageT_co, Sequence[PageT_co]]:
        if page_number < 0 or page_number >= self.max_pages:
            self.current_page = 0
            return self.pages[self.current_page]

        if self.per_page == 1:
            return self.pages[page_number]
        else:
            base = page_number * self.per_page
            return self.pages[base:base + self.per_page]

    def format_page(
        self, page: Union[PageT_co, Sequence[PageT_co]]
    ) -> Union[PageT_co, Sequence[PageT_co]]:
        return page

    async def get_page_kwargs(self,
                              page: Union[PageT_co, Sequence[PageT_co]],
                              skip_formatting: bool = False) -> Dict[str, Any]:
        formatted_page: Union[PageT_co, Sequence[PageT_co]]
        if not skip_formatting:
            self._page_kwargs = {
                "content": None,
                "embeds": [],
                "files": [],
                "view": self
            }
            formatted_page = await discord.utils.maybe_coroutine(
                self.format_page, page)
        else:
            formatted_page = page

        if isinstance(formatted_page, str):
            # idk about this
            content = self._page_kwargs["content"]
            if content is None:
                self._page_kwargs["content"] = formatted_page
            else:
                self._page_kwargs["content"] = f"{content}\n{formatted_page}"
        elif isinstance(formatted_page, discord.Embed):
            self._page_kwargs["embeds"].append(formatted_page)
        elif isinstance(formatted_page, (discord.File, discord.Attachment)):
            if isinstance(formatted_page, discord.Attachment):
                formatted_page = await formatted_page.to_file()  # type: ignore

            self._page_kwargs["files"].append(formatted_page)
        elif isinstance(formatted_page, (tuple, list)):
            for item in formatted_page:
                await self.get_page_kwargs(item, skip_formatting=True
                                           )  # type: ignore
        elif isinstance(formatted_page, dict):
            return formatted_page
        else:
            raise TypeError(
                "Page content must be one of str, discord.Embed, list[discord.Embed], or dict"
            )

        return self._page_kwargs

    def update_buttons(self) -> None:
        self.previous_page.disabled = self.max_pages < 2 or self.current_page <= 0
        self.next_page.disabled = self.max_pages < 2 or self.current_page >= self.max_pages - 1

    async def update_page(self, interaction: Interaction) -> None:
        if self.message is None:
            self.message = interaction.message

        self.update_buttons()
        kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
        self.reset_files(kwargs)
        kwargs["attachments"] = kwargs.pop("files", [])
        await interaction.response.edit_message(**kwargs)

    @discord.ui.button(label="Previous",
                       style=discord.ButtonStyle.blurple,
                       emoji="⬅️")
    async def previous_page(self, interaction: Interaction,
                            _: discord.ui.Button[Self]) -> None:
        self.current_page -= 1
        await self.update_page(interaction)

    @discord.ui.button(label="Next",
                       style=discord.ButtonStyle.blurple,
                       emoji="➡️")
    async def next_page(self, interaction: Interaction,
                        _: discord.ui.Button[Self]) -> None:
        self.current_page += 1
        await self.update_page(interaction)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red, emoji="⏹️")
    async def stop_paginator(self, interaction: Interaction,
                             _: discord.ui.Button[Self]) -> None:
        if self.delete_message_after:
            if self.message is not None:
                await self.message.delete()
        else:
            await interaction.response.send_message("Stopped the paginator.")

        self.stop()

    def reset_files(self, page_kwargs: dict[str, Any]) -> None:
        files: List[discord.File] = page_kwargs.get("files", [])
        if not files:
            return

        for file in files:
            file.reset()

    async def start(
        self, obj: Union[Interaction, Messageable], **send_kwargs: Any
    ) -> Optional[Union[discord.Message, discord.WebhookMessage]]:
        self.update_buttons()
        kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
        if self.max_pages < 2:
            self.stop()
            del kwargs["view"]

        self.reset_files(kwargs)
        if isinstance(obj, discord.Interaction):
            if obj.response.is_done():
                self.message = await obj.followup.send(**kwargs, **send_kwargs)
            else:
                await obj.response.send_message(**kwargs, **send_kwargs)
                self.message = await obj.original_response()

        elif isinstance(obj, Messageable):
            self.message = await obj.send(**kwargs, **send_kwargs)
        else:
            raise TypeError(
                f"Expected Interaction or Messageable, got {obj.__class__.__name__}"
            )

        return self.message  # type: ignore
