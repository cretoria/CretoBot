
import discord
import logging
import datetime

from discord.ext import commands

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='/home/pi/cretobot/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # So I can easily get discord IDs on mobile
    @commands.command(hidden=True)
    @commands.is_owner()
    async def i(self, ctx):
        await ctx.send(ctx.channel.id)
        
    @commands.command(hidden=True)
    async def github(self, ctx):
        await ctx.send('https://github.com/cretoria/Rockbot')
        
    
    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cogload(self, ctx, *, cog: str):
        """Command which Loads a Module."""

        try:
            self.bot.load_extension('cogs.'+cog)
        except Exception as e:
            await ctx.send('Failed to load extension {}\n{}: {}'.format(
                    extension, type(e).__name__, e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cogunload(self, ctx, *, cog: str):
        """Command which Unloads a Module."""

        try:
            self.bot.unload_extension('cogs.'+cog)
        except Exception as e:
            await ctx.send('Failed to load extension {}\n{}: {}'.format(
                    extension, type(e).__name__, e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', aliases=["rl"], hidden=True)
    @commands.is_owner()
    async def cogreload(self, ctx, *, cog: str):
        """Command which Reloads a Module."""

        try:
            self.bot.unload_extension('cogs.'+cog)
            self.bot.load_extension('cogs.'+cog)
        except Exception as e:
            await ctx.send('Failed to load extension {}\n{}: {}'.format(
                    extension, type(e).__name__, e))
        else:
            await ctx.send('**`SUCCESS`**')
            
    
            
#     @commands.command(aliases = ['mlog'], hidden=True)
#     @commands.is_owner()
#     async def msg_log(self, ctx):
#         def transform(message):
#             if message.content.endswith(').'):
#                 result = message.content[17:message.content.find(' [')]
#                 return result
#             elif 'bounce' in message.content:
#                 result = message.content[17:message.content.find(' [')]
#                 return result
#        
#         agestart = datetime.datetime(2018,7,16,0,0)
#         warstart = datetime.datetime(2018,9,14,10,18)
#        jun9yr8 = datetime.dateime(2018,9,15,21,23)
#         attacks = await ctx.channel.history(limit=None, after=agestart).map(transform).flatten()
#         print('\n'.join(('{}'.format(x)) for x in attacks if x != None))
#         async for content in ctx.channel.history(limit=10).map(transform):
#             print(content)


def setup(bot):
    bot.add_cog(Admin(bot))
