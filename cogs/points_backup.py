import discord
import asyncio
import json
import logging
import aiohttp

from datetime import datetime as dt
from discord.ext import commands

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(filename='/home/pi/cretobot/discord_points.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

shameless_json = '/home/pi/cretobot/shameless77.json'
points_json = '/home/pi/cretobot/points.json'

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(hidden=True)
    async def sroles(self, ctx):
        print(ctx.guild.roles)
        await ctx.send('\n'.join('Name: {} | ID: {}'.format(role.name, role.id) for
                                role in ctx.guild.roles))

    @commands.command(name='scoreboard')
    async def _showpoints(self, ctx):
#         data = open_json(points_json)
        with open(points_json, 'r') as f:
            data = json.load(f)
        team1 = data['Team 1']
        team2 = data['Team 2']
        team3 = data['Team 3']
        embed = discord.Embed(title=':cocktail:Shameless Speakeasy Scoreboard:cocktail:', 
                          color=0x52a363)
        embed.add_field(name='\u200b', value='<@&{}>\nTasty Libations: {:,}\nLeader: '
                    '<@{}>'.format(team1['id'],team1['points'],team1['leader.id']), inline=True)
        embed.add_field(name='\u200b', value='<@&{}>\nTasty Libations: {:,}\nLeader: '
                    '<@{}>'.format(team2['id'],team2['points'],team2['leader.id']), inline=True)
        embed.add_field(name='\u200b', value='<@&{}>\nTasty Libations: {:,}\nLeader: '
                    '<@{}>'.format(team3['id'],team3['points'],team3['leader.id']), inline=True)
        await ctx.send(embed=embed)
        
    @commands.command(name='mypoints')
    @commands.has_any_role('Artisanal Beverage Purveyors', 'Cocktail Captains', 'The Samanthas')
    async def teampoints(self, ctx):
        with open(points_json, 'r') as f:
            data = json.load(f)
        team1 = data['Team 1']
        team2 = data['Team 2']
        team3 = data['Team 3']
   
        ###Check user's roles to get correct Team
        if team1['id'] in [x.id for x in ctx.author.roles]:
            await ctx.send('<:bartender:655815698953797662>Artisanal Beverage Purveyors<:bartender:655815698953797662>'
                           'currently has {} :cocktail:.'.format(
                            team1['points']))
        elif team3['id'] in [x.id for x in ctx.author.roles]:
            await ctx.send('<:captain:655810928503423008>Cocktail Captains<:captain:655810928503423008> currently has {} '
                           ':cocktail:.'.format(
                            team2['points']))
        elif team2['id'] in [x.id for x in ctx.author.roles]:
            await ctx.send(':lips:The Samanthas:lips: currently '
                           'have {} :cocktail:.'.format(
                            team3['points']))
            
    # Notify if person isn't on one of the teams
    @teampoints.error
    async def teampoints_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You aren\'t on a team! Ask a leader to add you.')

    @commands.command(name='teams', aliases=['listteams', 'teamlist'])
    async def _teams(self, ctx):
        team1 = discord.utils.get(ctx.guild.roles, id=492057877343895554)
        team3 = discord.utils.get(ctx.guild.roles, id=492058028577652746)
        team2 = discord.utils.get(ctx.guild.roles, id=492058064497803274)
        embed1 = '\n'.join('{}'.format(x.display_name) for x in team1.members)
        embed2 = '\n'.join('{}'.format(x.display_name) for x in team2.members)
        embed3 = '\n'.join('{}'.format(x.display_name) for x in team3.members)
        embed = discord.Embed(title='Age 84 Teams', color=0x52a363)
        embed.add_field(name='<:bartender:655815698953797662>Artisanal Beverage Purveyors<:bartender:655815698953797662>', value=embed1, inline=True)
        embed.add_field(name=':lips:The Samanthas:lips:', value=embed3, inline=True)
        embed.add_field(name='<:captain:655810928503423008>Cocktail Captains<:captain:655810928503423008>', value=embed2, inline=True)
        await ctx.send(embed=embed)
                   
       

    # Leaders can give or take points to a team
    @commands.command(name='points', aliases=['cocktails', 'drinks', 'shots', ':cocktail:'])
    @commands.has_role('leaders')
    async def _points(self, ctx, pointee, amt: int, *, p_reason: str=None):
        if p_reason == None:
            p_reason = 'None given, maybe {} just felt like it.'.format(
                       ctx.author.display_name)
        pointee = pointee.replace('!','')
        member = ctx.guild.get_member(int(pointee.strip('<@>')))
        
        with open(points_json, 'r') as f:
            data = json.load(f)
        team1 = data['Team 1']
        team2 = data['Team 2']
        team3 = data['Team 3']
        
        ### Don't allow more than 250 points
        if amt > 250:
            return await ctx.send('Cut that shit out, {}, you can\'t give out'
                                  ' that many :cocktail:s at once.'.format(
                                      ctx.author.display_name))
        elif amt < -250:
            return await ctx.send('Cut that shit out, {}, you can\'t take away'
                                  ' that many :cocktail: at once.'.format(
                                      ctx.author.display_name))
        ### Don't allow leader to grant himself points
        if ctx.author == member:
            return await ctx.send('Don\'t be an ass, {}, you can\'t give yourself'
                                  ' :cocktail:!'.format(ctx.author.display_name))
    ### Send embed containing points transaction to #points-tracker
        points_channel = self.bot.get_channel(499226632704229376)
        embed = discord.Embed(title=':cocktail: Shameless Tasty Libations Update',
                              color=0x52a363)
        ###Check user's roles to get correct Team
        if team1['id'] in [x.id for x in member.roles]:
            team1['points'] += amt
            team_emoji = self.bot.get_emoji(655815698953797662)
            embed.add_field(name='Recipient:', value = '{} | Artisanal Beverage Purveyors'. format(
                        member.display_name), inline=True)
        elif team3['id'] in [x.id for x in member.roles]:
            team3['points'] += amt
            team_emoji = self.bot.get_emoji(655810928503423008)
            embed.add_field(name='Recipient:', value = '{} | Cocktail Captains'. format(
                        member.display_name), inline=True)
        elif team2['id'] in [x.id for x in member.roles]:
            team2['points'] += amt
