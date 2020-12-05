import discord
import asyncio
import json
import aiohttp

from datetime import datetime as dt
from itertools import islice
from discord.ext import commands

UTOPIA_URL = "https://utopia-game.com/wol/game/kingdoms_dump/"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

class Dragon(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.saved_data = None
        self.bot.session = aiohttp.ClientSession(loop=self.bot.loop)
        
    async def get_data(self):
        # If saved data is None we haven't fetched anything, thanks to short-
        # circuiting we can check the index in the or clause safely
        # If 15 minutes has passed since the last data fetched, we need to update 
        # to make sure it's fresh
        if self.saved_data is None or (dt.utcnow() - dt.strptime(self.saved_data[0], 
                                       DATETIME_FORMAT)).total_seconds() // 60 > 15:
            await self.download_data()
        return self.saved_data

    async def download_data(self):
        async with self.bot.session.get(UTOPIA_URL) as r:
            data = await r.json()
        self.saved_data = data
                    
    # Group of commands to assist with dragon cost, funding, and slaying
    @commands.group(invoke_without_command=False, aliases=["dragoncost"], 
                    case_insensitive=True, no_pm=True)
    async def fluffy(self, ctx):
        pass
    
    @fluffy.command(name="cost", no_pm=True)
    async def fluffy_cost(self, ctx, target_kd, color):
        # start with populating the cost multiplier for the dragon types
        with open ("/home/pi/cretobot/shameless77.json", "r") as f:
            data = json.load(f)
            our_kd = data["misc"]["our_KD"]
           
        fresh_data = await self.get_data()

        # The json file has timestamps at the first and last index, 
        # we don't care about these
        for e in fresh_data[1:-1]:
            if e.get("loc") == our_kd:
                our_nw = e.get("nw")
            if e.get("loc") == target_kd:
                target_nw = e.get("nw")
       
        if color.lower() == "emerald":
            cost_metric = 3
        elif color.lower() == "ruby":
            cost_metric = 2.4
        elif color.lower() == "topaz":
            cost_metric = 2
        elif color.lower() == "sapphire":
            cost_metric = 2
        elif color.lower() == "amethyst":
            cost_metric = 2.4
        else:
            await ctx.send("Invalid color option, please use: emerald, ruby, "
                           "topaz, amethyst, or sapphire.")
        
        # apply the formula from the utopia wiki    
        dragon_cost = int(target_nw * 0.656 * cost_metric)
        await ctx.send("Total cost for a {} dragon will be {:,}gc.".format(color,
                       dragon_cost))
        
        # if person calling command is a KD leader, give option to set the target 
        # KD, dragon cost, and per province dragonshare and store in the json file
        ok_roles = ['leaders', 'admin']
        roles = {x for x in ctx.guild.roles if x.name in ok_roles}
        if roles & set(ctx.author.roles):
            await ctx.send("Would you like to set this cost for dragonshare "
                           "purposes? (respond with 'yes' if so)")
            def check(m):
                return m.content.lower()=='yes'
            await self.bot.wait_for('message', timeout=20.0, check=check)

            # populate province list with province name and respective dragonshare
            fresh_data = await self.get_data()
            for d in fresh_data[1:-1]:
                if d.get("loc") == our_kd: 
                    for x in d.get("provinces"):
                        for p_name, p_info in data.items():
                            if x["name"] == p_name:
                                p_info["share"] = int(x["nw"]/d["nw"]*dragon_cost*1.1)
                        
#                     data = dict([x["name"], {"name": x["name"], "nw": x["nw"], "share": 
#                                  x["nw"]/d["nw"]*dragon_cost*1.1}] for x in d.get("provinces"))
            data["misc"]["dragon_cost"] = dragon_cost
            data["misc"]["target_KD"] = target_kd

            # update dragonScript json with target kd and province share info
            with open("/home/pi/cretobot/shameless77.json", "w+") as f:
            #with open ("/home/pi/cretobot/dragonScript.json", "w+") as f:
                json.dump(data, f, indent = 4, sort_keys=True)
                
            return await ctx.send('Dragon target successfully set to ({}) for a {} '
                                  'dragon with total cost of {:,}gc.\n To see the list '
                                  'of dragonshares by province, use `!fluffy fund`.'
                                  .format(target_kd, color, dragon_cost))
    
    @fluffy.command(name="price", no_pm=True)
    async def fluffy_price(self, ctx, target_nw: int, color):
            
        if color.lower() == "emerald":
            cost_metric = 3
        elif color.lower() == "ruby":
            cost_metric = 2.4
        elif color.lower() == "topaz":
            cost_metric = 2
        elif color.lower() == "sapphire":
            cost_metric = 2
        elif color.lower() == "amethyst":
            cost_metric = 2.4
        else:
            await ctx.send("Invalid color option, please use: emerald, ruby, "
                           "topaz, amethyst, or sapphire.")
        
        # apply the formula from the utopia wiki    
        dragon_cost = int(target_nw * 0.656 * cost_metric)
        await ctx.send("Total cost for a {} dragon will be {:,}gc.".format(color,
                       dragon_cost))
        
       
        
    @fluffy.command(name="fund", pass_context=True)
    async def fluffy_fund(self, ctx):
        with open ("/home/pi/cretobot/shameless77.json", "r") as f:
            data = json.load(f)
        
        await ctx.send('\n'.join(('{} | {:,}gc'.format(p_name, p_info["share"])
                                     for p_name, p_info in data.items() if
                                     p_name != 'misc')))

    
    @commands.command(name="myfund", aliases=["myshare"], pass_context=True)
    async def _myfund(self, ctx):
        with open("/home/pi/cretobot/shameless77.json", "r") as f:
            data = json.load(f)
        not_here = 1     
        for p_name, p_info in data.items():
            if p_name != "misc" and p_info["discord.id"] == ctx.author.id:
                not_here = 0
                return await ctx.send('Your total fund amount is {:,}gc.'
                               .format(p_info["share"]))
            
        if not_here == 1:
            await ctx.send('Your Discord user is not currently linked to any '
                           'province for Rockbot commands. Please do `!provset '
                           '[Province Name]` to link, then try this command again.')
                
    ### Listen in #internal channel for dragon-arrived post, then calc HP and prov shares
    @commands.Cog.listener()
    async def on_message(self, message):
        dragon_here = 'has begun ravaging'
        ### This is the funding tracker, need to refine still
#         if message.channel.id == 443472774179061790 and message.author.id == 401475129550438400:
#             with open('/home/pi/cretobot/dragonFund.json', 'r') as f:
#                 fund = json.load(f)
#             fundpost = message.content
#             fund_amt = int(''.join(filter(str.isdigit, fundpost)))
#             entry = {'Province': fundpost[25:fundpost.find(' [')], 'Amount': fund_amt}
#             fund.append(entry)
#             with open('/home/pi/cretobot/dragonFund.json','w') as f:
#                 json.dump(fund, f, indent = 2)
        ### End funding tracker
                
        if dragon_here in message.content:
            ### Get the dragon color
            words = message.content.split()
            if 'Dragon,' in message.content:
                dragon_color = words[words.index('Dragon,')-1].lower()
                print(dragon_color)
            else:
                dragon_color = words[words.index('Dragon')-1].lower()
            
            with open("/home/pi/cretobot/shameless77.json", "r") as f:
                data = json.load(f)
                our_kd = data["misc"]["our_KD"]
                
            fresh_data = await self.get_data()
            
            for e in fresh_data[1:-1]:
                if e.get("loc") == our_kd:
                    our_nw = e.get("nw")
                    
            if dragon_color == 'sapphire':
                hp_mod = 6.375
            elif dragon_color == 'topaz':
                hp_mod = 6.375
            elif dragon_color == 'ruby':
                hp_mod = 7.65
            elif dragon_color == 'emerald':
                hp_mod = 9.5625
            elif dragon_color == 'amethyst':
                hp_mod = 7.65
            else:
                return
            
            dragon_hp = int(hp_mod * our_nw / 132)
           
             # populate province list with province name and respective slay cost
            for d in fresh_data[1:-1]:
                if d.get("loc") == our_kd: 
                    for x in d.get("provinces"):
                        for p_name, p_info in data.items():
                            if x["name"] == p_name:
                                p_info["slay"] = int(x["nw"]/d["nw"]*dragon_hp*1.1)
            
            # update dragonScript json with province slay info
            with open ("/home/pi/cretobot/shameless77.json", "w+") as f:
                json.dump(data, f, indent = 4, sort_keys=True)
            leader_chan = self.bot.get_channel(435901894133547018)
#             await leader_chan.send('<@&{}> We have a dragon. Slay values '
#                            'have been posted in #announcements - let folks know '
#                            'what the slay orders are!'.format(435856600998215690))
            chan = self.bot.get_channel(445407642349993987)
            await chan.send('{} Dragon currently ravaging our lands has {:,}hp\n'.format(
                                    dragon_color.capitalize(), dragon_hp))
            await chan.send('\n'.join(("{} | {:,}hp".format(p_name, p_info["slay"])) 
                                       for p_name, p_info in data.items() if p_name
                                       != "misc"))
            return await chan.send('Leaders have been pinged that a dragon is here. We will'
                            ' typically slay our dragons ASAP according to this NW-'
                            'based allocation, but sending troops prior to an order'
                            ' from Leaders is at your own risk.')
        
    @fluffy.command(name="slay", pass_context=True)
    async def fluffy_slay(self, ctx):
        with open ("/home/pi/cretobot/shameless77.json", "r") as f:
            data = json.load(f)
            
        await ctx.send('\n'.join(("{} | {:,}hp".format(p_name, p_info["slay"])) 
                                  for p_name, p_info in data.items() if p_name
                                  != "misc"))
        
    @commands.command(name="myslay", pass_context=True)
    async def _myslay(self, ctx):
        with open("/home/pi/cretobot/shameless77.json", "r") as f:
            data = json.load(f)
        
        not_here = 1
        for p_name, p_info in data.items():
            if p_name != "misc" and p_info["discord.id"] == ctx.author.id:
                not_here = 0
                return await ctx.send('Your total slay amount is {:,}hp.'
                               .format(p_info["slay"]))
            
        if not_here == 1:
            await ctx.send('Your Discord user is not currently linked to any '
                           'province for Rockbot commands. Please do `!provset '
                           '[Province Name]` to link, then try this command again.')
            
    @fluffy.command(name='help', pass_context=True)
    async def fluffy_help(self, ctx):
        
        embed = discord.Embed(color=0xffff00)
        embed.set_author(name='Dragon commands help for your candy-ass')
        embed.add_field(name='`!fluffy cost [x:y] [color]`', value='Takes given target '
                        'KD and dragon type to calculate dragon cost. To use this '
                        'command you must include a KD location, i.e. 4:13, and '
                        'dragon color (sapphire, gold, ruby, emerald). With '
                        'proper parameters used the dragon cost is shown, and '
                        'if you are in @leaders you are given the option to set '
                        'the dragon, which will populate the fund cost for each '
                        'province.')
        embed.add_field(name='`!fluffy fund`', value='Lists the per-province'
                        ' funding amounts.', inline=False)
        embed.add_field(name='`!fluffy slay`', value='Lists the per-province'
                        ' slay points.', inline=False)
        embed.add_field(name='`!myfund`', value='Gives the user\'s individual '
                        'dragon funding responsibility. If you have not previously '
                        'linked your Discord user and province via `!setprov '
                        '[Province Name]`, you will receive an error advising you '
                        'to do so.')
        embed.add_field(name='`!myslay`', value='Gives the user\'s individual '
                        'dragon slay responsibility. If you have not previously '
                        'linked your Discord user and province via `!setprov '
                        '[Province Name]`, you will receive an error advising you '
                        'to do so.')
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Dragon(bot))
