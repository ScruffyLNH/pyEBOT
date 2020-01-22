import discord # noqa
import sheets
from discord.ext import commands


class DevTools(commands.Cog):

    def __init__(self, client):
        self.client = client

    """
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready.')
    """

    # Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command()
    async def getUserId(self, ctx):
        await ctx.send(f'Your user ID is: {ctx.author.id}')

    @commands.command()
    async def getChannelId(self, ctx):
        await ctx.send(f'This channels ID is: {ctx.channel.id}')

    @commands.command()
    async def clear(self, ctx, amount=1):
        await ctx.channel.purge(limit=amount + 1)

# Temporary test code.
    @commands.command()
    async def printSheetRow(self, ctx):
        rowNum = 3
        data = sheets.getRow(rowNum)
        await ctx.send(
            f'The values in row {rowNum} are {data}')


def setup(client):
    client.add_cog(DevTools(client))
