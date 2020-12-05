import discord
import asyncio
import json
import urllib
import aiohttp
import random
import collections
import re

from datetime import datetime as dt
from itertools import islice
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

UTOPIA_URL = "http://utopia-game.com/wol/game/kingdoms_dump/?key=l1FdkNfdklAs"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
shameless_json = '/home/pi/cretobot/shameless77.json'
gp_supporters = ['calamity',
                 'marrek',
                 'cheese',
                 'dnomder',
                 'selwonk'
                ]
gp_needers = ['Beer Bear',
              'Bully Bear',
              'Cunning Linguist Bear',
              'Discrete Bear',
              'Dont Care Bear',
              'Dumpster Fire Bear',
              'Faceless Bear',
              'Gentle Assassin Bear',
              'Grumpy Bear',
              'Illuminati Bear',
              'Jeer Bear',
              'Karen Bear',
              'Nair Bear',
              'Nice Personality Bear',
              'No Chill Bear',
              'Only Fans Bear',
              'Sadistic Bear',
              'Totally Shameless Bear',
              'Troll Bear'
             ]

class Meta(commands.Cog):
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
    
    # Command to add Dunce role to person, including increasing counter in KD json
    @commands.command(aliases=['dunce','givedunce'])
    @commands.has_role('leaders')
    async def _dunce(self, ctx, duncee, *, dunce_reason: str=None):
        
        with open(shameless_json, 'r') as f:
            data = json.load(f)
            
        member = ctx.guild.get_member(int(duncee.strip('<@!>')))
        dunce_role = discord.utils.get(ctx.guild.roles, id=739615380787429516)
        await member.add_roles(dunce_role, reason=dunce_reason)
        
        ### Update individual member dunce count
        for p_name, p_info in data.items():
            if p_name != "misc" and p_info["discord.id"] == member.id:
                p_info['dunce_count'] += 1
                dunce_count=p_info['dunce_count']
                
        ### Send embed containing dunce post to #dunce-corner
        dunce_channel = self.bot.get_channel(759132744252391505)
        
        embed = discord.Embed(title='SOMEONE HAS BEEN DUNCED!', color=0x96b403)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/404868940683149332/743549927799390228/rock-dunce.jpg')
        embed_text = ('Here\'s why: __{}__ \n'
                      'Number of times {} has been dunced this age: **{}**'.format(
                         dunce_reason, member.name, dunce_count))
        embed.add_field(name= '{} is a dunce for 12 hours!'.format(member.name),                                                                                                 value = embed_text)
