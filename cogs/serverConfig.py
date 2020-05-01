import discord # noqa
from utility import saveData
from constants import Constants
from discord.ext import commands


class serverConfig(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Functions and coroutines
    def tryParseInt(self, input):
        try:
            r = int(input)
            return r, True
        except ValueError:
            r = input
            return r, False

    def verifyChannelId(self, guild, id):
        # TODO: Docstring
        try:
            channel = guild.get_channel(id)
        except discord.NotFound:
            channel = None
        return channel

    def verifyRoleId(self, guild, id):
        # TODO: Docstring
        try:
            role = guild.get_role(id)
        except discord.NotFound:
            role = None
        return role

    def verifyChannelName(self, guild, name):
        # TODO: Docstring
        for chn in guild.channels:
            if chn.name == name:
                return chn
        return None

    def verifyRoleName(self, guild, name):
        # TODO: Docstring
        for r in guild.roles:
            if r.name == name:
                return r
        return None

    def processSetChannelRequest(self, channelRef):
        # TODO: Docstring
        guild = self.client.get_guild(self.client.config.guildId)
        (channelRef, isInt) = self.tryParseInt(channelRef)
        channel = None
        if isInt:
            channel = self.verifyChannelId(guild, channelRef)
        else:
            channel = self.verifyChannelName(guild, channelRef)
        return channel.id

    async def processCreateChannelRequest(
        self, channelName, channelType='text'
    ):
        # TODO: Docstring
        # Channel types text voice category
        guild = self.client.get_guild(self.client.config.guildId)
        channel = self.verifyChannelName(guild, channelName)
        if channel is None:
            if channelType == 'category':
                chnl = await guild.create_category_channel(channelName)
                return chnl.id

            # Get the category channel and make new channel within.
            categoryId = self.client.config.mainCategoryChannelId
            categoryChannel = guild.get_channel(categoryId)
            if channelType == 'text':
                chnl = await categoryChannel.create_text_channel(channelName)
                return chnl.id
            if channelType == 'voice':
                chnl = await categoryChannel.create_voice_channel(channelName)
                return chnl.id
        else:
            # Channel already exists or category channel does not exist,
            # return None.
            return None

    def processSetRoleRequest(self, roleRef):
        guild = self.client.get_guild(self.client.config.guildId)
        (roleRef, isInt) = self.tryParseInt(roleRef)
        role = None
        if isInt:
            role = self.verifyRoleId(guild, roleRef)
        else:
            role = self.verifyRoleName(guild, roleRef)
        return role

    async def processCreateRoleRequest(self, roleName):
        guild = self.client.get_guild(self.client.config.guildId)
        role = self.verifyRoleName(guild, roleName)
        if role is None:
            r = await guild.create_role
            return r.id
        return None

    # Commands
    @commands.command(name='setGuildId')
    async def setGuildId(self, ctx):
        # Get the id of the guild from where the command was invoked.
        guildId = ctx.guild.id
        # Set the id in config object
        self.client.config.guildId = guildId
        # Save config to file
        configData = self.client.config.json(indent=2)
        saveData(Constants.CONFIG_DATA_FILENAME, configData)

        await ctx.send(f'Guild ID ({guildId}) has been set.')

    @commands.group(name='configureChannels', invoke_without_command=True)
    async def configChn(self, ctx):
        await ctx.send(
            'The following subcommands are available:\n'
            'setMainCategory (param: channelName or Id) \n'
            'createMainCategory (param: ChannelName)\n'
        )

    @configChn.command(name='setMainCategory')
    async def setMainCategory(self, ctx, channelRef):
        id = self.processSetChannelRequest(channelRef)
        if id is None:
            await ctx.send('Could not find the requested channel.')
        else:
            self.client.config.mainCategoryChannelId = id
            configData = self.client.config.json(indent=2)
            saveData(Constants.CONFIG_DATA_FILENAME, configData)
            await ctx.send(f'Category channel with id {id} set successfully.')

    @configChn.command(name='createMainCategory')
    async def createMainCategory(self, ctx, channelName):
        id = await self.processCreateChannelRequest(
            channelName,
            channelType='category'
        )
        if id is None:
            await ctx.send('Could not create channel. Check if name is taken.')
        else:
            self.client.config.mainCategoryChannelId = id
            configData = self.client.config.json(indent=2)
            saveData(Constants.CONFIG_DATA_FILENAME, configData)
            await ctx.send(f'Channel created successfully. ID is {id}')

    # Command check for entire cog.
    def cog_check(self, ctx):
        return ctx.author.id == self.client.config.adminId


def setup(client):
    client.add_cog(serverConfig(client))
