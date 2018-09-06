import discord
import asyncio
import config
import json
import aiohttp

from discord.ext import commands

INITIAL_EXTENSIONS = [
    'cogs.admin',
    'cogs.dragon', 
    'cogs.meta'
]
 
description = 'A bot made for the renowned kingdom of Shameless.'

class RockBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", description=description, case_insensitive=True)
        self.client_id = 460400451645472782
        self.owner_id = 404071518159634452
                                
        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(
                    extension, type(e).__name__, e))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
    
    # lemme know that bot is working...
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        print(discord.__version__)
     
    async def on_message(self, message):
        if message.author.bot:
            return
        if 'honot' in message.content.lower():
            await message.channel.send('We must protect our honot!')
        await self.process_commands(message)
                           
    def run(self):
        super().run(config.token, reconnect=True)
    
if __name__ == '__main__':
    bot = RockBot()
    bot.run()
