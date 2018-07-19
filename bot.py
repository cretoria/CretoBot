import discord
import asyncio
import sys
import json
import aiohttp
import time



from discord.ext import commands

def load_credentials():
    """
    Retrieves token
    """
    with open('config.json') as f:
        return json.load(f)
    
credentials = load_credentials()

client = discord.Client()

@client.event
async def on_ready():
    print ('Logged in as')
    print (client.user.name)
    print (client.user.id)
    print ('------')

client.run(credentials)
