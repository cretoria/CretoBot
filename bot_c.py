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
 
description = 'This is my bot. I like it -- when it works...'


class RockBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", description=description, case_insensitive=True)
        self.client_id = 460400451645472782
        self.owner_id = 404071518159634452
        self.add_command(self.setkd)
        self.add_command(self.kd)
        self.add_command(self.list_provs)
        self.session = aiohttp.ClientSession(loop=self.loop)
                
        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(
                    extension, type(e).__name__, e))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
    
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
        
    async def on_message(self, message):
        if message.channel.name == 'dragon' and message.author.name == 'munkbot':
            with open('dragonFund.json', 'r') as f:
                fund = json.load(f)
            fundpost = message.content
            fund_amt = int(''.join(filter(str.isdigit, fundpost)))
            entry = {'Province': fundpost[25:fundpost.find(' [')], 'Amount': fund_amt}
            fund.append(entry)
            with open('dragonFund.json','w') as f:
                json.dump(fund, f, indent = 2)
        await self.process_commands(message)
    
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
