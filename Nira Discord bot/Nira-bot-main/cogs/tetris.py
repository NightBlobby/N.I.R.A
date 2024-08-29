import discord
from discord.ext import commands
import asyncio
import random
import aiohttp


class TetrisPiece:
    SHAPES = [[[1, 1, 1, 1]], [[1, 1], [1, 1]], [[1, 1, 1], [0, 1, 0]],
              [[1, 1, 1], [1, 0, 0]], [[1, 1, 1], [0, 0, 1]],
              [[1, 1, 0], [0, 1, 1]], [[0, 1, 1], [1, 1, 0]]]

    def __init__(self):
        self.shape = random.choice(self.SHAPES)
        self.color = random.randint(1, 7)

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))


class TetrisGame:
    WIDTH = 10
    HEIGHT = 20
    BASE_FALL_SPEED = 1.0
    MIN_FALL_SPEED = 0.15

    def __init__(self):
        self.board = [[0 for _ in range(self.WIDTH)]
                      for _ in range(self.HEIGHT)]
        self.current_piece = None
        self.next_piece = TetrisPiece()
        self.piece_x = 0
        self.piece_y = 0
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.started = False

    def new_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = TetrisPiece()
        self.piece_x = self.WIDTH // 2 - len(self.current_piece.shape[0]) // 2
        self.piece_y = 0
        if not self.is_valid_move(self.piece_x, self.piece_y,
                                  self.current_piece.shape):
            self.game_over = True

    def move(self, dx, dy):
        if self.current_piece and self.is_valid_move(self.piece_x + dx,
                                                     self.piece_y + dy,
                                                     self.current_piece.shape):
            self.piece_x += dx
            self.piece_y += dy
            return True
        return False

    def rotate(self):
        if not self.current_piece:
            return False
        rotated_shape = list(zip(*self.current_piece.shape[::-1]))
        if self.is_valid_move(self.piece_x, self.piece_y, rotated_shape):
            self.current_piece.shape = rotated_shape
            return True
        return False

    def hard_drop(self):
        if not self.current_piece:
            return 0
        drop_distance = 0
        while self.move(0, 1):
            drop_distance += 1
        return drop_distance

    def is_valid_move(self, x, y, shape):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell and (y + i >= self.HEIGHT or x + j < 0
                             or x + j >= self.WIDTH or
                             (y + i >= 0 and self.board[y + i][x + j])):
                    return False
        return True

    def merge_piece(self):
        if not self.current_piece:
            return
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.board[self.piece_y + i][self.piece_x +
                                                 j] = self.current_piece.color

    def clear_lines(self):
        lines_cleared = 0
        for i in range(self.HEIGHT - 1, -1, -1):
            if all(self.board[i]):
                del self.board[i]
                self.board.insert(0, [0 for _ in range(self.WIDTH)])
                lines_cleared += 1

        if lines_cleared:
            self.lines_cleared += lines_cleared
            self.score += (lines_cleared**2) * 100 * self.level
            self.level = min(self.lines_cleared // 10 + 1, 15)

        return lines_cleared

    def render(self):
        board_copy = [row[:] for row in self.board]
        if self.current_piece:
            for i, row in enumerate(self.current_piece.shape):
                for j, cell in enumerate(row):
                    if cell and 0 <= self.piece_y + i < self.HEIGHT and 0 <= self.piece_x + j < self.WIDTH:
                        board_copy[self.piece_y +
                                   i][self.piece_x +
                                      j] = self.current_piece.color

        return "\n".join("".join(self.cell_to_emoji(cell) for cell in row)
                         for row in board_copy)

    @staticmethod
    def cell_to_emoji(cell):
        return ["⬛", "🟥", "🟦", "🟩", "🟨", "🟪", "🟧", "⬜", "⚪"][cell]

    def get_fall_speed(self):
        return max(self.BASE_FALL_SPEED - (self.level - 1) * 0.05,
                   self.MIN_FALL_SPEED)


class TetrisCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.games = {}
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    @commands.command(name="tetris")
    async def tetris(self, ctx):
        if ctx.author.id in self.games:
            await ctx.send(
                "You're already in a game! Use the 🛑 reaction to end it.")
            return

        game = TetrisGame()
        self.games[ctx.author.id] = game

        embed = discord.Embed(title="Tetris Game", color=0x00ff00)
        embed.add_field(name="\u200b",
                        value="Press ▶️ to start!",
                        inline=False)
        embed.add_field(name="Score", value="0", inline=True)
        embed.add_field(name="Level", value="1", inline=True)
        embed.add_field(name="Lines", value="0", inline=True)
        embed.add_field(name="Next Piece", value="?", inline=True)
        embed.set_footer(
            text=
            "▶️: Start | ⬅️: Left | ➡️: Right | 🔽: Soft Drop | ⏬: Hard Drop\n🔄: Rotate | ⏸️: Pause | 🛑: End | ❓: Help"
        )

        message = await ctx.send(embed=embed)
        await message.add_reaction("▶️")

        # First row of controls
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
        await message.add_reaction("🔽")
        await message.add_reaction("⏬")

        # Second row of controls
        await message.add_reaction("🔄")
        await message.add_reaction("⏸️")
        await message.add_reaction("🛑")
        await message.add_reaction("❓")

    async def game_loop(self, user_id, message):
        game = self.games[user_id]
        game.new_piece()
        await self.update_game(user_id, message)
        while not game.game_over and user_id in self.games:
            if not game.paused:
                await asyncio.sleep(game.get_fall_speed())
                if not game.move(0, 1):
                    game.merge_piece()
                    lines_cleared = game.clear_lines()
                    if game.game_over:
                        await self.end_game(user_id, message, "Game Over!")
                        return
                    game.new_piece()
                await self.update_game(user_id, message)
            else:
                await asyncio.sleep(0.1)

    async def update_game(self, user_id, message):
        if user_id not in self.games:
            return
        game = self.games[user_id]
        embed = message.embeds[0]
        embed.color = 0x0000ff if game.paused else 0x00ff00  # Blue when paused, green otherwise
        embed.set_field_at(0, name="\u200b", value=game.render(), inline=False)
        embed.set_field_at(1, name="Score", value=str(game.score), inline=True)
        embed.set_field_at(2, name="Level", value=str(game.level), inline=True)
        embed.set_field_at(3,
                           name="Lines",
                           value=str(game.lines_cleared),
                           inline=True)
        next_piece_preview = "\n".join("".join(
            game.cell_to_emoji(cell) for cell in row)
                                       for row in game.next_piece.shape)
        embed.set_field_at(4,
                           name="Next Piece",
                           value=next_piece_preview,
                           inline=True)
        await message.edit(embed=embed)

    async def end_game(self, user_id, message, end_message):
        if user_id not in self.games:
            return
        game = self.games[user_id]
        embed = message.embeds[0]
        embed.title = end_message
        embed.color = 0xff0000
        embed.set_field_at(0, name="\u200b", value=game.render(), inline=False)
        embed.set_field_at(1,
                           name="Final Score",
                           value=str(game.score),
                           inline=True)
        embed.set_field_at(2,
                           name="Level Reached",
                           value=str(game.level),
                           inline=True)
        embed.set_field_at(3,
                           name="Lines Cleared",
                           value=str(game.lines_cleared),
                           inline=True)
        await message.edit(embed=embed)
        del self.games[user_id]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot or user.id not in self.games:
            return

        game = self.games[user.id]
        moved = False

        if reaction.emoji == "▶️" and not game.started:
            game.started = True
            await self.game_loop(user.id, reaction.message)
            return
        elif not game.started:
            await reaction.remove(user)
            return
        elif reaction.emoji == "⬅️":
            moved = game.move(-1, 0)
        elif reaction.emoji == "➡️":
            moved = game.move(1, 0)
        elif reaction.emoji == "🔽":
            moved = game.move(0, 1)
        elif reaction.emoji == "⏬":
            drop_distance = game.hard_drop()
            game.score += drop_distance * 2  # Bonus points for hard drop
            game.merge_piece()
            lines_cleared = game.clear_lines()
            if game.game_over:
                await self.end_game(user.id, reaction.message, "Game Over!")
                return
            game.new_piece()
            moved = True
        elif reaction.emoji == "🔄":
            moved = game.rotate()
        elif reaction.emoji == "⏸️":
            game.paused = not game.paused
            moved = True  # Force update to change color
        elif reaction.emoji == "🛑":
            await self.end_game(user.id, reaction.message, "Game Ended")
            return
        elif reaction.emoji == "❓":
            await self.show_help(reaction.message.channel)
            return

        if moved:
            await self.update_game(user.id, reaction.message)

        await reaction.remove(user)

    async def show_help(self, channel):
        help_embed = discord.Embed(title="Tetris Help", color=0x0000ff)
        help_embed.add_field(
            name="How to Play",
            value=("• ▶️: Start the game\n"
                   "• ⬅️: Move left\n"
                   "• ➡️: Move right\n"
                   "• 🔽: Soft drop (move down faster)\n"
                   "• ⏬: Hard drop (instantly drop to bottom)\n"
                   "• 🔄: Rotate piece\n"
                   "• ⏸️: Pause/Resume game\n"
                   "• 🛑: End game\n"
                   "• Clear lines to score points and level up!\n"
                   "• Game speeds up as you level up.\n"
                   "• Game ends if pieces stack up to the top."),
            inline=False)
        await channel.send(embed=help_embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TetrisCog(bot))