#             team_emoji = self.bot.get_emoji(628417196514869258)
            team_emoji = '💋'
            embed.add_field(name='Recipient:', value = '{} | The Samanthas'. format(
                        member.display_name), inline=True)
        else:
            return await ctx.send('{} doesn\'t appear to be on any team, please '
                           'check.'.format(member.display_name))
        ### Update points JSON
        with open(points_json, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
            
        if amt > 0:
            embed.add_field(name=':cocktail: granted:', value = amt, inline=True)
        elif amt < 0:
            embed.add_field(name=':cocktail: removed:', value = amt, inline=True)
        embed.add_field(name='By leader:', value = '{}'.format(
                        ctx.author.display_name), inline=True)
        embed.add_field(name='Reason:', value = p_reason)   
        await points_channel.send(embed=embed)
#         confirm_emoji = self.bot.get_emoji(628403619686907904)
        confirm_emoji = '🍸'
        await ctx.message.add_reaction(team_emoji)
        return await ctx.message.add_reaction(confirm_emoji)
       
        
    # Notify if person doens't have necessary role
    @_points.error
    async def _points_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Go sit your candy-ass down! You\'re no leader...')
            
    @commands.command(name='points_reset', hidden=True)
    @commands.is_owner()
    async def _reset(self, ctx, team: int, new_amt: int):
        with open(points_json, 'r') as f:
            data = json.load(f)
        team1 = data['Team 1']
        team2 = data['Team 2']
        team3 = data['Team 3']
        
        if team == 1:
            team1['points'] = new_amt
            await ctx.send('Points successfully updated.')
        elif team == 2:
            team2['points'] = new_amt
            await ctx.send('Points successfully updated.')
        elif team == 3:
            team3['points'] = new_amt
            await ctx.send('Points successfully updated.')
            
        ### Update points JSON
        with open(points_json, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
            
        
        
def setup(bot):
    bot.add_cog(Points(bot))
        

