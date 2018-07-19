import discord
import asyncio
from utils import permissions, default

config = default.get("config.json")

client = discord.Client()

@client.event
async def on_ready():
    print ('Logged in as')
    print (client.user.name)
    print (client.user.id)
    print ('------')

client.run(config.token)
