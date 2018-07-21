import discord
import config

bot = discord.Client()

@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return
    
    print(message.author, message.content)

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.nick}'.format(message)
        await bot.send_message(message.channel, msg)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(config.token)
