import discord
import asyncio
import config
import json
import aiohttp

from datetime import datetime as dt
from itertools import islice
from discord.ext import commands

UTOPIA_URL = "http://utopia-game.com/wol/game/kingdoms_dump/?key=l1FdkNfdklAs"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

class Dragon:
    def __init__(self, bot):
        self.bot = bot
        self.saved_data = None
            
        
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
        
    # let's kick off this dragon calc
    @commands.group(invoke_without_command=True, pass_context = True, case_insensitive=True)
    async def dragoncost(self, ctx, target_kd, color):
        # start with populating the cost multiplier for the dragon types
        with open ("/home/pi/cretobot/dragonScript.json", "r") as f:
            d = json.load(f)
            our_kd = d["our_KD"]
           
        fresh_data = await self.get_data()
        print(fresh_data)
        # The json file has timestamps at the first and last index, we don't care about these
        for e in fresh_data[1:-1]:
            if e.get("loc") == our_kd:
                our_nw = e.get("nw")
            if e.get("loc") == target_kd:
                target_nw = e.get("nw")
        
        if color.lower() == "emerald":
            cost_metric = 3
        elif color.lower() == "ruby":
            cost_metric = 2.4
        elif color.lower() == "gold":
            cost_metric = 2
        elif color.lower() == "sapphire":
            cost_metric = 1
        else:
            await ctx.send("Invalid color option, please use: emerald, ruby, gold, or sapphire.")
        
        # apply the formula from the utopia wiki    
        dragon_cost = int(target_nw * 0.656 * cost_metric)
        await ctx.send("Total cost for a {} dragon will be {:,}gc.".format(color, dragon_cost))
        
        # if person calling command is a KD leader, give option to set the target KD, dragon cost,
        # and per province dragonshare and store in the json file
        ok_roles = ['leaders', 'admin']
        roles = {x for x in ctx.guild.roles if x.name in ok_roles}
        if roles & set(ctx.author.roles):
            await ctx.send("Would you like to set this cost for dragonshare purposes? (respond with 'yes' if so)")
            def check(m):
                return m.content.lower()=='yes'
            await self.wait_for('message', timeout=20.0, check=check)

            # pull any existing data from json
            with open ("/home/pi/cretobot/dragonScript.json", "r+") as f:
                data = json.load(f)
                our_kd = data["our_KD"]

            # set cost and target info in prep for writing to json    
            data["dragon_cost"] = dragon_cost
            data["target_KD"] = target_kd

            # populate province list with province name and respective dragonshare
            province_share = {}
            fresh_data = await self.get_data()
                # The json file has timestamps at the first and last index, we don't care about these
            for d in fresh_data[1:-1]:
                if d.get("loc") == our_kd:                  
                    province_share = [{"name": x["name"], "nw": x["nw"], "share": x["nw"]/d["nw"]*dragon_cost*1.1} for x in d.get("provinces")]

            data["provinces"] = province_share
            # update dragonScript json with target kd and province share info
            with open ("/home/pi/cretobot/dragonScript.json", "w+") as f:
                json.dump(data, f, indent = 2)
                
            return await ctx.send('Dragon target successfully set to ({}) for a {} dragon with total cost of {:,}gc.\n'
                                  'To see the list of dragonshares by province, use `!dragoncost list`.'.format(
                                  target_kd, color, dragon_cost))
        
    @dragoncost.command(pass_context=True)
    async def list(self, ctx):
        with open ("/home/pi/cretobot/dragonScript.json", "r") as f:
            data = json.load(f)
            
        await ctx.send('\n'.join(("{} | {:,.0f}gc".format(x["name"], x["share"])) for x in data["provinces"]))


def setup(bot):
    bot.add_cog(Dragon(bot))