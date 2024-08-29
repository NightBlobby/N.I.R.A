import discord
from discord.ext import commands
from discord import ui
import random
from datetime import timedelta, datetime
import asyncio
import aiohttp


class MemoryGameButton(discord.ui.Button):

    def __init__(self, x: int, y: int, emoji: str):
        super().__init__(style=discord.ButtonStyle.secondary, emoji="❓", row=y)
        self.x = x
        self.y = y
        self.hidden_emoji = emoji
        self.revealed = False

    async def callback(self, interaction: discord.Interaction):
        await self.view.process_button(self, interaction)


class MemoryGameView(discord.ui.View):

    def __init__(self, ctx: commands.Context, time_limit: int, cog):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.cog = cog
        self.board = []
        self.selected_buttons = []
        self.moves = 0
        self.pairs_found = 0
        self.start_time = None
        self.message = None
        self.setup_board()
        self.last_interaction_time = None
        self.inactivity_task = None
        self.time_limit = time_limit * 60  # Convert minutes to seconds
        self.timer_task = None
        self.game_started = False
        self.hints_remaining = 2
        self.hints_used = 0

    def setup_board(self):
        guild_emojis = self.ctx.guild.emojis
        pairs_needed = 12
        if len(guild_emojis) < pairs_needed:
            raise ValueError(
                f"Not enough custom emojis in the server! You need at least {pairs_needed}."
            )

        emojis = random.sample(guild_emojis, pairs_needed) * 2
        random.shuffle(emojis)

        for y in range(5):
            for x in range(5):
                if x == 2 and y == 2:
                    self.add_item(
                        ui.Button(style=discord.ButtonStyle.secondary,
                                  emoji="🔒",
                                  disabled=True,
                                  row=y))
                else:
                    button = MemoryGameButton(x, y, emojis.pop())
                    self.add_item(button)
                    self.board.append(button)

    async def start_game(self, existing_message=None):
        for child in self.children:
            child.disabled = True

        initial_content = f"Memory Game: Match the pairs! Time limit: {self.time_limit // 60} minutes\nHints remaining: {self.hints_remaining}\n(Showing the emojis for 7 seconds...)"
        if existing_message:
            self.message = existing_message
            await self.message.edit(content=initial_content,
                                    view=self,
                                    embed=None)
        else:
            self.message = await self.ctx.send(initial_content, view=self)

        await self.reveal_all_emojis()
        await discord.utils.sleep_until(discord.utils.utcnow() +
                                        timedelta(seconds=7))
        await self.hide_all_emojis()

        self.start_time = datetime.now()
        self.last_interaction_time = self.start_time
        self.game_started = True

        for child in self.children:
            if isinstance(child, MemoryGameButton):
                child.disabled = False
        await self.message.edit(content=self.get_game_status(), view=self)

        self.inactivity_task = asyncio.create_task(self.check_inactivity())
        self.timer_task = asyncio.create_task(self.update_timer())

        await self.message.add_reaction("💡")  # Add hint emoji

    def get_game_status(self):
        if not self.game_started:
            return f"Memory Game (5x5): Match the pairs!\nTime limit: {self.time_limit // 60} minutes\nHints remaining: {self.hints_remaining}"

        remaining_time = self.time_limit - (datetime.now() -
                                            self.start_time).total_seconds()
        minutes, seconds = divmod(int(remaining_time), 60)
        return f"Memory Game (5x5): Match the pairs!\nTime remaining: {minutes:02d}:{seconds:02d}\nHints remaining: {self.hints_remaining}"

    async def reveal_all_emojis(self):
        for button in self.board:
            button.emoji = button.hidden_emoji
            button.style = discord.ButtonStyle.secondary
        await self.message.edit(view=self)

    async def hide_all_emojis(self):
        for button in self.board:
            button.emoji = "❓"
            button.style = discord.ButtonStyle.secondary
            button.revealed = False
        await self.message.edit(view=self)

    async def process_button(self, button: MemoryGameButton,
                             interaction: discord.Interaction):
        self.last_interaction_time = datetime.now()
        if not button.revealed:
            button.revealed = True
            button.style = discord.ButtonStyle.success
            button.emoji = button.hidden_emoji
            self.selected_buttons.append(button)
            self.moves += 1

            if len(self.selected_buttons) == 2:
                for child in self.children:
                    if isinstance(child, MemoryGameButton):
                        child.disabled = True
                await interaction.response.edit_message(
                    content=self.get_game_status(), view=self)

                btn1, btn2 = self.selected_buttons
                if btn1.hidden_emoji == btn2.hidden_emoji:
                    btn1.disabled = True
                    btn2.disabled = True
                    self.pairs_found += 1

                    if self.pairs_found == 12:
                        if self.inactivity_task:
                            self.inactivity_task.cancel()
                        if self.timer_task:
                            self.timer_task.cancel()
                        await self.end_game(interaction)
                        return
                else:
                    btn1.style = btn2.style = discord.ButtonStyle.danger
                    await interaction.message.edit(view=self)
                    await discord.utils.sleep_until(discord.utils.utcnow() +
                                                    timedelta(seconds=1))
                    btn1.emoji = btn2.emoji = "❓"
                    btn1.style = btn2.style = discord.ButtonStyle.secondary
                    btn1.revealed = btn2.revealed = False

                self.selected_buttons.clear()

                for child in self.children:
                    if isinstance(child,
                                  MemoryGameButton) and not child.revealed:
                        child.disabled = False

                await interaction.message.edit(content=self.get_game_status(),
                                               view=self)
            else:
                await interaction.response.edit_message(
                    content=self.get_game_status(), view=self)

    async def check_inactivity(self):
        while True:
            await asyncio.sleep(1)
            if (datetime.now() -
                    self.last_interaction_time).total_seconds() > 20:
                await self.end_game_inactivity()
                break

    async def update_timer(self):
        while True:
            await asyncio.sleep(1)
            if self.game_started:
                elapsed_time = (datetime.now() -
                                self.start_time).total_seconds()
                if elapsed_time >= self.time_limit:
                    await self.end_game_timeout()
                    break
                await self.message.edit(content=self.get_game_status())

    async def end_game_inactivity(self):
        if self.timer_task:
            self.timer_task.cancel()
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="Game ended due to inactivity.",
                                view=None)
        self.game_started = False
        self.cog.end_game(self.ctx.author.id)

    async def end_game_timeout(self):
        if self.inactivity_task:
            self.inactivity_task.cancel()
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="Time's up! Game over.", view=None)
        self.game_started = False
        self.cog.end_game(self.ctx.author.id)

    async def end_game(self, interaction: discord.Interaction):
        if self.inactivity_task:
            self.inactivity_task.cancel()
        if self.timer_task:
            self.timer_task.cancel()
        end_time = datetime.now()
        time_taken = end_time - self.start_time
        minutes, seconds = divmod(time_taken.seconds, 60)

        embed = discord.Embed(title="🎉 Memory Game Completed! 🎉",
                              color=0x00ff00)
        embed.add_field(name="🕒 Time Taken",
                        value=f"{minutes} minutes and {seconds} seconds",
                        inline=False)
        embed.add_field(name="🔢 Total Moves",
                        value=str(self.moves),
                        inline=False)
        embed.add_field(name="💡 Hints Used",
                        value=f"{self.hints_used}/2",
                        inline=False)
        embed.set_footer(text="Thanks for playing!")

        rematch_view = RematchView(self.ctx, self.message, self.cog)
        await interaction.message.edit(content=None,
                                       embed=embed,
                                       view=rematch_view)
        self.game_started = False
        self.cog.end_game(self.ctx.author.id)

    async def show_hint(self):
        if self.hints_remaining > 0:
            unrevealed_buttons = [
                btn for btn in self.board
                if not btn.revealed and not btn.disabled
            ]
            if unrevealed_buttons:
                hint_button = random.choice(unrevealed_buttons)
                hint_button.emoji = hint_button.hidden_emoji
                hint_button.style = discord.ButtonStyle.primary
                self.hints_remaining -= 1
                self.hints_used += 1
                await self.message.edit(content=self.get_game_status(),
                                        view=self)
                await asyncio.sleep(2)
                if not hint_button.revealed:
                    hint_button.emoji = "❓"
                    hint_button.style = discord.ButtonStyle.secondary
                    await self.message.edit(view=self)


