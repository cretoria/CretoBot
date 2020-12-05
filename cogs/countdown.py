###setup command, which will take several args:
### time to countdown (day/hours/minutes)
### who to mention, if any
### message for countdown
###   potentially have format for countdown inline

import discord
import asyncio
import json
import urllib
import aiohttp
import random
import collections
import re

from datetime import datetime as dt
from itertools import islice
from discord.ext import commands

class Countdown(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rockcount(self, ctx, *, msg:str):
        msg_to_edit = await ctx.message.channel.send(msg)
        
        await asyncio.sleep(3)
        await msg_to_edit.edit(content='this is a new message')
        
def setup(bot):
    bot.add_cog(Countdown(bot))
