import discord # noqa
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


def setup(client):
    client.add_cog(DevTools(client))
