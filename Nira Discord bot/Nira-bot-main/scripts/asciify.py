from discord.ext import commands
from discord import Member, File
from typing import Union
from PIL import Image
from io import BytesIO
import aiohttp


async def fetch_image(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch image: {response.status}")
            return await response.read()


def process_image(image_data: bytes, new_width: int) -> Image.Image:
    image = Image.open(BytesIO(image_data))
    width, height = image.size
    new_height = int(new_width * height / width)
    return image.resize((new_width, new_height)).convert('L')


def create_ascii_art(image: Image.Image) -> str:
    ascii_chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
    pixels = list(image.getdata())

    if not all(isinstance(pixel, int) for pixel in pixels):
        raise ValueError("Image data contains non-integer pixel values")

    ascii_str = ''.join([ascii_chars[pixel // 25] for pixel in pixels])
    ascii_art = '\n'.join([
        ascii_str[i:i + image.width]
        for i in range(0, len(ascii_str), image.width)
    ])
    return ascii_art


async def asciify(ctx: commands.Context,
                  link: Union[Member, str],
                  new_width: int = 100) -> None:
    if isinstance(link, Member):
        url = link.display_avatar.url
    else:
        url = link

    try:
        image_data = await fetch_image(url)
        image = process_image(image_data, new_width)
        ascii_art = create_ascii_art(image)

        with BytesIO() as buffer:
            buffer.write(ascii_art.encode('utf-8'))
            buffer.seek(0)
            file = File(buffer, filename="ascii_art.txt")
            await ctx.send(file=file)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
