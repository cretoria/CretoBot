import discord
from discord.ext import commands
import asyncio
import config
import json
from itertools import islice


description = 'This is my bot. I like it -- when it works...'
bot = commands.Bot(command_prefix='!', description=description)

owner = [404071518159634452]

# Command to set our current KD
@bot.command()
@commands.has_any_role('leaders', 'admin')
async def setkd(ctx, our_kd):
    with open ("dragonScript.json", "r+") as f:
        data = json.load(f)
        
    data["our_KD"] = our_kd
    
    with open ("dragonScript.json", "w+") as f:
        json.dump(data, f)
    
    await ctx.send('Our KD set to ({}).'.format(our_kd))

# Notify if person doens't have necessary role
@setkd.error
async def setkd_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('You do not have the necessary permissions for this command.')

# Retrieves our KD location from json
@bot.command()
async def kd(ctx):
    with open ("dragonScript.json", "r+") as jsonFile:
        data = json.load(jsonFile)
        our_kd = data["our_KD"]
    await ctx.send('Our KD is ({}).'.format(our_kd))
    
# List current KD provinces


@bot.command()
async def list_provs(ctx):
    with open ("dragonScript.json", "r") as f:
        data = json.load(f)
        our_kd = data["our_KD"]
    try:
#        with open ("dump.txt", "r") as kd_dump:
#            current_line = 1
#            for line in kd_dump:
#                if line.startswith("count") == True:
#                    print(line)
#                    current_line += 1
#                    if line.find(our_kd) == True:
#                        await ctx.send('Found our KD!')
#                        break
#                current_line += 1        
#    
        with open('dump.txt', 'r+') as f:
                    for linenum, line in enumerate(f):
                        if line.find('"loc": "' + our_kd + '",') != -1:
                            chunk = islice(f, 7)
                            provs = []
                            for line in chunk:
                                if line.lstrip().startswith('"name"') == True:
                                    provs.append(line.lstrip('"name": "').rstrip('",\n'))
                                    pprovs = '\n'.join(provs)
                                    await ctx.send(pprovs)
                                    
        
    except FileNotFoundError:
        await ctx.send('KD dump data not found, please notify @admin.')
        
### parse.py info
#fae_occur = []  #list to store faery occurences
#substr = "faery"   #we want to search for all instances of faery
#try:
#    with open ('dump.txt', 'rt') as in_dump:
#        for linenum, line in enumerate(in_dump):   #keep track of line numbers
#            if line.lower().find(substr) != -1:
#                fae_occur.append((linenum,line.rstrip('\n')))
#                
#        for linenum, line in fae_occur:
#            print("Line ", linenum, ": ", line, sep='')
#except FileNotFoundError:
#    print('Dump file not found.')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(discord.__version__)

bot.run(config.token)    # 