class RematchView(discord.ui.View):

    def __init__(self, ctx: commands.Context, message: discord.Message, cog):
        super().__init__(timeout=15.0)
        self.ctx = ctx
        self.message = message
        self.cog = cog

    @discord.ui.button(label="Rematch", style=discord.ButtonStyle.primary)
    async def rematch(self, interaction: discord.Interaction,
                      button: ui.Button):
        if interaction.user == self.ctx.author:
            await interaction.response.defer()
            new_game = MemoryGameView(
                self.ctx, 5, self.cog)  # Default to 5 minutes for rematch
            self.cog.start_game(self.ctx.author.id, new_game)
            await new_game.start_game(self.message)
        else:
            await interaction.response.send_message(
                "Only the original player can start a rematch.",
                ephemeral=True)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


class MemoryGame(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ongoing_games = {}
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    def start_game(self, user_id: int, game: MemoryGameView):
        self.ongoing_games[user_id] = game

    def end_game(self, user_id: int):
        if user_id in self.ongoing_games:
            del self.ongoing_games[user_id]

    @commands.command(name="memorygame")
    async def memorygame(self, ctx: commands.Context, time_limit: int = 5):
        """Starts a 5x5 memory game with custom server emojis. Optionally set a time limit (1-6 minutes)."""
        if ctx.author.id in self.ongoing_games:
            await ctx.send(
                "You already have an ongoing game. Please finish it before starting a new one."
            )
            return

        if time_limit < 1 or time_limit > 6:
            await ctx.send("Time limit must be between 1 and 6 minutes.")
            return

        try:
            game = MemoryGameView(ctx, time_limit, self)
            self.start_game(ctx.author.id, game)
            await game.start_game()
        except ValueError as e:
            await ctx.send(str(e))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if reaction.emoji == "💡":
            game = self.ongoing_games.get(user.id)
            if game and game.hints_remaining > 0:
                await reaction.remove(user)
                await game.show_hint()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MemoryGame(bot))
