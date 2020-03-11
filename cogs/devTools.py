import discord # noqa
from constants import Constants
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
    async def getGuildId(self, ctx):
        await ctx.send(f'Your guilds ID is: {ctx.guild.id}')

    @commands.command()
    async def getChannels(self, ctx):
        channels = ''
        guild = self.client.get_guild(Constants.GUILD_ID)
        for channel in guild.channels:
            channels += f'\n {channel.name}'
            channels += f'\n\tid: {channel.id},\n\ttype: {channel.type}\n'
        await ctx.send(f'Channels in this server:\n{channels}')

    @commands.command()
    async def getRoles(self, ctx):
        serverRoles = ctx.guild.roles
        roles = ''
        for role in serverRoles:
            roles += f'\n {role.name}'
            roles += f'\n\tid: {role.id},\n\tPosition: {role.position}\n'
        roles = roles.translate(str.maketrans('', '', '@'))
        await ctx.send(f'Roles on this server:\n{roles}')


    @commands.command()
    async def getGuilds(self, ctx):
        guilds = ''
        for guild in self.client.guilds:
            guilds += f'\n {guild.name}, id: {guild.id}'
        await ctx.send(f'Connected guilds: {guilds}')

    @commands.command()
    async def clear(self, ctx, amount=1):
        await ctx.channel.purge(limit=(amount + 1))

    @commands.command()
    async def editMessage(self, ctx, messageId, *, newContent):
        msg = await ctx.channel.fetch_message(messageId)
        await msg.edit(content=newContent)


def setup(client):
    client.add_cog(DevTools(client))
