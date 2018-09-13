import discord
import asyncio
import json
import aiohttp

from datetime import datetime as dt
from itertools import islice
from discord.ext import commands

UTOPIA_URL = "http://utopia-game.com/wol/game/kingdoms_dump/?key=l1FdkNfdklAs"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

class Meta:
    def __init__(self,bot):
        self.bot = bot
        self.saved_data = None
#         self.bot.session = aiohttp.ClientSession(loop=self.bot.loop)
        
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
        
        
    @commands.command()
    async def roster(self, ctx):
        e = discord.Embed(title='Shameless Kingdom Roster', color=0x000000)
        e.set_image(url='https://i.imgur.com/grEYenc.png')
        await ctx.send(content='Here you go you candy-ass jabroni...', embed=e)
    
     # Command to set our current KD
    @commands.command()
    @commands.has_any_role('leaders', 'admin')
    async def setkd(self, ctx, our_kd):
        print('ok')
        fresh_data = await self.get_data()
        print('ok.1')
        for d in fresh_data[1:-1]:
            if d.get("loc") == our_kd:  
                print('ok2')
                data = dict([x["name"], {"nw": x["nw"], "acres": x["land"],
                                "race": x["race"], "honor": x["honor"], "discord.id":
                                0, "discord.name": ""}] for x in d.get("provinces"))
                data["misc"] = {}
                data["misc"]["our_KD"] = our_kd
    
        with open ("/home/pi/cretobot/shameless77.json", "w+") as f:
            json.dump(data, f, indent=4, sort_keys=True)
    
        await ctx.send('Our KD set to ({}) and all province info populated.'
                       .format(our_kd))
    
    # Notify if person doens't have necessary role
    @setkd.error
    async def setkd_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have the necessary permissions for this command.')
            
    '''
    Piggyback on munkbot's !setprov to store discord ID in dragonScript.json
    along with the respective province name
    '''
    @commands.command(aliases=['provset'])
    async def setprov(self, ctx, *, prov_name):
        with open('/home/pi/cretobot/shameless77.json', 'r') as f:
            data = json.load(f)
        
        for p_name, p_info in data.items():
            if p_name == prov_name:
                p_info["discord.id"] = ctx.author.id
                p_info["discord.name"] = ctx.author.name
                # update KD json with data
                with open('/home/pi/cretobot/shameless77.json', 'w') as f:
                    json.dump(data, f, indent=4, sort_keys=True)
                return await ctx.send('Info updated to link your Discord user '
                                      'info with Rockbot\'s KD info')
            elif prov_name not in data.keys():
                return await ctx.send('Invalid province name, jabroni.')
        
    @commands.command()
    async def me(self, ctx):
        with open('/home/pi/cretobot/shameless77.json', 'r') as f:
            data = json.load(f)
        
        for p_name, p_info in data.items():
            if p_info["discord.id"] == ctx.author.id:
                print('id matched')
                embed = discord.Embed(color=0x4169e1)
                embed.set_author(name='Your Shameless User Info:')
                embed.set_thumbnail(url=
                                    "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024"
                                    .format(ctx.author))
                embed.add_field(name= "Province Name: ", value = p_name, inline=True)
                embed.add_field(name='Ruler: ', value=ctx.author.name, inline=True)
                embed.add_field(name='Nobility: ', value=p_info["honor"], inline=True)
                return await ctx.send(embed=embed)
    
    ### Custom help command
    @commands.command()
    async def help(self, ctx, cmd):
        
        if cmd.lower() == 'fluffy':
            embed = discord.Embed(color=0xffff00)
            embed.set_author(name='Help for your candy-ass')
            embed.add_field(name='**`!fluffy`**', value='Use along with sub-commands to'
                            ' calculate and set dragon fund and slay amounts.', inline=False)
            embed.add_field(name='`!fluffy cost [x:y] [color]`', value='Takes given target KD '
                            'and dragon type to calculate dragon cost. To use this '
                            'command you must include a KD location, i.e. 4:13, and '
                            'dragon color (sapphire, gold, ruby, emerald). With '
                            'proper parameters used the dragon cost is shown, and '
                            'if you are in @leaders you are given the option to set '
                            'the dragon, which will populate the fund cost for each '
                            'province.')
            embed.add_field(name='`!fluffy fund`', value='Lists the per-province'
                            ' funding amounts.')
            embed.add_field(name='`!fluffy slay`', value='Lists the per-province'
                            ' slay points.')
        else:
            embed = discord.Embed(title="Oops", color=0xffff00)
            embed.add_field(name='Need more info...', value=
                            'You need to include an existing command'
                            ' after !help, i.e. `!help [command]`')
        
        await ctx.send(embed=embed)
    
    # Retrieves our KD location from json
    @commands.command()
    async def kd(self, ctx):
        with open ("/home/pi/cretobot/shameless77.json", "r+") as f:
            data = json.load(f)
            our_kd = data["misc"]["our_KD"]
        await ctx.send('Our KD is ({}).'.format(our_kd))
        
    @commands.command()
    @commands.has_any_role('leaders', 'admin')
    async def rocksays(self, ctx, destination: discord.TextChannel=None, *, msg: str):
        
        #Makes the bot say something in the specified channel
                
        if not destination.permissions_for(ctx.author).send_messages:
            return await ctx.message.add_reaction("\N{WARNING SIGN}")
        
        destination = ctx.message.channel if destination is None else destination
        emoji = self.bot.get_emoji(466428026880786452)
        await destination.send(msg)
        return await ctx.message.add_reaction(emoji)
    
    # Notify if person doens't have necessary role
    @rocksays.error
    async def rocksays_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Quit posing, you candy-ass! You don\'t tell me what to do!')
        
    
        
def setup(bot):
    bot.add_cog(Meta(bot))
