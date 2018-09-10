import discord
import logging

from discord.ext import commands

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='/home/pi/cretobot/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class Admin:

    def __init__(self, bot):
        self.bot = bot
    
    # So I can easily get discord IDs on mobile
    @commands.command(hidden=True)
    @commands.is_owner()
    async def i(self, ctx):
        await ctx.send(ctx.channel.id)
        
    
    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog: str):
        """Command which Loads a Module."""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send('Failed to load extension {}\n{}: {}'.format(
                    extension, type(e).__name__, e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog: str):
        """Command which Unloads a Module."""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send('Failed to load extension {}\n{}: {}'.format(
                    extension, type(e).__name__, e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', aliases=["rl"], hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module."""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send('Failed to load extension {}\n{}: {}'.format(
                    extension, type(e).__name__, e))
        else:
            await ctx.send('**`SUCCESS`**')


def setup(bot):
    bot.add_cog(Admin(bot))