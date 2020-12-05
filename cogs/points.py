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
        

    @commands.command(name='scoreboard', aliases=['sb','score'])
    async def _showpoints(self, ctx):
        with open(shameless_json, 'r') as f:
            data = json.load(f)
        
        points_list = {p_info['discord.id']: p_info['points'] for p_name, p_info in data.items()
                       if p_name != 'misc'}
        team1_info = data['misc']['Team 1']
        team2_info = data['misc']['Team 2']
        team3_info = data['misc']['Team 3']
        team1 = discord.utils.get(ctx.guild.roles, id=492057877343895554)
#         print('got team1')
        team2 = discord.utils.get(ctx.guild.roles, id=492058028577652746)
#         print(team2.members)
        team3 = discord.utils.get(ctx.guild.roles, id=492058064497803274)
#         print('got team3')
        
        embed1 = '\n'.join(('{} | {}'.format(x.display_name,points_list[x.id])) for x in team1.members)
#         print('embed1 good')
        embed2 = '\n'.join(('{} | {}'.format(x.display_name,points_list[x.id])) for x in team2.members)
#         print('embed2 good')
        embed3 = '\n'.join(('{} | {}'.format(x.display_name,points_list[x.id])) for x in team3.members)
#         print('embed3 good')
        embed = discord.Embed(title='<:therock:466428026880786452>Shameless Points Scoreboard<:therock:466428026880786452>', 
                          color=0xc51104)
        embed.add_field(name='**{}**'.format(team1.name), 
                        value='__Team Total: {}__'
                        '\nTeam Leader: <@{}>'
                        '\n__Individual Amounts:__\n{}'
                        .format(team1_info['points'],team1_info['leader.id'],embed1), inline=True)
        embed.add_field(name='**{}**'.format(team2.name), 
                        value='__Team Total: {}__'
                        '\nTeam Leader: <@{}>'
                        '\n__Individual Amounts:__\n{}'
                        .format(team2_info['points'],team2_info['leader.id'],embed2), inline=True)
        embed.add_field(name='**{}**'.format(team3.name), 
                        value='__Team Total: {}__'
                        '\nTeam Leader: <@{}>'
                        '\n__Individual Amounts:__\n{}'
                        .format(team3_info['points'],team3_info['leader.id'],embed3), inline=True)

        await ctx.send(embed=embed)
        
    @commands.command(name='mypoints')
    @commands.has_any_role(492057877343895554, 492058028577652746, 492058064497803274)
    async def teampoints(self, ctx):
        with open(shameless_json, 'r') as f:
            data = json.load(f)
        team1_info = data['misc']['Team 1']
        team2_info = data['misc']['Team 2']
        team3_info = data['misc']['Team 3']
        team1 = discord.utils.get(ctx.guild.roles, id=492057877343895554)
        team2 = discord.utils.get(ctx.guild.roles, id=492058028577652746)
        team3 = discord.utils.get(ctx.guild.roles, id=492058064497803274)
        
        for p_name, p_info in data.items():
            if p_name != "misc" and p_info["discord.id"] == ctx.author.id:
                yourpoints = p_info['points']
   
        ###Check user's roles to get correct Team
        if team1_info['id'] in [x.id for x in ctx.author.roles]:
            await ctx.send('Your total points earned this age '
                           'is {}.\n{} currently has {} points.'.format(
                               yourpoints,team1.name,team1_info['points']))
        elif team2_info['id'] in [x.id for x in ctx.author.roles]:
            await ctx.send('Your total points earned this age '
                           'is {}.\n{} currently has {} points.'.format(
                           yourpoints,team2.name,team2_info['points']))
        elif team3_info['id'] in [x.id for x in ctx.author.roles]:
            await ctx.send('Your total points earned this age '
                           'is {}.\n{} currently has {} points.'.format(
                           yourpoints,team3.name,team3_info['points']))
            
    # Notify if person isn't on one of the teams
    @teampoints.error
    async def teampoints_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('You aren\'t on a team! Ask a leader to add you.')

    @commands.command(name='teams', aliases=['listteams', 'teamlist'])
    async def _teams(self, ctx):
        team1 = discord.utils.get(ctx.guild.roles, id=492057877343895554)
        team2 = discord.utils.get(ctx.guild.roles, id=492058028577652746)
        team3 = discord.utils.get(ctx.guild.roles, id=492058064497803274)
        embed1 = '\n'.join('{}'.format(x.display_name) for x in team1.members)
        embed2 = '\n'.join('{}'.format(x.display_name) for x in team2.members)
        embed3 = '\n'.join('{}'.format(x.display_name) for x in team3.members)
        embed = discord.Embed(title='Age 89 Teams', color=0x52a363)
        embed.add_field(name='__**{}**__'.format(team1.name), value=embed1, inline=True)
        embed.add_field(name='__**{}**__'.format(team2.name), value=embed2, inline=True)
        embed.add_field(name='__**{}**__'.format(team3.name), value=embed3, inline=True)
        await ctx.send(embed=embed)
        
                   
       

    # Leaders can give or take points to a team
    @commands.command(name='points', aliases=['sus','vote','votes'])
    @commands.has_any_role('leaders','admin')
    async def _points(self, ctx, pointee, amt: int, *, p_reason: str=None):
        if p_reason == None:
            p_reason = 'None given, maybe {} just felt like it.'.format(
                       ctx.author.display_name)
        
        member = ctx.guild.get_member(int(pointee.strip('<@!>')))
     
        
        with open(shameless_json, 'r') as f:
            data = json.load(f)
        team1_info = data['misc']['Team 1']
        team2_info = data['misc']['Team 2']
        team3_info = data['misc']['Team 3']
        team1 = discord.utils.get(ctx.guild.roles, id=492057877343895554)
        team2 = discord.utils.get(ctx.guild.roles, id=492058028577652746)
        team3 = discord.utils.get(ctx.guild.roles, id=492058064497803274)
        
        
        ### Don't allow more than 250 points
        if amt > 250:
            return await ctx.send('Cut that shit out, {}, you can\'t give out'
                                  ' that many points at once.'.format(
                                      ctx.author.display_name))
        elif amt < -250:
            return await ctx.send('Cut that shit out, {}, you can\'t take away'
                                  ' that many points at once.'.format(
                                      ctx.author.display_name))
        ### Don't allow leader to grant himself points
        if ctx.author == member:
            return await ctx.send('Don\'t be an ass, {}, you can\'t give yourself'
                                  ' points!'.format(ctx.author.display_name))
    ### Send embed containing points transaction to #points-tracker
        points_channel = self.bot.get_channel(499226632704229376)
        embed = discord.Embed(title='<:therock:466428026880786452>Shameless Points Update',
                              color=0xc51104)
        
        ### Update individual member points
        for p_name, p_info in data.items():
            if p_name != "misc" and p_info["discord.id"] == member.id:
                p_info['points'] += amt
        
        ###Check user's roles to get correct Team
        if team1_info['id'] in [x.id for x in member.roles]:
            team1_info['points'] += amt
            team_emoji = '👻'
            embed.add_field(name='Recipient:', value = '{} | {}'. format(
                        member.display_name,team1.name), inline=True)
        elif team2_info['id'] in [x.id for x in member.roles]:
            team2_info['points'] += amt
            team_emoji = '🔪'
            embed.add_field(name='Recipient:', value = '{} | {}'. format(
                        member.display_name,team2.name), inline=True)
        elif team3_info['id'] in [x.id for x in member.roles]:
            team3_info['points'] += amt
#             team_emoji = self.bot.get_emoji(628417196514869258)
            team_emoji = '👨‍🔧'
            embed.add_field(name='Recipient:', value = '{} | {}'. format(
                        member.display_name,team3.name), inline=True)
        else:
            return await ctx.send('{} doesn\'t appear to be on any team, please '
                           'check.'.format(member.display_name))
        ### Update points JSON
        with open(shameless_json, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
            
        if amt > 0:
            embed.add_field(name='points granted:', value = amt, inline=True)
        elif amt < 0:
            embed.add_field(name='points removed:', value = amt, inline=True)
        embed.add_field(name='By leader:', value = '{}'.format(
                        ctx.author.display_name), inline=True)
        embed.add_field(name='Reason:', value = p_reason)   
        await points_channel.send(embed=embed)
#         confirm_emoji = self.bot.get_emoji(628403619686907904)
        confirm_emoji = '✔️'
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
        with open(shameless_json, 'r') as f:
            data = json.load(f)
        team1 = data['misc']['Team 1']
        team2 = data['misc']['Team 2']
        team3 = data['misc']['Team 3']
        
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
        with open(shameless_json, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
            
        
        
def setup(bot):
    bot.add_cog(Points(bot))
        

