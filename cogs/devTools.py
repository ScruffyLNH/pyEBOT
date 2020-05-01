import discord # noqa
from utility import sendMessagePackets
from constants import Constants
from discord.ext import commands


class DevTools(commands.Cog):

    def __init__(self, client):
        self.client = client

    """
    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        messageId = message.id
        print(f'Message ID is: {messageId}')
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
    async def getGuildId(self, ctx):
        await ctx.send(f'This guilds ID is: {ctx.guild.id}')

    @commands.command()
    async def getChannels(self, ctx):
        channels = ''
        guild = self.client.get_guild(Constants.GUILD_ID)
        for i, channel in enumerate(guild.channels):
            channels += f'\n {channel.name}'
            channels += f'\n\tid: {channel.id},\n\ttype: {channel.type},'
            channels += f'\n\tposition: {channel.position}\n'

        await sendMessagePackets(ctx, channels)

    @commands.command()
    async def getRoles(self, ctx):
        serverRoles = ctx.guild.roles
        roles = ''
        for role in serverRoles:
            roles += f'\n {role.name}'
            roles += f'\n\tid: {role.id},\n\tPosition: {role.position}\n'
        roles = roles.translate(str.maketrans('', '', '@'))

        await sendMessagePackets(ctx, roles)

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
    async def clearEvents(self, ctx):

        await ctx.send('Now clearing all events', delete_after=3.0)

        guild = self.client.get_guild(Constants.GUILD_ID)
        signupChannel = ctx.channel
        categoryChannels = []

        # Delete all roles and channels.
        for orgEvent in self.client.orgEvents.events:
            for role in orgEvent.roles.values():
                dRole = guild.get_role(role.id)
                await dRole.delete()
            for channel in orgEvent.channels.values():
                dChannel = guild.get_channel(channel.id)
                # Wait to delete category channels until all channels within
                # the category channels are gone.
                if dChannel.type is not discord.ChannelType.category:
                    await dChannel.delete()
                else:
                    categoryChannels.append(dChannel)
        # Delete category channels now that they are cleared.
        for dChannel in categoryChannels:
            await dChannel.delete()

        # Delete all embed messages.
        for orgEvent in self.client.orgEvents.events:
            msg = await signupChannel.fetch_message(orgEvent.id)
            await msg.delete()

        await ctx.message.delete()

        await ctx.send(
            'Channels and roles associated with events cleared.',
            delete_after=3.0)

    @commands.command()
    async def editMessage(self, ctx, messageId, *, newContent):
        msg = await ctx.channel.fetch_message(messageId)
        await msg.edit(content=newContent)

    # Command check for entire cog.
    def cog_check(self, ctx):
        return ctx.author.id == self.client.config.adminId


def setup(client):
    client.add_cog(DevTools(client))
