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

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        messageId = message.id
        print(f'Message ID is: {messageId}')

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
        await ctx.channel.purge(limit=(amount + 1))

    @commands.command()
    async def editMessage(self, ctx, messageId, *, newContent):
        msg = await ctx.channel.fetch_message(messageId)
        await msg.edit(content=newContent)


def setup(client):
    client.add_cog(DevTools(client))
