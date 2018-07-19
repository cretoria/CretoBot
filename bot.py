import discord
import asyncio
import sys
import json
import aiohttp
import time
import config
from discord.ext import commands

bot = discord.Client()
bot = commands.Bot(command_prefix='+', description='A bot that greets the user back.')

@bot.event
async def on_ready():
    print ('Logged in as')
    print (bot.user.name)
    print (bot.user.id)
    print ('------')

@bot.command()
async def hello(ctx):
    await ctx.send("Hello there! :wave:")
    


client.run(config.token)
