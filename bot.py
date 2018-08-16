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
        super().__init__(command_prefix="!", description=description, case_insensitive=True)
        self.add_command(self.setkd)
        self.add_command(self.kd)
        self.add_command(self.list_provs)
        self.add_command(self.dragoncost)
        self.saved_data = None
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
    
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
    
    # let's kick off this dragon calc
    @commands.group(invoke_without_command=True, pass_context = True, case_insensitive=True)
    async def dragoncost(self, ctx, target_kd, color):
        # start with populating the cost multiplier for the dragon types
        with open ("dragonScript.json", "r") as f:
            d = json.load(f)
            our_kd = d["our_KD"]
            em = d["emerald"]
            ruby = d["ruby"]
            gold = d["gold"]
            saph = d["sapphire"]
 
        fresh_data = await self.get_data()
        # The json file has timestamps at the first and last index, we don't care about these
        for e in fresh_data[1:-1]:
            if e.get("loc") == our_kd:
                our_nw = e.get("nw")
            if e.get("loc") == target_kd:
                target_nw = e.get("nw")
        
        if color.lower() == "emerald":
            cost_metric = em
        elif color.lower() == "ruby":
            cost_metric = ruby
        elif color.lower() == "gold":
            cost_metric = gold
        elif color.lower() == "sapphire":
            cost_metric = saph
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
            with open ("dragonScript.json", "r+") as f:
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
                   # province_share = list(x["name"] for x in d.get("provinces"))
                   # print(*province_share)
                    province_share = [{"name": x["name"], "nw": x["nw"], "share": x["nw"]/d["nw"]*dragon_cost*1.1} for x in d.get("provinces")]

            data["provinces"] = province_share
            # update dragonScript json with target kd and province share info
            with open ("dragonScript.json", "w+") as f:
                json.dump(data, f, indent = 2)
                
            return await ctx.send('Dragon target successfully set to ({}) for a {} dragon with total cost of {:,}gc.\n'
                                  'To see the list of dragonshares by province, use `!dragoncost list`.'.format(
                                  target_kd, color, dragon_cost))


    @dragoncost.command(pass_context=True)
    async def list(ctx):
        with open ("dragonScript.json", "r") as f:
            data = json.load(f)
            
        await ctx.send('\n'.join(("{} | {:,.0f}gc".format(x["name"], x["share"])) for x in data["provinces"]))
        
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
                return await ctx.send("Our KD NW: {}".format(d.get("nw"))),
                await ctx.send('\n'.join((x["name"], str(int(y["nw"]))) for x, y in d.get("provinces")))

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
