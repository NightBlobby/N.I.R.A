import discord
from discord import app_commands
from discord.ui import View, Button
from discord.ext import commands
import asyncio
import random
import time
import aiohttp

DEFAULT_PLAYER_X = "❌"
DEFAULT_PLAYER_O = "⭕"
EMPTY = "‎‎‎‎‎‎‎‎‎‎‎‎‎‎‎‎‎‎"  # A zero-width space to make buttons appear empty
COOLDOWN_TIME = 1.0  # Cooldown time in seconds


class TicTacToeButton(discord.ui.Button):

    def __init__(self, x: int, y: int, game):
        super().__init__(style=discord.ButtonStyle.secondary,
                         label=EMPTY,
                         row=y)
        self.x = x
        self.y = y
        self.game = game
        self.emoji = None

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in [self.game.player1, self.game.player2]:
            await interaction.response.send_message(
                "You are not part of this game!", ephemeral=True)
            return

        if interaction.user != self.game.current_player:
            await interaction.response.send_message("It's not your turn!",
                                                    ephemeral=True)
            return

        if self.emoji is not None or self.label != EMPTY:
            await interaction.response.send_message(
                "This spot is already taken!", ephemeral=True)
            return

        # Check if the cooldown has passed
        current_time = time.time()
        if current_time - self.game.last_move_time < COOLDOWN_TIME:
            await interaction.response.send_message(
                f"Please wait {COOLDOWN_TIME} seconds between moves.",
                ephemeral=True)
            return

        self.game.last_move_time = current_time

        self.emoji = self.game.current_symbol
        self.label = None
        self.style = discord.ButtonStyle.success if self.game.current_player == self.game.player1 else discord.ButtonStyle.danger
        self.disabled = True
        await interaction.response.edit_message(view=self.game.board_view)

        self.game.reset_timeout_task(
        )  # Reset the inactivity timer after every move

        if self.game.check_winner():
            await self.game.show_winner(interaction)
        elif self.game.check_draw():
            await self.game.show_draw(interaction)
        else:
            self.game.switch_turn()
            if self.game.current_player.bot:
                await self.game.bot_move(interaction)
            else:
                await interaction.edit_original_response(
                    content=f"It's {self.game.current_player.mention}'s turn"
                    if not self.game.vs_bot else None,
                    view=self.game.board_view,
                )


class RematchButton(discord.ui.Button):

    def __init__(self, game):
        super().__init__(style=discord.ButtonStyle.primary,
                         label="Rematch",
                         row=3)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in [self.game.player1, self.game.player2]:
            await interaction.response.send_message(
                "You are not part of this game!", ephemeral=True)
            return

        # Create a new game with the same players
        new_game = TicTacToeGame(self.game.player1, self.game.player2,
                                 self.game.ctx, self.game.player_x.name,
                                 self.game.player_o.name)
        new_game.message = self.game.message

        # Update the message with the new game board
        await interaction.response.edit_message(
            content=f"It's {new_game.current_player.mention}'s turn"
            if not new_game.vs_bot else None,
            view=new_game.board_view)
        new_game.reset_timeout_task()


