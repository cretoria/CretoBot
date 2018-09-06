import discord
import asyncio
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
        self.bot.session = aiohttp.ClientSession(loop=self.bot.loop)
        
    async def get_data(self):
        # If saved data is None we haven't fetched anything, thanks to short-circuiting we can check the index in the or clause safely
        # If 15 minutes has passed since the last data fetched, we need to update to make sure it's fresh
        if self.saved_data is None or (dt.utcnow() - dt.strptime(self.saved_data[0], DATETIME_FORMAT)).total_seconds() // 60 > 15:
            await self.download_data()
        return self.saved_data

    async def download_data(self):
        async with self.bot.session.get(UTOPIA_URL) as r:
            data = await r.json()
        self.saved_data = data
    
    ### Listen in #dragon channel for funding posts, and log in tracking json
    async def on_message(self, message):
        if message.channel.name == 'dragon' and message.author.name == 'munkbot':
            with open('/home/pi/cretobot/dragonFund.json', 'r') as f:
                fund = json.load(f)
            fundpost = message.content
            fund_amt = int(''.join(filter(str.isdigit, fundpost)))
            entry = {'Province': fundpost[25:fundpost.find(' [')], 'Amount': fund_amt}
            fund.append(entry)
            with open('/home/pi/cretobot/dragonFund.json','w') as f:
                json.dump(fund, f, indent = 2)
                
                    
    # Group of commands to assist with dragon cost, funding, and slaying
    @commands.group(invoke_without_command=False, aliases=["dragoncost"], case_insensitive=True, no_pm=True)
    async def fluffy(self, ctx):
        pass
    
    @fluffy.command(name="cost", no_pm=True)
    async def fluffy_cost(self, ctx, target_kd, color):
        # start with populating the cost multiplier for the dragon types
        with open ("/home/pi/cretobot/dragonScript.json", "r") as f:
            d = json.load(f)
            our_kd = d["our_KD"]
           
        fresh_data = await self.get_data()

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
            await self.bot.wait_for('message', timeout=20.0, check=check)

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

            data["provinces"] = sorted(province_share, key=lambda k:k["name"])
            # update dragonScript json with target kd and province share info
            with open ("/home/pi/cretobot/dragonScript.json", "w+") as f:
                json.dump(data, f, indent = 4)
                
            return await ctx.send('Dragon target successfully set to ({}) for a {} dragon with total cost of {:,}gc.\n'
                                  'To see the list of dragonshares by province, use `!fluffy list`.'.format(
                                  target_kd, color, dragon_cost))
        
    @fluffy.command(name="fund", pass_context=True)
    async def fluffy_fund(self, ctx):
        with open ("/home/pi/cretobot/dragonScript.json", "r") as f:
            data = json.load(f)
            
        await ctx.send('\n'.join(("{} | {:,.0f}gc".format(x["name"], x["share"])) for x in data["provinces"]))

    ### Listen in #internal channel for dragon-arrived post, then calc HP and prov shares
    async def on_message(self, message):
        dragon_here = 'has begun ravaging our lands'
        if message.channel.id == 404868940683149332 and dragon_here in message.content:
            ### Get the dragon color
            words = message.content.split()
            dragon_color = words[words.index('Dragon,')-1].lower()
            
            with open("/home/pi/cretobot/dragonScript.json", "r") as f:
                data = json.load(f)
                our_kd = data["our_KD"]
                
            fresh_data = await self.get_data()
            
            for e in fresh_data[1:-1]:
                if e.get("loc") == our_kd:
                    our_nw = e.get("nw")
                    
            if dragon_color == 'sapphire':
                hp_mod = 1
            elif dragon_color == 'gold':
                hp_mod = 2.625
            elif dragon_color == 'ruby':
                hp_mod = 4.5
            elif dragon_color == 'emerald':
                hp_mod = 5.25
            else:
                return
            
            dragon_hp = int(hp_mod * our_nw / 132)
            province_slay = {}
           
            for d in fresh_data[1:-1]:
                if d.get("loc") == our_kd:                  
                    province_slay = [{"name": x["name"], "nw": x["nw"], "slay": x["nw"]/d["nw"]*dragon_hp*1.1} for x in d.get("provinces")]
            
            data["slay_list"] = sorted(province_slay, key=lambda k:k["name"])
            # update dragonScript json with target kd and province slay info
            with open ("/home/pi/cretobot/dragonScript.json", "w+") as f:
                json.dump(data, f, indent = 4)
                
            return await message.channel.send('{} Dragon currently ravaging our lands has {:,}hp\n'
                                  'To see the list of dragonslay hp by province, use'
                                  '`!fluffy slay`.'.format(dragon_color.capitalize(),
                                  dragon_hp))
        
    @fluffy.command(name="slay", pass_context=True)
    async def fluffy_slay(self, ctx):
        with open ("/home/pi/cretobot/dragonScript.json", "r") as f:
            data = json.load(f)
            
        await ctx.send('\n'.join(("{} | {:,.0f}hp".format(x["name"], x["slay"])) for x in data["slay_list"]))

def setup(bot):
    bot.add_cog(Dragon(bot))
