import discord
from discord.ext import commands

client = commands.Bot('!')


@client.event
async def on_ready():
    print('Ready.')


@client.command()
async def ping(ctx):
    await ctx.send('Pong!')

client.run('NjY1ODQ2MTI2NzMzNDI2NzA5.Xhrj1Q.dWY00Kdjl8jTsVx4K099PCc-4QY')
