import os
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from datetime import datetime
import pytz
import pycountry


class Weather(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up resources when the cog is unloaded."""
        await self.session.close()

    @app_commands.command(
        name="weather", description="Get the weather for a specified location")
    async def weather(self, interaction: discord.Interaction, location: str):
        api_key = os.getenv(
            "WEATHER_API_KEY")  # Retrieve the API key from the environment
        if not api_key:
            await interaction.response.send_message("Error: API key not found."
                                                    )
            return

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": api_key, "units": "metric"}

        async with self.session.get(base_url, params=params) as response:
            data = await response.json()

        if data["cod"] != 200:
            await interaction.response.send_message(f"Error: {data['message']}"
                                                    )
            return

        # Extract data from API response
        weather_description = data["weather"][0]["description"].capitalize()
        icon = data["weather"][0]["icon"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        country_code = data["sys"]["country"]
        country_name = self.get_country_name(country_code)

        title = f"Weather in {location.capitalize()} - {country_name}"

        last_updated = datetime.utcfromtimestamp(data["dt"])
        local_tz = pytz.timezone('Asia/Kolkata')
        last_updated_local = last_updated.astimezone(local_tz)
        last_updated_time = last_updated_local.strftime('%I:%M %p')
        last_updated_date = last_updated_local.strftime('%Y-%m-%d')

        embed_color = self.get_embed_color(weather_description)

        embed = discord.Embed(title=title, color=embed_color)
        embed.set_thumbnail(
            url=f"http://openweathermap.org/img/wn/{icon}@2x.png")
        embed.add_field(name="Description",
                        value=weather_description,
                        inline=False)
        embed.add_field(name="Temperature", value=f"{temp}°C", inline=True)
        embed.add_field(name="Feels Like",
                        value=f"{feels_like}°C",
                        inline=True)
        embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
        embed.add_field(name="Wind Speed",
                        value=f"{wind_speed} m/s",
                        inline=True)
        embed.set_footer(
            text=
            f"Forecast by openweathermap.org | Last updated: {last_updated_date} {last_updated_time}"
        )

        await interaction.response.send_message(embed=embed)

    def get_country_name(self, country_code):
        try:
            country = pycountry.countries.get(alpha_2=country_code)
            return country.name if country else 'Unknown Country'
        except LookupError:
            return 'Unknown Country'

    def get_embed_color(self, weather_description):
        color_map = {
            'clear': '#00BFFF',
            'clouds': '#D3D3D3',
            'rain': '#1E90FF',
            'drizzle': '#1E90FF',
            'thunderstorm': '#8A2BE2',
            'snow': '#00CED1',
            'mist': '#B0E0E6',
            'fog': '#B0E0E6',
            'haze': '#F5F5DC',
            'sand': '#F4A460',
            'dust': '#D2B48C',
            'tornado': '#FF4500',
            'hurricane': '#FF6347'
        }
        for key, color in color_map.items():
            if key in weather_description.lower():
                return discord.Color(int(color[1:], 16))
        return discord.Color.default()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Weather(bot))
