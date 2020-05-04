import discord # noqa
from utility import saveData, checkConfig, getConfigIds
from constants import Constants
from discord.ext import commands
# TODO: This whole cog should really be rewritten.
# TODO: Check that guildId has been set before commands are available.


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

    # Validation checks.
    async def guildIsSet(self, ctx):
        if type(self.client.config.guildId) == int:
            return True
        else:
            await ctx.send(
                'Guild ID must be set before creating or setting any channels '
                'or roles.'
            )
            return False

    async def categoryChannelExists(self, ctx, channelAttribute):
        if (
            self.client.config.mainCategoryChannelId is None and
            'Category' not in channelAttribute
        ):
            await ctx.send(
                'Please set or create the main category channel before '
                'setting any other channels.'
            )
            return False
        else:
            return True

    async def attributeFound(self, ctx, attribute):
        try:
            getattr(self.client.config, attribute)
        except AttributeError:
            await ctx.send(
                'Could not find the config attribute, make sure the first '
                'argument is correct.'
            )
            return False
        return True

    async def attrTypeCorrect(self, ctx, attribute, attrType):
        if attrType in attribute:
            return True
        else:
            await ctx.send(
                f'Attribute type is not correct for this command.\n'
                f'Please make sure you are setting a {attrType}'
            )
            return False

    async def channelExists(self, ctx, channelRef, expectedResult=False):
        guild = self.client.get_guild(self.client.config.guildId)

        (channelRef, isInt) = self.tryParseInt(channelRef)

        if isInt:
            channel = self.verifyChannelId(guild, channelRef)
        else:
            channel = self.verifyChannelName(guild, channelRef)

        if expectedResult:
            if not channel:
                await ctx.send('Channel not fond.')
        else:
            if channel:
                await ctx.send('Channel already exists.')

        return True if channel else False

    async def roleExists(self, ctx, roleRef, expectedResult=False):
        guild = self.client.get_guild(self.client.config.guildId)

        (roleRef, isInt) = self.tryParseInt(roleRef)

        if isInt:
            role = self.verifyRoleId(guild, roleRef)
        else:
            role = self.verifyRoleName(guild, roleRef)
        if expectedResult:
            if not role:
                await ctx.send('Role not found.')
        else:
            if role:
                await ctx.send('Role already exists.')

        return True if role else False

    async def serializeConfig(self, ctx, attribute, id):
        setattr(self.client.config, attribute, id)
        configData = self.client.config.json(indent=2)
        saveData(Constants.CONFIG_DATA_FILENAME, configData)
        await ctx.send(f'{attribute} successfully set, ID is {id}')

    async def processSetChannelRequest(self, channelRef, catChannel=False):  # TODO: Rename?
        # TODO: Docstring
        guild = self.client.get_guild(self.client.config.guildId)
        (channelRef, isInt) = self.tryParseInt(channelRef)
        channel = None
        if isInt:
            channel = self.verifyChannelId(guild, channelRef)
        else:
            channel = self.verifyChannelName(guild, channelRef)

        # Move channel to correct category if not already there.
        if not catChannel:
            category = guild.get_channel(
                self.client.config.mainCategoryChannelId
            )
            if channel.category is None:  # TODO: Refactor
                await channel.edit(category=category)
            elif category.id != channel.category.id:
                await channel.edit(category=category)

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
        return role.id

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
        """Sets the ID of the current guild as the event bot guild ID.
        """
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
        """Command group for configuring channels. Use help command for sub commands.
        """
        await ctx.send(
            'This is a command group. Use help function for subcommands\n'
            f'{Constants.CMD_PREFIX}help configureChannels'
        )

    @configChn.command(name='setChannel')
    async def setChannel(self, ctx, channelAttribute, discordChannel):
        """Link existing discord channels to config channels.

        :param channelAttribute: The Config attribute. Use checkConfiguration
        command to see attributes yet to be configured.
        :type channelAttribute: string
        :param discordChannel: Name/id of discord channel to be set in config.
        :type discordChannel: string
        """
        # Do verification checks
        if not await self.guildIsSet(ctx):
            return

        if not await self.categoryChannelExists(ctx, channelAttribute):
            return

        if not await self.channelExists(
            ctx, discordChannel, expectedResult=True
        ):
            return

        if not await self.attributeFound(ctx, channelAttribute):
            return

        if not await self.attrTypeCorrect(ctx, channelAttribute, 'Channel'):
            return

        # Get id of the discord channel if it exists.
        channelId = await self.processSetChannelRequest(discordChannel, True)

        if channelId is None:
            await ctx.send('Could not find the requested channel.')
        else:
            await self.serializeConfig(ctx, channelAttribute, channelId)

    @configChn.command(name='createChannel')
    async def createChannel(self, ctx, channelAttribute, discordChannel):
        """Create discord channel and link to config.

        :param channelAttribute: The config attribute use checkConfiguration
        command to see attributes yet to be configured.
        :type channelAttribute: string
        :param discordChannel: Name of the discord channel
        :type discordChannel: string
        """

        # Do verification checks
        if not await self.guildIsSet(ctx):
            return

        if not await self.categoryChannelExists(ctx, channelAttribute):
            return

        if await self.channelExists(ctx, discordChannel):
            return

        if not await self.attributeFound(ctx, channelAttribute):
            return

        if not await self.attrTypeCorrect(ctx, channelAttribute, 'Channel'):
            return

        # Determine the channel type.
        if 'Voice' in channelAttribute:
            channelType = 'voice'
        elif 'Category' in channelAttribute:
            channelType = 'category'
        else:
            channelType = 'text'

        channelId = await self.processCreateChannelRequest(
            discordChannel,
            channelType=channelType
        )

        await self.serializeConfig(ctx, channelAttribute, channelId)

    @commands.group(name='configureRoles', invoke_without_command=True)  # TODO: Check that guildId has been set.
    async def configRole(self, ctx):
        """Command group for configuring roles. Use help command for sub commands.
        """
        await ctx.send(
            'This is a command group. Use help function for subcommands\n'
            f'{Constants.CMD_PREFIX}help configureRoles'
        )

    @configRole.command(name='setRole')
    async def setRole(self, ctx, roleAttribute, discordRole):

        # Do verification checks.
        if not await self.guildIsSet(ctx):
            return
        if not await self.roleExists(ctx, discordRole, expectedResult=True):
            return
        if not await self.attributeFound(ctx, roleAttribute):
            return
        if not await self.attrTypeCorrect(ctx, roleAttribute, 'Role'):
            return

        roleId = self.processSetRoleRequest(discordRole)
        await self.serializeConfig(ctx, roleAttribute, roleId)

    @configRole.command(name='createRole')
    async def createRole(self, ctx, roleAttribute, discordRole):

        # Do verification checks.
        if not await self.guildIsSet(ctx):
            return
        if await self.roleExists(self, ctx, discordRole):
            return
        if await self.attributeFound(ctx, roleAttribute):
            return
        if not await self.attrTypeCorrect(ctx, roleAttribute, 'Role'):
            return

        roleId = self.processCreateRoleRequest(discordRole)

        await self.serializeConfig(ctx, roleAttribute, roleId)

    @commands.command(name='checkConfiguration', aliases=['checkConfig'])
    async def checkConfiguration(self, ctx):
        """Check which configuration fields needs to be configured.
        """
        remainingFields = '\n'.join(checkConfig(self.client.config))
        completedFields = '\n'.join(getConfigIds(self.client.config))

        # Build the message with a buffer
        buffer = []

        if remainingFields:
            buffer.append(
                'Remaining fields to be configured are as follows:\n'
            )
            buffer.append(remainingFields)
            buffer.append('\n\n')
        else:
            buffer.append('Configuration is complete\n\n')

        if completedFields:
            buffer.append(
                'The following fields have been configured:\n'
            )
            buffer.append(completedFields)

        await ctx.send(''.join(buffer))

    # Command check for entire cog.
    def cog_check(self, ctx):
        return ctx.author.id == self.client.config.adminId


def setup(client):
    client.add_cog(serverConfig(client))
