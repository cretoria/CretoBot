import random
import json
import discord

from discord.ext import commands

class Meta:
    def __init__(self,bot):
        self.bot = bot
        
    @commands.command()
    async def roster(self, ctx):
        e = discord.Embed(title='Shameless Kingdom Roster', color=0x000000)
        e.set_image(url='https://i.imgur.com/grEYenc.png')
        await ctx.send(content='Here you go you candy-ass jabroni...', embed=e)
            
    # Command to set our current KD
    @commands.command()
    @commands.has_any_role('leaders', 'admin')
    async def setkd(self, ctx, our_kd):
        with open ("/home/pi/cretobot/dragonScript.json", "r+") as f:
            data = json.load(f)
        
        data["our_KD"] = our_kd
    
        with open ("/home/pi/cretobot/dragonScript.json", "w+") as f:
            json.dump(data, f, indent=4)
    
        await ctx.send('Our KD set to ({}).'.format(our_kd))
    
    # Notify if person doens't have necessary role
    @setkd.error
    async def setkd_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You do not have the necessary permissions for this command.')
    
    # Retrieves our KD location from json
    @commands.command()
    async def kd(self, ctx):
        with open ("/home/pi/cretobot/dragonScript.json", "r+") as jsonFile:
            data = json.load(jsonFile)
            our_kd = data["our_KD"]
        await ctx.send('Our KD is ({}).'.format(our_kd))
        
    
        
def setup(bot):
    bot.add_cog(Meta(bot))