#         value = 'Here\'s why: {}\n'
#                         'Number of times {} has been a dunce this age: **{}**'.format(
#                             dunce_reason, member.name, p_info['dunce_count']))
        await ctx.send(embed=embed)
        await dunce_channel.send(embed=embed)
    
        with open(shameless_json, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
        
        await asyncio.sleep(43200)
        await member.remove_roles(dunce_role)
        
    # Notify if person doens't have necessary role
    @_dunce.error
    async def _dunce_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Go sit your candy-ass down! You\'re not the Monarch or a Steward...')
    
    # Command to calcualte books needed for desired science effect
    @commands.command(aliases=['books','booksneeded','books_needed'])
    async def _books_needed(self, ctx, chosen_cat: str=None, chosen_inc: str=None):
        author = ctx.author
        # Cal doesn't get to use this nifty tool
        if author.id == 217085842307547136:
            return await ctx.send('Sorry Cal, this tool is only available for those who'
                                 ' believe in the benfits of science. Please fuck off'
                                 ' and try again later. Have a nice day.')        
        # Define the science category multipliers
        # These are as of Age 87 from the Wiki
        cat_list = collections.OrderedDict([
            ('alchemy',('Income',0.0724)),   
            ('tools',('Building Effectiveness',0.0524)),
            ('housing',('Population Limit',0.0262)),
            ('production',('Food & Rune Production',0.2492)),
            ('bookkeeping',('Wage Reduction',0.068)),
            ('artisan',('Construction Time & Cost',0.0478)),
            ('strategy',('Defensive Military Efficiency',0.0367)),
            ('siege',('Battle Gains',0.0262)),
            ('tactics',('Offensive Military Efficiency',0.0418)),
            ('valor',('Military Train Time & Dragon Slaying',0.0582)),
            ('heroism',('Draft Speed & Cost',0.0418)),
            ('crime',('Thievery Effectiveness',0.1557)),
            ('channeling',('Magic Effectiveness',0.1875)),
            ('shielding',('Reduced Damage from Enemy Ops',0.0314)),
            ('cunning',('Increased Ops Damage',0.0472)),
            ('invocation',('Ritual Rune Cost Reduction',0.0622))])
        
        if chosen_cat != None and chosen_inc == None:
            return await ctx.send('If you\'re trying to use the shortcut method, the syntax is:'
                          '```!books [number for science category] [number for increase percent]```')
        elif chosen_cat != None and chosen_inc != None:
            #Determine if the race mod should be changed by checking user against Shameless json data
            with open(shameless_json, 'r+') as f:
                data = json.load(f)
            for p_name, p_info in data.items():
                if p_name != 'misc' and p_info['discord.id'] == author.id:
                    if p_info['race'] == 'Human':
                        race_mod = 1.1
                        race = 'Human'
    #                 elif p_info['race'] == 'Undead':
    #                     race_mod = 0.5
    #                     race = 'Undead'
                    else:
                        race_mod = 1
                        race = None
            try:
                val = int(chosen_cat)
                        
            except ValueError:
                await ctx.send('```Science category needs to be a whole number.\n'
                               'Please start over.```')
            
            if not 1 <= int(chosen_cat) <= 16:
                return await ctx.send('```Pick 1-16.\nPlease start over.```')
            
            try:
                chosen_inc = float(chosen_inc)

            except ValueError:
                await ctx.send('```Percentage increase needs to be a number, e.g. 5, 10.8, 20.\n'
                               'Please start over.```')

            for i,(cat,(desc,mult)) in enumerate(cat_list.items(),start=1):
                if i==int(chosen_cat):
                    needed = round((float(chosen_inc)/(mult*race_mod))**2.125)
                    return await ctx.send('{:,} books needed in {} for a desired effect of {}%.'.format(needed,cat,chosen_inc))   

            if race != None:
                await ctx.send('*Note this includes your {} science modifier.*'.format(race))
        else:
            pass
        
        await ctx.send('\n'.join('{} - {} ({})'.format(i,x.capitalize(),y) 
                                 for i, (x,(y,z)) in enumerate(cat_list.items(),start=1)))
        # Define other variables of the science formula
        race_mod = 1
        multiplier = 1
            
        def check(m):
            return m.author == author
        
        #Determine if the race mod should be changed by checking user against Shameless json data
        with open(shameless_json, 'r+') as f:
            data = json.load(f)
            
        for p_name, p_info in data.items():
            if p_name != 'misc' and p_info['discord.id'] == author.id:
                if p_info['race'] == 'Human':
                    race_mod = 1.1
                    race = 'Human'
#                 elif p_info['race'] == 'Undead':
#                     race_mod = 0.5
#                     race = 'Undead'
                else:
                    race_mod = 1
                    race = None
        
        #Get the science category to calculate books for
        await ctx.send('Which science category would you like me to calculate the needed books for?\n'
                       '*(Enter the number corresponding to your desired choice (1-16).)*')

       
        try:
            sci_cat = await self.bot.wait_for('message', timeout=30.0, check=check)
                        
        except asyncio.TimeoutError:
            await ctx.send('```Too slow choosing jabroni, try !books again when'
                           ' you\'ve made up your mind!```')
        else:
            chosen_cat = sci_cat.content
            print(chosen_cat)
        
        try:
            val = int(chosen_cat)
                        
        except ValueError:
            await ctx.send('```Needs to be a number.```')
            
        if not 1 <= int(chosen_cat) <= 16:
            return await ctx.send('```Pick 1-16.```')
        
        await ctx.send("What is your target effect? *i.e. 15% increase, then enter 15*")
        try:
            sci_inc = await self.bot.wait_for('message', timeout=30.0, check=check)
                        
        except asyncio.TimeoutError:
            await ctx.send('```too slow```')
            
        else:
            chosen_inc = sci_inc.content
                    
        try:
            chosen_inc = float(chosen_inc)
            
        except ValueError:
            await ctx.send('```Needs to be a number.```')
        
        for i,(cat,(desc,mult)) in enumerate(cat_list.items(),start=1):
            if i==int(chosen_cat):
                needed = round((chosen_inc/(mult*race_mod))**2.125)
                await ctx.send('{:,} books needed in {} for a desired effect of {}%.'.format(needed,cat,chosen_inc))   
                
        if race != None:
            await ctx.send('*Note this includes your {} science modifier.*'.format(race))
        
        ### Science Bonus = ( # of Books in Type )^(1/2.125) * Science Multiplier * Race Mod
        
        
    @commands.command()
    async def roster(self, ctx):
        await ctx.send('https://cdn.discordapp.com/attachments/435902101810577458/757668183044915290/image0.jpg')
