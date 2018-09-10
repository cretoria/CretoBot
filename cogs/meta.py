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
        
    '''
    Piggyback on munkbot's !setprov to store discord ID in dragonScript.json
    along with the respective province name
    '''
    @commands.command()
    async def setprov(self, ctx, *, prov_name):
        with open('dragonScript.json', 'r') as f:
            data = json.load(f)
        
        provinces = data['provinces']
        blah = next((x for x in provinces if x['name'] == prov_name), None)
        print(blah)
        if blah != None:
            blah.update({'discord.id' : ctx.author.id,
                         'discord.name' : ctx.author.name})
            await ctx.send('Info updated to link your Discord user info with'
                           ' Rockbot\'s KD info')
            
            # update KD json with data
            with open('dragonScript.json', 'w') as f:
                json.dump(data, f, indent=4)
        else:
            return await ctx.send('Check if {} is new province or spelled '
                                  'incorrectly.'.format(prov_name))
    
    @commands.command()
    async def me(self, ctx):
        with open('dragonScript.json', 'r') as f:
            data = json.load(f)
        await ctx.send(ctx.author.id)
        
        info = data['provinces']
        blah = next((x for x in info if x['discord.id'] == 
                    ctx.author.id), None)
        if blah == None:
            await ctx.send('none')
        name = blah['name']
        discord_id = blah['discord.id']
        
        await ctx.send('{}|{}'.format(name, discord_id))
        embed = discord.Embed(title='Your KD Info:', color=0x4169e1)
        embed.set_thumbnail(ctx.author.avatar_url)
        embed.add_field(name= "Province Name:", value = ['name'])
        embed.add_field(name='Ruler:', value=ctx.author.name)
        
        #await ctx.send(embed=embed)
    
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
