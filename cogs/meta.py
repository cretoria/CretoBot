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
        
    
        
def setup(bot):
    bot.add_cog(Meta(bot))
