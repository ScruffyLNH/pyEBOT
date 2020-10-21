import discord # noqa
from utility import sendMessagePackets, saveData
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
        """Verify bot is online. Bot should respond with "Pong!"
        """
        await ctx.send('Pong!')

    @commands.command()
    async def getUserId(self, ctx):
        """Get the discord id for the author of the command message.
        """
        await ctx.send(f'Your user ID is: {ctx.author.id}')

    @commands.command()
    async def getChannelId(self, ctx):
        """Get the channel id of the channel where command was invoked.
        """
        await ctx.send(f'This channels ID is: {ctx.channel.id}')

    @commands.command()
    async def getGuildId(self, ctx):
        """Get the guild id of the guild where command was invoked.
        """
        await ctx.send(f'This guilds ID is: {ctx.guild.id}')

    @commands.command()
    async def getChannels(self, ctx):
        """Get information on all channels in guild.
        """
        if self.client.config.guildId is None:
            await ctx.send(
                'Please configure the guildId before using this command'
            )
            return

        channels = ''
        guild = self.client.get_guild(self.client.config.guildId)
        for i, channel in enumerate(guild.channels):
            channels += f'\n {channel.name}'
            channels += f'\n\tid: {channel.id},\n\ttype: {channel.type},'
            channels += f'\n\tposition: {channel.position}\n'

        await sendMessagePackets(ctx, channels)

    @commands.command()
    async def getUsers(self, ctx):
        """Get information about guild members.
        """

        members = ''
        for i, member in enumerate(ctx.guild.members):
            members += f'\n {member.name}'
            members += f'\n\tnick: {member.nick},'
            members += f'\n\tdisplay name: {member.display_name},'
            members += f'\n\tid: {member.id}\n'

        await sendMessagePackets(ctx, members)

    @commands.command()
    async def getRoles(self, ctx):
        """Get information on all roles in guild.
        """
        serverRoles = ctx.guild.roles
        roles = ''
        for role in serverRoles:
            roles += f'\n {role.name}'
            roles += f'\n\tid: {role.id},\n\tPosition: {role.position}\n'
        roles = roles.translate(str.maketrans('', '', '@'))

        await sendMessagePackets(ctx, roles)

    @commands.command()
    async def getGuilds(self, ctx):
        """See all guilds connected to bot.
        """
        guilds = ''
        for guild in self.client.guilds:
            guilds += f'\n {guild.name}, id: {guild.id}'
        await ctx.send(f'Connected guilds: {guilds}')

    @commands.command()
    async def clear(self, ctx, amount=1):
        """Clear message(s) in a channel.

        :param amount: Amount of messages to delete, defaults to 1
        :type amount: int, optional
        """
        await ctx.channel.purge(limit=(amount + 1))

    @commands.command()
    async def clearEvents(self, ctx):
        """Clear all active events from discord.
        """

        if self.client.config.guildId is None:
            await ctx.send(
                'Please configure the guildId before using this command'
            )
            return

        await ctx.send('Now clearing all events', delete_after=3.0)

        cog = self.client.get_cog('Updater')

        # Delete all roles and channels.
        for orgEvent in self.client.orgEvents.events:
            # Clear discord roles, channels and event embed.
            await cog.clearEvent(orgEvent)

            # Clear internal event record.
            await cog.clearEventData(orgEvent)

        await ctx.send(
            'Channels and roles associated with events cleared.',
            delete_after=3.0)

    @commands.command()
    async def editMessage(self, ctx, messageId, *, newContent):
        """Edit a message already posted by bot

        :param messageId: The id of the message to be edited.
        :type messageId: Str
        :param newContent: New content of the message.
        :type newContent: Str
        """
        msg = await ctx.channel.fetch_message(messageId)
        await msg.edit(content=newContent)

    @commands.command()
    async def removeReaction(self, ctx, memberId, messageId, reaction):

        memberId = int(memberId)
        messageId = int(messageId)

        guild = self.client.get_guild(self.client.config.guildId)
        member = guild.get_member(memberId)
        channel = guild.get_channel(self.client.config.signupChannelId)
        msg = await channel.fetch_message(messageId)
        await msg.remove_reaction(reaction, member)

    @commands.command()
    async def addReaction(self, ctx, messageId, reaction):

        messageId = int(messageId)

        guild = self.client.get_guild(self.client.config.guildId)
        channel = guild.get_channel(self.client.config.signupChannelId)
        msg = await channel.fetch_message(messageId)
        await msg.add_reaction(reaction)

    @commands.command()
    async def forceNewMessage(self, ctx, oldId):
        # TODO: REFACTOR THIS HOTFIX

        # Convert input to int
        oldId = int(oldId)

        for orgEvent in self.client.orgEvents.events:
            if orgEvent.id == oldId:
                myEvent = orgEvent
                break
        else:
            return

        guild = self.client.get_guild(self.client.config.guildId)

        channel = guild.get_channel(self.client.config.signupChannelId)

        # Delete old message if exists.
        try:
            oldMsg = await channel.fetch_message(oldId)
            await oldMsg.delete()
        except discord.NotFound:
            pass

        user = self.client.get_user(myEvent.organizer.id)

        vc = guild.get_channel(self.client.config.defaultVoiceChannelId)

        embed = myEvent.makeEmbed(True, user, mainVoiceName=vc.name)

        # Post the new embed.
        msg = await channel.send(embed=embed)
        # Register the new event id.
        myEvent.id = msg.id
        # Add reactions to the message. #TODO refactor wet code (make a method for adding the reactions in evntCog)
        await msg.add_reaction(Constants.REACTION_EMOJIS['participate'])
        await msg.add_reaction(Constants.REACTION_EMOJIS['cancel'])
        if True in orgEvent.privateIndication.values():
            await msg.add_reaction(Constants.REACTION_EMOJIS['info'])
        await msg.add_reaction(Constants.REACTION_EMOJIS['help'])

        eventData = self.client.orgEvents.json(indent=2)
        saveData(Constants.EVENT_DATA_FILENAME, eventData)

    # Command check for entire cog.
    def cog_check(self, ctx):
        """Check that the user of commands in this cog is the admin.

        :return: True if user is admin, else False
        :rtype: bool
        """
        return ctx.author.id == self.client.config.adminId


def setup(client):
    client.add_cog(DevTools(client))