#         e = discord.Embed(title='Shameless Kingdom Roster', color=0x000000)
#         e.set_image(url='https://media.discordapp.net/attachments/404868940683149332/618891889390780431/roster_82_9-4-19.jpg')
#         await ctx.send(content='Here you go you candy-ass jabroni...', embed=e)
#         await ctx.send('I\'d be happy to serve up our current KD roster for you to reference.'
#                       '\n\nBefore I do, though, please answer the following question:using the '
#                       'the number of the choice that best describes you:\n\n'
#                       '1. I feel like a beautiful princess with long, golden locks.\n'
#                       '2. I feel like strapping on my boat shoes and spending a day at sea.\n'
#                       '3. I feel like celebrating my favorite holiday, All Hallows\' Eve.\n'
#                       '4. On Wednesdays we wear pink.\n'
#                       '5. I feel devoid of any excitement in my life.\n'
#                       '6. I like surprises. Life is better when you don\'t know what\'s around the corner.')
        
#         author = ctx.author
        
#         def check(m):
#             return m.author == author
        
#         roster_choice = await self.bot.wait_for('message', timeout=60.0, check=check)
        
#         if roster_choice.content == '1':
#             await ctx.send('https://media.discordapp.net/attachments/435902101810577458/633753890549923851/SnipImage.JPG\n'
#                            'https://media.giphy.com/media/W5yshKbH5wrwA/giphy.gif')
#         elif roster_choice.content == '2':
#             await ctx.send('https://media.discordapp.net/attachments/404868940683149332/633736850305056778/roster-832.jpg')
#         elif roster_choice.content == '3':
#             await ctx.send('https://media.discordapp.net/attachments/435902101810577458/633749734208700437/SnipImage.JPG')
#         elif roster_choice.content == '4':
#             await ctx.send('https://media.discordapp.net/attachments/435902101810577458/633749678642429952/SnipImage.JPG')
#         elif roster_choice.content == '5':
#             await ctx.send('https://media.discordapp.net/attachments/435902101810577458/633749607116963868/SnipImage.JPG')
#         elif roster_choice.content == '6':
#             random_url = ['https://media.discordapp.net/attachments/435902101810577458/633753890549923851/SnipImage.JPG \n https://media.giphy.com/media/W5yshKbH5wrwA/giphy.gif',
#                           'https://media.discordapp.net/attachments/404868940683149332/633736850305056778/roster-832.jpg',
#                           'https://media.discordapp.net/attachments/435902101810577458/633749734208700437/SnipImage.JPG',
#                           'https://media.discordapp.net/attachments/435902101810577458/633749678642429952/SnipImage.JPG',
#                           'https://media.discordapp.net/attachments/435902101810577458/633749607116963868/SnipImage.JPG']
#             random_roster = random.choice(random_url)
#             await ctx.send('{}'.format(random_roster))
#         else:
#             await ctx.send('Sorry jabroni...you seem to have difficulty understanding simple numbers.')
        
    
     # Command to set our current KD
    @commands.command()
    @commands.has_any_role('admin')
    async def setkd(self, ctx, our_kd):
        fresh_data = await self.get_data()
        for d in fresh_data[1:-1]:
            if d.get("loc") == our_kd:  
                data = dict([x["name"], {"nw": x["nw"], "acres": x["land"],
                             "race": x["race"], "honor": x["honor"], "discord.id":
                             0, "discord.name": "", "bounces": 0, "points": 0, "dunce_count": 0,"whois": "", "last_bounce": ""}]
                             for x in d.get("provinces"))
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
        with open(shameless_json, 'r') as f:
            data = json.load(f)
        
        for p_name, p_info in data.items():
            if p_name == prov_name:
                p_info["discord.id"] = ctx.author.id
                p_info["discord.name"] = ctx.author.name
                # update KD json with data
                with open(shameless_json, 'w') as f:
                    json.dump(data, f, indent=4, sort_keys=True)
                return await ctx.send('Info updated to link your Discord user '
                                      'info with Rockbot\'s KD info')
            elif prov_name not in data.keys():
                return await ctx.send('Invalid province name, jabroni.')
    
    ### Our own custom dice roller
    @commands.command()
    async def roll(self, ctx, *, dsides: int=None):
        if dsides == None:
            dsides = 20
        await ctx.send('**{}** rolled {}.\n*(using a d{} :game_die:)*'.format(
                       ctx.message.author.name,random.randint(1,dsides),dsides))
    
    @commands.command()
    async def giphy(self, ctx, *, giphy_search: str):
        giphy_search_urlify = giphy_search.replace(" ","-")
        search_url = "https://api.giphy.com/v1/gifs/random?api_key=6w7qM8L6T0Z3OkwtUX1ahBhWLBK3A2Zs&tag="+giphy_search_urlify+"&rating=G"
        print(search_url)
        async with self.bot.session.get(search_url) as r:
            data = await r.json()
            return await ctx.send(data["data"]["url"])
    
    @commands.command()
    async def me(self, ctx):
        with open(shameless_json, 'r') as f:
            data = json.load(f)
        
        for p_name, p_info in data.items():
            if p_name != 'misc' and p_info["discord.id"] == ctx.author.id:
                embed = discord.Embed(color=0x4169e1)
                embed.set_author(name='Your Shameless User Info:')
                embed.set_thumbnail(url=
                                    "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024"
                                    .format(ctx.author))
                embed.add_field(name= "Province Name: ", value = p_name, inline=True)
                embed.add_field(name='Ruler: ', value=ctx.author.name, inline=True)
                embed.add_field(name='Nobility: ', value=p_info["honor"], inline=True)
                embed.add_field(name='Bounces: ', value=p_info['bounces'])
                return await ctx.send(embed=embed)
    
    #Embed that lists the primary bot commands useful for @leaders
    @commands.command(aliases=['lh','helpleader','leaderhelp','leaders_help'])
    async def leader_help(self, ctx):
        embed = discord.Embed(color=0x3498db)
        embed.title = "Common Leader Commands"
        embed.add_field(name='__Using this guide__', value='With any of these, '
                       'you can use either . or ! to call the command. Whenever '
                       'there is [some text] listed in the syntax, you don\'t need '
                       'those square brackets.')
        embed.add_field(name='__The Basics__', value='**Orders**\n'
                       'Adding an order: ```.addorder [order text]\ne.g. .addorder Raze Calamity```\n'
                       'Deleting an order: ```.delorder [order ID number]\ne.g. .delorder 22```\n'
                       'Deleting all orders: *careful this can\'t be undone* ```.delallorders```\n'
                       '**Events**\n'
                       'Adding an event: ```.addevent [mmmDDyrX] [event text]\ne.g. .addorder apr9yr4 wave date```\n'
                       'Deleting an event: ```.delevent [event ID number]```\n'
                       'Display events: ```.events```\n'
                       '**Ops Plan**\n'
                       'When a war is over, or if a wave doesn\'t pan out but ops are already loaded, use this to clear them:'
                       '```.resetopplan```')
        embed.add_field(name='__Dragon Cost Calculator__', value='To determine the cost of a dragon against a '
                       'target kingdom, use: ```!fluffy cost [target KD] [emerald|ruby|amethyst|sapphire|topaz]\n'
                       'e.g. !fluffy cost 1:1 ruby```Rockbot will post the cost, and if you want to set this for '
                       'province funding amounts, the leader who called the command must type and enter "Yes" within '
                       '20 seconds or it will timeout.')
        embed.add_field(name='__Rockbot Points System__', value='To give or remove points, anyone with a leader '
                       'role may do so. Use the command below, and note that "!points" will always be a valid '
                       'command tag, but we often use a theme-specific command as well such as "!hugs" or "!takeout".'
                       '```!points [@user] [number of points, lead with - to remove] [reason for points{optional}]\n'
                       'e.g. !points @Dev 5 intel\n'
                       'e.g. !points @Calamity -5 being a douche```')
        return await ctx.send(embed=embed)
    
    @commands.command()
    async def support(self, ctx):
        
        embed = discord.Embed(color=0x1abc9c)
        embed.title = "Support Spells Cheatsheet"
        embed.add_field(name='__Provs to check for Greater Protection__', value='\n'.join(gp_needers), inline=False)
        embed.add_field(name='\n__REMINDER__', value='The best way to see if someone needs GP when there aren\'t spells'
                       'requested in the !request function is to check https://utopia-game.com/wol/game/kingdom_intel/8/3'
                       ', and check to see if the provs listed above show GP in effect.')
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def war_report(self, ctx):
        report_contents = open('/home/pi/cretobot/war_report.txt').readlines()

        chunk1 = report_contents[4:35]
        chunk2 = report_contents[35:65]
        chunk3 = report_contents[65:95]
        chunk4 = report_contents[95:125]
        chunk5 = report_contents[125:]
        print(len(report_contents))
       
        
        
        embed = discord.Embed(color=0xffff00)
        embed.title = "Current War Report"
        embed.description = report_contents[1]
        embed.add_field(name='\u200b', value=''.join(chunk1), inline=False)
        embed.add_field(name='\u200b', value=''.join(chunk2), inline=False)
        embed.add_field(name='\u200b', value=''.join(chunk3), inline=False)
        embed.add_field(name='\u200b', value=''.join(chunk4), inline=False)
        embed.add_field(name='\u200b', value=''.join(chunk5), inline=False)
        
        await ctx.send(embed=embed)

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
        elif cmd == 'points':
            embed = discord.Embed(color=0xffff00)
            embed.set_author(name='Help on the team points system for your candy-ass')
            embed.add_field(name='`!teams | !teamlist | !listteams`', value=
                            'Shows the current makeup of the three teams.')
            embed.add_field(name='`!mypoints`', value='Lists your team\'s current'
                            ' number of points, as well as your individual points'
                            ' for the age.')
            embed.add_field(name='`!scoreboard`', value='Shows current points '
                            'for all teams, along with the team leaders.')
            embed.add_field(name='`!points` (Leaders Only)', value='If you have '
                            'the @leaders> role, you can assign or '
                            'take away points using the following syntax:\n'
                            '`!points [@user] [number of points] [reason(optional)]'
                            '\n *Note: to remove points, just use "-".*')
            embed.add_field(name='\u200b', value='A log of points given/taken '
                            'can be found in the <#499226632704229376> channel.')
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
        
    # Sets value in Shameless JSON file for the .whois trigger
    @commands.command()
    @commands.has_any_role('leaders', 'admin')
    async def setwhois(self, ctx, member_to_change, *, new_whois: str=None):
        print(member_to_change[0])
        if member_to_change[0] != "<":
            return await ctx.send("Please be sure you are using the correct format"
                                 " ```!setwhois @user [URL or desired phrase]```")
        if new_whois == None:
            new_whois = ""
        member_to_change = member_to_change.replace('!','')
        member_stripped = ctx.guild.get_member(int(member_to_change.strip('<@>')))
        print(member_stripped.id)
        print(new_whois)
        
        with open(shameless_json, 'r') as f:
                data = json.load(f)
        
        for p_name, p_info in data.items():
            print(p_name)
            if p_name != "misc" and p_info["discord.id"] == member_stripped.id:
                p_info["whois"] = new_whois
                with open(shameless_json, 'w') as f:
                    json.dump(data, f, indent=4, sort_keys=True)
                return await ctx.send("Whois trigger successfully updated.")
        else:
            return await ctx.send("Having trouble finding that user\'s info. Please check"
                                  " and try again.")
        
        # Notify if person doens't have necessary role
    @setwhois.error
    async def setwhois_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Quit posing, you candy-ass! You don\'t tell me what to do!')
        
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
    
    ### Let me send things to command line
    @commands.command()
    @commands.is_owner()
    async def sendpi(self, ctx, *, print_terminal: str):
        time_sent = dt.now()
        print('{} \n Time sent: {}'.format(print_terminal,time_sent))
        confirm_emoji = '✔️'
        return await ctx.message.add_reaction(confirm_emoji)
    
    ### listen in #attacks_log for bounce message, and update json with info        
    @commands.Cog.listener()
    async def on_message(self, message):
        bouncewords = ["bounce:",")."]
        cutwords = ['cut a bitch','cut you','cut someone']
        
        # captures bounce info
        if (message.channel.name == 'attacks_log' and any(s in message.content
                                                          for s in bouncewords)):
            bounce_msg = message.content
            print(bounce_msg)
            bouncer = [bounce_msg[17:bounce_msg.find(' [')].strip(), 
                       bounce_msg[2:bounce_msg.find(' [')].strip()]
            bouncetime = dt.utcnow().strftime("%c")
            print(bouncetime)
            print(bouncer)
            with open(shameless_json, 'r') as f:
                data = json.load(f)
            for p_name, p_info in data.items():
                if p_name in bouncer:
                    p_info['bounces'] += 1
                    p_info['last_bounce'] = bouncetime
            with open(shameless_json, 'w') as f:
                json.dump(data, f, indent=4, sort_keys=True)
        
        elif (message.channel.id == 435902101810577458 and '__greater protection__ expired' in message.content):
            list_of_stuff = []
            list_of_stuff = message.content.split('\n')
            for x in list_of_stuff:
                if '__greater protection__ expired' in x:
                    gp_needer = re.search('\[(.+?)\]', x).group(1)

                    if gp_needer not in gp_supporters:
                        await message.channel.send('.requestfor {} gp note: added by Rockbot'.format(gp_needer))
                    print(gp_needer)
            print(list_of_stuff)
        #troll Kalrenz and his fat self
        elif message.author.id == 88125388051447808 and 'ranch' in message.content.lower():
            ranch_gifs = ['https://media.giphy.com/media/3oGRFnbLY1U9S5ZITm/giphy.gif',
                         'https://media.giphy.com/media/l3c5Kcw7NypsdWTPa/giphy.gif',
                         'https://media.giphy.com/media/lU5FniZJ03PMc/giphy.gif',
                         'https://media.giphy.com/media/26uf4ztgExZ3VEzUQ/giphy.gif',
                         'https://media.giphy.com/media/xT5LMq7AadOYYpEYdq/giphy.gif']
            ranchitem = random.choice(ranch_gifs)
            await message.channel.send('Here you go, fat-ass: {}'.format(ranchitem))
        
        # Cleans up utopiabot spam from bad .list messages
        elif 'not an option, try one of these' in message.content:
            await message.delete(delay=3)
            
        elif 'Sent PM to you, <@!460400451645472782>' in message.content:
            await message.delete(delay=0)
            
        # Cleans up stupid utopiabot's worthless dice rolls
        elif 'You rolled the dice and you got' in message.content:
            await message.delete(delay=0)
        
        #Uses the .whois function in utopiabot to load a fun trigger for searched user
        elif 'phone:' in message.content:
            start = 'prov: '
            end = ' | links:'
   
            prov_to_search = (message.content.split(start))[1].split(end)[0]
            
            with open(shameless_json, 'r') as f:
                data = json.load(f)
        
            for p_name, p_info in data.items():
                if p_name != "misc" and p_name == prov_to_search:
                    await message.channel.send('{}'.format(p_info["whois"]))
                    
                    
        elif any(s in message.content.lower() for s in cutwords):
            await message.channel.send('https://giphy.com/gifs/imRiPoKJB9R9m')
                
    @commands.command(pass_context=True)
    async def bounces(self, ctx):
        with open("/home/pi/cretobot/shameless77.json", "r") as f:
            data = json.load(f)
        not_here = 1     
        for p_name, p_info in data.items():
            if p_name != "misc" and p_info["discord.id"] == ctx.author.id:
                not_here = 0
                return await ctx.send('You have bounced {} times this age, and your last '
                                      'bounce was {}.\n'
                                      'Way to go, dumbass!'.format(p_info["bounces"],
                                                                   p_info["last_bounce"]))
            
        if not_here == 1:
            await ctx.send('Your Discord user is not currently linked to any '
                           'province for Rockbot commands. Please do `!provset '
                           '[Province Name]` to link, then try this command again.')
            
    @commands.command(pass_context=True)
    async def shamelist(self, ctx):
        with open(shameless_json, 'r') as f:
            data = json.load(f)
        
        losers = {p_info['discord.id']: p_info['bounces'] for p_name, p_info in data.items()
                 if p_name != 'misc' and p_info['bounces'] > 0}
        sortedlosers = sorted(losers.items(), key=lambda x: x[1], reverse=True)
        embedlosers = '\n'.join('<@{}> | Bounces: {}'.format(loser_id, loser_bounces)
                          for loser_id, loser_bounces in sortedlosers)
        embed = discord.Embed(title='The Shameless Shame-List', color=0xb20000)
        embed.set_author(name='Age 84')
        embed.add_field(name='Best of the worst:', value=embedlosers)
        await ctx.send(embed=embed)
        
    @commands.command(name='react')
    async def react_log(self, ctx, msg_id: int):
        _message = await ctx.get_message(msg_id)
        results = {react.emoji: react.count for react in _message.reactions}
        print('\n'.join('{}|{}'.format(x,y) for x,y in results.items()))
