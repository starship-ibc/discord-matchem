import os

import discord

from .game import Game

discord_key = os.environ.get("DISCORD_KEY")

game = Game(intents=discord.Intents.default())
game.run(discord_key)
