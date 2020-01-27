import discord # noqa
import os
from discord.ext import commands

client = commands.Bot('!')
client.remove_command('help')


# Check functions
def isAdmin(ctx):
    return ctx.author.id == 312381318891700224

# Events
@client.event
async def on_ready():
    print('Ready.')

# Commands
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    client.reload_extension(f'cogs.{extension}')


@client.command()
@commands.check(isAdmin)
async def checkTest(ctx):
    await ctx.send('Yes, you are admin')


for filename in os.listdir('./cogs'):
    if not filename == 'devTools.py':
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')


client.run('NjY1ODQ2MTI2NzMzNDI2NzA5.Xhrj1Q.dWY00Kdjl8jTsVx4K099PCc-4QY')
