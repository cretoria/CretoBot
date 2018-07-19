import discord
import asyncio
import sys
import json
import aiohttp
import time

with open('config.json', 'r') as f:
    config = json.load(f)

from discord.ext import commands

client = discord.Client()

@client.event
async def on_ready():
    print ('Logged in as')
    print (client.user.name)
    print (client.user.id)
    print ('------')

client.run(config.token)