#         await ctx.send(results)
        await ctx.send('\n'.join('{} | {}'.format(candidate, count) for candidate,
                                 count in results.items()))    
    
    @commands.command()
    async def parrot(self, ctx, *, memeify:str=None):
        img = Image.open('images/parrot.jpg')
 
        fnt = ImageFont.truetype('Impact.ttf', 50)
        d = ImageDraw.Draw(img)
        d.text((50,50), 'SQUAWK!!! ' + memeify.upper(), font=fnt, fill=(0, 191, 255))

        img.save('images/parrot_text.jpg')
        await ctx.send(file=discord.File('images/parrot_text.jpg'))
    
    @commands.command()
    @commands.is_owner()
    async def pass_file(self, ctx, filepath):
        print('/home/pi/cretobot/'+filepath)
        await ctx.send(file=discord.File('/home/pi/cretobot/'+filepath))
        
    @commands.command()
    async def jack(self, ctx, *, memeify:str=None):
        img = Image.open('images/jack.gif')
 
        fnt = ImageFont.truetype('Arial_Bold_Italic.ttf', 20)
        d = ImageDraw.Draw(img)
        d.text((50,50), memeify, font=fnt, fill=(255, 255, 0))

        img.save('images/jack_text.gif')
        await ctx.send(file=discord.File('images/jack_text.gif'))
        
    @commands.command(aliases=["bk"], pass_context=True)
    async def bounceking(self, ctx):
        with open(shameless_json, 'r') as f:
            data = json.load(f)
            
        bounce_list = {p_info['discord.id']: p_info['bounces'] for p_name, p_info in data.items()
                       if p_name != 'misc'}
        sorted_bouncers = sorted(bounce_list.items(), key=lambda x: x[1], reverse=True)
        bounceking = self.bot.get_user(sorted_bouncers[0][0])
        print(bounceking)
        embed = discord.Embed(title='The Shameless Bounce King', color=0xffd700)
        embed.set_thumbnail(url=
                            'https://cdn.discordapp.com/attachments/404868940683149332/497485025743470602/BOUNCE-KING.png')
        embed.add_field(name='\u200b', value='<@{}> | Bounces: {}'.format(
                        sorted_bouncers[0][0], sorted_bouncers[0][1]))
        await ctx.send(content='All hail the Bounce King!', embed=embed)
        
    @commands.command(aliases=["converttemp", "temp", "convert"])
    async def tempconvert(self, ctx, temp:int, system):
        if system.lower() == "f":
            converted_temp = int((temp - 32) * 5 / 9)
            return await ctx.send("{}\u00b0F is equal to {}\u00b0C".format(temp,converted_temp))
        elif system.lower() == "c":
            converted_temp = int((temp * 9 / 5) + 32)
            return await ctx.send("{}\u00b0C is equal to {}\u00b0:flag_us:".format(temp,converted_temp))
        else:
            return await ctx.send("Please use the format: ```!tempconvert [temperature] [C/F]```")
    
    @commands.command()
    async def gold(self, ctx):
        role_info = discord.utils.get(ctx.guild.roles, id=715567892644626483)
        embed1 = '\n'.join(('{}'.format(x.display_name)) for x in role_info.members)
        embed = discord.Embed(title='Members With Gold Status', color=0xd4af37)
        embed.add_field(name='\u200b', value = embed1)
        await ctx.send(content='Here you go jabroni:', embed=embed)
    
    @commands.command()
    async def hasrole(self, ctx, passed_role):
        passed_role_id = int(passed_role.strip('<@&>'))
        print(passed_role_id)
        role_info = discord.utils.get(ctx.guild.roles, id=passed_role_id)
        role_color_stripped = role_info.color
        role_color_stripped = role_color_stripped.strip('#')
        role_color = '0x'.join(role_color_stripped)
        print(role_color)
        embed1 = '\n'.join(('{}'.format(x.display_name)) for x in role_info.members)
        embed = discord.Embed(title='Members with {} role:', color=role_color)
        embed.add_field(name='\u200b', value=embed1)
        await ctx.send(content='Here you go jabroni:', embed=embed)
        print(role_info.name)
        print(role_color)
                           
   
        
def setup(bot):
    bot.add_cog(Meta(bot))
