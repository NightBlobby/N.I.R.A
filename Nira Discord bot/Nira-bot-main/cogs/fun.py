import discord
from discord.ext import commands
import random
from discord import Member
from io import BytesIO
from PIL import Image
from typing import Union
from scripts.emojify import emojify_image
from jokeapi import Jokes
import aiohttp
import requests
from scripts.asciify import asciify
import os
from scripts.collatz import is_collatz_conjecture
import aiofiles


class Fun(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    class Fun(commands.Cog):

        def __init__(self, bot):
            self.bot = bot

    @commands.command()
    async def wanted(self,
                     ctx: commands.Context,
                     *,
                     member: discord.Member = None):
        await ctx.defer()

        # Define the paths for the images
        wanted_image_path = "images/wanted.jpg"
        profile_image_path = "images/profile.jpg"

        # If no member is mentioned, use the command issuer's profile picture
        if member is None:
            member = ctx.author

        # Check if the wanted image file exists
        if not os.path.exists(wanted_image_path):
            await ctx.send(
                f"File {wanted_image_path} not found. Please check the file path."
            )
            return

        try:
            # Open the wanted poster image asynchronously
            async with aiofiles.open(wanted_image_path, mode='rb') as f:
                wanted_bytes = await f.read()
                wanted = Image.open(BytesIO(wanted_bytes))
        except IOError:
            await ctx.send(
                f"Failed to open {wanted_image_path}. Please check the file.")
            return

        try:
            # Read the member's avatar
            avatar_bytes = BytesIO(await member.display_avatar.read())
            pfp = Image.open(avatar_bytes)
            pfp = pfp.resize((2691, 2510))
            wanted.paste(pfp, (750, 1867))
        except IOError:
            await ctx.send(
                "Failed to process the avatar image. Please try again.")
            return

        try:
            # Save the combined image asynchronously
            async with aiofiles.open(profile_image_path, mode='wb') as f:
                output_bytes = BytesIO()
                wanted.save(output_bytes, format='JPEG')
                await f.write(output_bytes.getvalue())
        except IOError:
            await ctx.send(
                f"Failed to save the profile image to {profile_image_path}.")
            return

        try:
            await ctx.send(file=discord.File(profile_image_path))
        except discord.DiscordException:
            await ctx.send("Failed to send the image. Please try again.")

    @commands.command()
    async def collatz(self, ctx, number: int):
        await ctx.defer()
        original_number = int(number)
        if is_collatz_conjecture(original_number):
            steps = []
            while original_number > 1:
                steps.append(original_number)
                if original_number % 2 == 0:
                    original_number //= 2
                else:
                    original_number = 3 * original_number + 1
            steps.append(1)

            steps_message = (
                f"The number {number} holds true for **Collatz conjecture**.\n"
                f"**Steps:**\n```py\n{steps}```\nReached 1 successfully!!")

            if len(steps_message) > 2000:
                with open("collatztxt.py", "w") as file:
                    file.write("steps = [\n")
                    for i in range(0, len(steps), 7):
                        file.write(", ".join(map(str, steps[i:i + 7])) + ",\n")
                    file.write("]\n")
                await ctx.send(
                    "The steps are too long to display here, so I've uploaded them as a file:",
                    file=discord.File("collatztxt.py"))
                os.remove("collatztxt.py")
            else:
                await ctx.send(steps_message)
        else:
            await ctx.send(f"The number {number} is not a Collatz conjecture.")

    @commands.command(aliases=['peepee', 'pipi', 'pepe'])
    async def pp(self, ctx):
        await ctx.defer()
        user = ctx.author.name
        footer_pfp = ctx.author.display_avatar
        pp_list = [
            '8>\nYou Have The Smallest PP In The World!🤣', '8=>', '8==>',
            '8===>', '8====>', '8=====>', '8======>', '8=======>',
            '8========>', '8==========>', '8===========>',
            '8============D\nYou Have The Largest PP In The World!🙀'
        ]
        embed = discord.Embed(title='PP Size Machine~', color=0x2f3135)
        embed.add_field(name='Your PP size is:',
                        value=f'```py\n{random.choice(pp_list)}```')
        embed.set_footer(text=f"Requested By: {user}", icon_url=footer_pfp)
        await ctx.send(embed=embed)

    @commands.command()
    async def emojify(self, ctx, url: Union[discord.Member, str], size: int):
        await ctx.defer()
        if isinstance(url, discord.Member):
            url = url.display_avatar.url

        def get_emojified_image():
            r = requests.get(url, stream=True)
            image = Image.open(r.raw).convert("RGB")
            res = emojify_image(image, size)
            if size > size:
                res = f"```{res}```"
            return res

        result = await self.bot.loop.run_in_executor(None, get_emojified_image)
        await ctx.send(f"```py\n{result}```")

    @commands.command()
    async def asciify(self,
                      ctx: commands.Context,
                      link: Union[Member, str],
                      new_width: int = 100):
        await ctx.defer()
        await asciify(ctx, link, new_width)

    @commands.command()
    async def rng(self, ctx):
        await ctx.defer()
        rand_int = random.randint(0, 1000)
        embed = discord.Embed(
            title="RNG Machine~",
            description="Generates A Random Number Between 1 And 1000",
            color=0x2f3131)
        embed.add_field(name="Number:", value=f"```py\n{rand_int}```")
        await ctx.send(embed=embed)

    @commands.command()
    async def joke(self, ctx: commands.Context):
        await ctx.defer()
        try:
            j = await Jokes()
            joke = await j.get_joke()

            # Ensure joke is treated as a dictionary
            joke = dict(joke)

            if joke["type"] == "single":
                msg = joke["joke"]
            else:
                msg = joke["setup"]
                if 'delivery' in joke:
                    msg += f"||{joke['delivery']}||"

            await ctx.send(msg)
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

    @commands.command()
    async def slap(self, ctx, who: discord.Member, *reason):
        li = [
            'https://media.tenor.com/aCZMe2OKWX0AAAAC/fail-water.gif',
            'https://media.tenor.com/pUatwfgNCZUAAAAd/fish-slap-w2s.gif',
            'https://media.tenor.com/pmCZDX1MB1gAAAAC/johnny-knoxville-slap.gif',
            'https://media.tenor.com/83tH-nXQeAMAAAAC/fish-slap.gif',
            'https://media.tenor.com/-RSry4HDatUAAAAC/slap-out-kast.gif',
            'https://media.tenor.com/__oycZBexeAAAAAC/slap.gif',
            'https://media.tenor.com/WsKM5ZDigvgAAAAC/penguin-penguins.gif',
            'https://media.tenor.com/tKF3HiguDmEAAAAC/wrrruutchxxxxiii-slapt.gif',
            'https://media.tenor.com/2L_eT6hPUhcAAAAC/spongebob-squarepants-patrick-star.gif',
            'https://media.tenor.com/fw6gs_ia_UIAAAAd/slap-slapping.gif',
            'https://media.tenor.com/OXFdOzVbsW0AAAAC/smack-you.gif',
            'https://media.tenor.com/R6LaPVpPwfcAAAAd/slap-slapping.gif',
            'https://media.tenor.com/zdNVA6sB53AAAAAC/molorant-ckaz.gif',
            'https://media.tenor.com/E3OW-MYYum0AAAAC/no-angry.gif',
            'https://media.tenor.com/2-r7BEc-cb8AAAAC/slap-smack.gif',
            'https://media.tenor.com/rVXByOZKidMAAAAd/anime-slap.gif',
            'https://media.tenor.com/Ws6Dm1ZW_vMAAAAC/girl-slap.gif',
            'https://media.tenor.com/5jBuDXkDsjYAAAAC/slap.gif',
            'https://media.tenor.com/eU5H6GbVjrcAAAAC/slap-jjk.gif',
            'https://media.tenor.com/0yMtzZ0GUGsAAAAC/hyouka-good.gif'
        ]

        reason_li = [
            "an eyesore", "a fool", "stupid", "a dumbass", "a moron",
            "a loser", "a noob", "a bot", "a fool"
        ]

        if not reason:
            reason = random.choice(reason_li)

        embed = discord.Embed(
            colour=discord.Color.random(),
            description=
            f"# {ctx.author.mention} slaps {who.mention} for being  {' '.join(reason)}"
        )
        embed.set_author(name=ctx.author.display_name,
                         icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=random.choice(li))
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
