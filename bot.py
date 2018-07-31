import discord
import asyncio
import config
import json
import aiohttp

from datetime import datetime as dt
from itertools import islice
from discord.ext import commands
 
description = 'This is my bot. I like it -- when it works...'
# bot = commands.Bot(command_prefix='!', description=description)
owner = [404071518159634452]

UTOPIA_URL = "http://utopia-game.com/wol/game/kingdoms_dump/?key=l1FdkNfdklAs"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"



class CretoriaBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", description=description)
        self.add_command(self.setkd)
        self.add_command(self.kd)
        self.add_command(self.list_provs)
        self.saved_data = None
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def get_data(self):
        # If saved data is None we haven't fetched anything, thanks to short-circuiting we can check the index in the or clause safely
        # If 15 minutes has passed since the last data fetched, we need to update to make sure it's fresh
        if self.saved_data is None or (dt.utcnow() - dt.strptime(self.saved_data[0], DATETIME_FORMAT)).total_seconds() // 60 > 15:
            await self.download_data()
        return self.saved_data

    async def download_data(self):
        async with self.session.get(UTOPIA_URL) as r:
            data = await r.json()
        self.saved_data = data

    # Command to set our current KD
    @commands.command()
    @commands.has_any_role('leaders', 'admin')
    async def setkd(self, ctx, our_kd):
        with open ("dragonScript.json", "r+") as f:
            data = json.load(f)
        
        data["our_KD"] = our_kd
    
        with open ("dragonScript.json", "w+") as f:
            json.dump(data, f)
    
        await ctx.send('Our KD set to ({}).'.format(our_kd))
    
    # Notify if person doens't have necessary role
    @setkd.error
    async def setkd_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have the necessary permissions for this command.')
    
    # Retrieves our KD location from json
    @commands.command()
    async def kd(self, ctx):
        with open ("dragonScript.json", "r+") as jsonFile:
            data = json.load(jsonFile)
            our_kd = data["our_KD"]
        await ctx.send('Our KD is ({}).'.format(our_kd))
    
    # List current KD provinces
    
    
    @commands.command()
    async def list_provs(self, ctx):
        with open ("dragonScript.json", "r") as f:
            data = json.load(f)
            our_kd = data["our_KD"]
            print(our_kd)

        fresh_data = await self.get_data()
        # The json file has timestamps at the first and last index, we don't care about these
        for d in fresh_data[1:-1]:
            if d.get("loc") == our_kd:
                return await ctx.send('\n'.join(x["name"] for x in d.get("provinces")))

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        print(discord.__version__)

    def run(self):
        super().run(config.token, reconnect=True)
    
if __name__ == '__main__':
    bot = CretoriaBot()
    bot.run()