class TicTacToeGame:

    def __init__(self, player1: discord.Member, player2: discord.Member,
                 ctx: discord.Interaction, player_x: str, player_o: str):
        self.player1 = player1
        self.player2 = player2
        self.vs_bot = player2.bot
        self.current_player = player1 if self.vs_bot else random.choice(
            [player1, player2])
        self.current_symbol = self._format_emoji(player_x or DEFAULT_PLAYER_X)
        self.player_x = self._format_emoji(player_x or DEFAULT_PLAYER_X)
        self.player_o = self._format_emoji(player_o or DEFAULT_PLAYER_O)
        self.board_view = self.create_board_view()
        self.ctx = ctx
        self.timeout_task = None
        self.message = None
        self.last_move_time = 0  # Initialize last move time

    def _format_emoji(self, emoji: str) -> discord.PartialEmoji:
        if emoji.startswith("<") and emoji.endswith(">"):
            emoji_id = int(emoji.split(":")[-1][:-1])
            emoji_name = emoji.split(":")[1]
            return discord.PartialEmoji(name=emoji_name, id=emoji_id)
        else:
            return discord.PartialEmoji(name=emoji)

    def reset_timeout_task(self):
        if self.timeout_task:
            self.timeout_task.cancel()
        self.timeout_task = asyncio.create_task(self.handle_timeout())

    async def handle_timeout(self):
        await asyncio.sleep(20)
        if self.message:
            await self.clear_board("Game ended due to inactivity.")

    def create_board_view(self) -> View:
        view = View(timeout=None)
        for y in range(3):  # Fixed 3x3 board
            for x in range(3):
                view.add_item(TicTacToeButton(x, y, self))
        return view

    def switch_turn(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1
        self.current_symbol = self.player_o if self.current_symbol == self.player_x else self.player_x

    def check_winner(self) -> bool:
        board = [[self.get_button(x, y).emoji for x in range(3)]
                 for y in range(3)]

        # Check rows and columns
        for i in range(3):
            if all(board[i][j] == board[i][0] is not None for j in range(3)):
                return True
            if all(board[j][i] == board[0][i] is not None for j in range(3)):
                return True

        # Check diagonals
        if all(board[i][i] == board[0][0] is not None for i in range(3)):
            return True
        if all(board[i][2 - i] == board[0][2] is not None for i in range(3)):
            return True

        return False

    def get_button(self, x: int, y: int) -> TicTacToeButton:
        for button in self.board_view.children:
            if isinstance(button,
                          TicTacToeButton) and button.x == x and button.y == y:
                return button

    def check_draw(self) -> bool:
        return all(button.emoji is not None
                   for button in self.board_view.children
                   if isinstance(button, TicTacToeButton))

    async def show_winner(self, interaction: discord.Interaction):
        winner = self.current_player
        loser = self.player2 if winner == self.player1 else self.player1
        await self.end_game("win", winner=winner, loser=loser)
        await interaction.edit_original_response(content="",
                                                 view=self.board_view)

    async def show_draw(self, interaction: discord.Interaction):
        await self.end_game("draw")
        await interaction.edit_original_response(content="",
                                                 view=self.board_view)

    async def end_game(self,
                       result: str,
                       winner: discord.Member = None,
                       loser: discord.Member = None):
        if self.timeout_task:
            self.timeout_task.cancel()

        # Make all TicTacToeButtons grey and disabled
        for button in self.board_view.children:
            if isinstance(button, TicTacToeButton):
                button.style = discord.ButtonStyle.secondary
                button.disabled = True

        # Remove any existing result buttons
        self.board_view.remove_item(self.board_view.children[-1] if len(
            self.board_view.children) > 9 else None)
        self.board_view.remove_item(self.board_view.children[-1] if len(
            self.board_view.children) > 9 else None)

        if result == "draw":
            result_button = Button(style=discord.ButtonStyle.blurple,
                                   label="It's a draw!",
                                   disabled=True,
                                   row=3)
            self.board_view.add_item(result_button)
        else:
            win_button = Button(style=discord.ButtonStyle.green,
                                label=f"{winner.name} won!",
                                disabled=True,
                                row=3)
            lose_button = Button(style=discord.ButtonStyle.red,
                                 label=f"{loser.name} lost!",
                                 disabled=True,
                                 row=3)
            self.board_view.add_item(win_button)
            self.board_view.add_item(lose_button)

        # Add the rematch button
        self.board_view.add_item(RematchButton(self))

    async def bot_move(self, interaction: discord.Interaction):
        best_score = -float('inf')
        best_move = None

        for button in self.board_view.children:
            if isinstance(button, TicTacToeButton) and button.emoji is None:
                button.emoji = self.current_symbol
                score = self.minimax(0, False)
                button.emoji = None
                if score > best_score:
                    best_score = score
                    best_move = button

        if best_move:
            best_move.emoji = self.current_symbol
            best_move.label = None
            best_move.style = discord.ButtonStyle.danger
            best_move.disabled = True

            self.reset_timeout_task(
            )  # Reset the inactivity timer after bot's move

            if self.check_winner():
                await self.show_winner(interaction)
            elif self.check_draw():
                await self.show_draw(interaction)
            else:
                self.switch_turn()
                await interaction.edit_original_response(
                    content=f"It's {self.current_player.mention}'s turn",
                    view=self.board_view)

    def minimax(self, depth: int, is_maximizing: bool) -> int:
        if self.check_winner():
            return 1 if not is_maximizing else -1
        elif self.check_draw():
            return 0

        if is_maximizing:
            best_score = -float('inf')
            for button in self.board_view.children:
                if isinstance(button,
                              TicTacToeButton) and button.emoji is None:
                    button.emoji = self.current_symbol
                    score = self.minimax(depth + 1, False)
                    button.emoji = None
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for button in self.board_view.children:
                if isinstance(button,
                              TicTacToeButton) and button.emoji is None:
                    button.emoji = self.player_x if self.current_symbol == self.player_o else self.player_o
                    score = self.minimax(depth + 1, True)
                    button.emoji = None
                    best_score = min(score, best_score)
            return best_score

    async def clear_board(self, content: str):
        for button in self.board_view.children:
            if isinstance(button, TicTacToeButton):
                self.board_view.remove_item(button)

        if self.message:
            try:
                await self.message.edit(content=content, view=self.board_view)
            except discord.errors.NotFound:
                print("Failed to clear the board: Message not found.")


class AcceptDeclineButtons(View):

    def __init__(self, game, author, opponent):
        super().__init__(timeout=15)  # Set the timeout to 15 seconds
        self.game = game
        self.author = author
        self.opponent = opponent

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
        if interaction.user != self.opponent:
            await interaction.response.send_message("This isn't for you!",
                                                    ephemeral=True)
            return

        self.stop(
        )  # Stop the view when the game starts to prevent timeout handling
        await interaction.message.delete()
        initial_message = f"It's {self.game.current_player.mention}'s turn"
        message = await interaction.channel.send(initial_message,
                                                 view=self.game.board_view)
        self.game.message = message
        self.game.reset_timeout_task(
        )  # Start the timeout task when the game starts
        self.game.last_move_time = time.time()  # Set initial move time

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
        if interaction.user != self.opponent:
            await interaction.response.send_message("This isn't for you!",
                                                    ephemeral=True)
            return

        self.stop()  # Stop the view after a decision has been made
        await interaction.message.edit(
            content=
            f"{self.opponent.mention} declined the invitation to play Tic Tac Toe.",
            view=None)

    async def on_timeout(self):
        # Handle the scenario where the opponent doesn't respond in time
        await self.game.ctx.edit_original_response(
            content=
            f"{self.opponent.mention} did not respond to the game invitation in time.",
            view=None)
        self.stop()


class TicTacToe(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    @app_commands.command(name="ttt",
                          description="Start a new Tic Tac Toe game")
    @app_commands.describe(
        opponent=
        "The user you want to play against (leave empty to play against the bot)",
        player_x="Custom emoji for player X (optional)",
        player_o="Custom emoji for player O (optional)")
    async def tic_tac_toe(self,
                          interaction: discord.Interaction,
                          opponent: discord.Member = None,
                          player_x: str = None,
                          player_o: str = None):
        if opponent is None:
            opponent = interaction.guild.me

        # Check for invalid emojis
        if player_x and not self.is_valid_emoji(player_x):
            await interaction.response.send_message(
                "Invalid emoji for player X. Please use a valid emoji.",
                ephemeral=True)
            return

        if player_o and not self.is_valid_emoji(player_o):
            await interaction.response.send_message(
                "Invalid emoji for player O. Please use a valid emoji.",
                ephemeral=True)
            return

        game = TicTacToeGame(interaction.user, opponent, interaction, player_x,
                             player_o)

        if opponent == interaction.guild.me:
            await interaction.response.send_message(
                f"**{interaction.user.mention}** vs {opponent.mention} - Let's play Tic Tac Toe!",
                view=game.board_view)
            game.message = await interaction.original_response()
            game.reset_timeout_task(
            )  # Start the timeout task when the game starts
            game.last_move_time = time.time()  # Set initial move time
        elif opponent == interaction.user:
            await interaction.response.send_message(
                "You cannot play against yourself!", ephemeral=True)
            return
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} has invited {opponent.mention} to play Tic Tac Toe. Would you like to accept?",
                view=AcceptDeclineButtons(game, interaction.user, opponent))

    def is_valid_emoji(self, emoji: str) -> bool:
        """Check if the provided string is a valid emoji."""
        try:
            # Try to create a PartialEmoji object
            discord.PartialEmoji.from_str(emoji)
            return True
        except:
            return False


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TicTacToe(bot))
