import discord # noqa
from constants import Constants
import event
import utility
from datetime import datetime
from discord.ext import commands


class EventSignupHandler(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == Constants.MAIN_CHANNEL_ID:
            if payload.emoji.name in Constants.REACTION_EMOJIS.values():
                self.client.loop.create_task(
                    self.handleSignup(payload)
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id == Constants.MAIN_CHANNEL_ID:
            if payload.emoji.name in Constants.REACTION_EMOJIS.values():
                self.client.loop.create_task(
                    self.handleCancellation(payload)
                )

    async def handleSignup(self, payload):  # TODO: generalize method to handle more emojis and roles.

        if payload.emoji.name == Constants.REACTION_EMOJIS['participant']:
            await self.handleParticipationRequest(payload)

        if payload.emoji.name == Constants.REACTION_EMOJIS['spectator']:
            await self.handleSpectatorRequest()  # TODO: Make handleSpectatorRequest method.

        # If private event check if user is member.
        # Instanciate user and add to client.orgEvents.
        # Update embed.
        # Grant user roles if the event has a private channel.
        # Mention user in event channel: "@examplePerson Welcome to the event!"

    async def handleCancellation(self, payload):  # TODO: generalize method to handle more emojis and roles.

        messageId = payload.message_id
        # Check which event was reacted to
        orgEvent = self.getEvent(messageId)
        # Get channel object
        channel = self.client.get_channel(payload.channel_id)
        # Get the Message object.
        message = await channel.fetch_message(messageId)
        # Get the Guild object.
        guild = message.guild
        # Get the user who reacted
        member = guild.get_member(payload.user_id)

        person = orgEvent.getParticipant(member.id)
        if person is not None:
            person.active = False
            if person.roles:
                roleId = orgEvent.roles['participant'].id
                person.removeRole(roleId)

                # Get the discord role.
                participantRole = guild.get_role(roleId)
                await member.remove_roles(participantRole)

        utility.saveData(
            'eventData.json', self.client.orgEvents.json(indent=2)
        )

        # Update embed in discord.
        self.makeUpdate(orgEvent)

    async def handleParticipationRequest(self, payload):
        """
        messageId = payload.message_id
        # Check which event was reacted to
        orgEvent = self.getEvent(messageId)
        # Get the Channel object.
        channel = self.client.get_channel(payload.channel_id)
        # Get the Message object.
        message = await channel.fetch_message(messageId)
        # Get the Guild object.
        guild = message.guild
        # Get the user who reacted
        member = guild.get_member(payload.user_id)
        # Get the role that official members will have.
        memberRole = guild.get_role(Constants.MEMBER_ROLE_ID)
        """

        data = await self.gatherPayloadData(payload)
        orgEvent = data[0]
        member = data[1]

        # No action should be taken if the bot made the reaction.
        if member.bot:
            return

        # Check that event was found in the internal record.
        if not orgEvent:
            self.client.logger.warning(
                'Someone tried to sign up for an untracked event.'
            )
            return

        # Check that event is not over, and handle rejection if required.
        if await self.eventHasPassed(data):
            return

        # Check that the deadline has not passed, and handle rejection if req.
        if await self.deadlineExceeded(data):
            return

        # If event is private, check if user has proper authorization.
        if orgEvent.data['Members Only'].upper() == 'YES':
            # Check that user has member role, handle rejection if not.
            if await self.noMemberRole(data):
                return

        # Attempt to get person object
        person = orgEvent.getParticipant(member.id)
        if person is not None:
            person.active = True
            # Check if user already has role, handle rejection if necessary.
            if await self.userAlreadyHasRole(data):
                return

            orgEvent.moveToBottom(person)

        # If user has passed all flags, add user to event and update
        # the embed.

        # Add role/person with role to internal event object.
        if 'participant' in orgEvent.roles.keys():
            pRole = orgEvent.roles['participant']
        else:
            pRole = None

        if person is None:
            person = event.Person(id=member.id, name=member.name, active=True)
            orgEvent.participants.append(person)

        if pRole is not None:
            person.roles.append(pRole)

        # if person is None:
        #     person = event.Person(id=member.id, name=member.name)
        #     if pRole:
        #         person.roles.append(pRole)
        #     orgEvent.participants.append(person)
        # elif pRole:
        #     person.roles.append(orgEvent.roles['participant'])

        # Add discord role.
        if pRole is not None:
            await self.addDiscordRole(member, orgEvent.roles['participant'])

        # Serialize data.
        utility.saveData(
            'eventData.json', self.client.orgEvents.json(indent=2)
        )

        # Update embed in discord.
        self.makeUpdate(orgEvent)

        # Send welcome message to the discussion channel.
        if 'discussion' in orgEvent.channels.keys():
            await self.sendWelcomeMsg(member, orgEvent.channels['discussion'])

        # TODO: Update the embed.

    async def eventHasPassed(self, data):
        # TODO: docstring.

        # Gather necessary data from the payload.
        orgEvent, member, message, memeberRole, emoji = data

        # Check if event has passed.
        currentTime = datetime.utcnow()
        if currentTime > orgEvent.dateAndTime:
            await member.send(
                'Sorry, you\'d need a time machine to join this event.',
                delete_after=60.0
                )
            await message.remove_reaction(emoji, member)
            return True
        return False

    async def deadlineExceeded(self, data):
        # TODO: Doctring...

        # Gather necessary data from the payload.
        orgEvent, member, message, memberRole, emoji = data

        # Check if deadline has passed.
        currentTime = datetime.utcnow()
        if orgEvent.deadline is not None:
            if currentTime > orgEvent.deadline:
                await member.send(
                    'Sorry, signup deadline has passed.',
                    delete_after=60.0
                )
                await message.remove_reaction(emoji, member)
                return True
        return False

    async def noMemberRole(self, data):
        # TODO: Docstring...

        # Gather necessary data from the payload.
        orgEvent, member, message, memberRole, emoji = data

        # Check if user has membership.
        if memberRole not in member.roles:
            await member.send(
                'Sorry, this event is for members only. '
                'You do not have the clearance to participate or spectate '
                'this event.',
                delete_after=60.0
            )
            await message.remove_reaction(emoji, member)
            return True
        return False

    async def userAlreadyHasRole(self, data):
        # TODO: docstring.

        # Gather necessary data from payload.
        orgEvent, member, message, memberRole, emoji = data

        # Check if user already has the role.
        person = orgEvent.getParticipant(member.id)
        if 'participant' in orgEvent.roles.keys():
            if person.getRole(orgEvent.roles['participant'].id) is not None:
                self.client.logger.warning(
                    'Event user inconsistency. Signup request received from '
                    'registered user.'
                )
                await member.send(
                    'Hmm, you seem to already be registered for the event.'
                    ' Strange. :shrug:',
                    delete_after=60.0
                )
                return True
        return False

    async def addDiscordRole(self, member, role):

        discordRole = member.guild.get_role(role.id)
        if discordRole not in member.roles:
            await member.add_roles(discordRole)

    async def sendWelcomeMsg(self, member, channel):

        discordChannel = self.client.get_channel(channel.id)
        welcomeMsg = (
            f'Welcome to the event {member.mention}, '
            'glad to have you!'
        )
        await discordChannel.send(welcomeMsg, delete_after=60.0)

    async def gatherPayloadData(self, payload):
        # Gather necessary data from the payload.
        messageId = payload.message_id
        orgEvent = self.getEvent(messageId)
        channel = self.client.get_channel(payload.channel_id)
        message = await channel.fetch_message(messageId)
        guild = message.guild
        member = guild.get_member(payload.user_id)
        memberRole = guild.get_role(Constants.MEMBER_ROLE_ID)
        emoji = payload.emoji.name

        # Return tuple with the needed data.
        return orgEvent, member, message, memberRole, emoji

    def getEvent(self, id):
        for orgEvent in self.client.orgEvents.events:
            if orgEvent.id == id:
                return orgEvent
                break
        else:
            return False

    def getUser(self, id, orgEvent):
        for user in orgEvent.participants:
            if user.id == id:
                return user
                break
        else:
            return False

    def makeUpdate(self, event):
        self.client.loop.create_task(
            self.runUpdate(event)
        )

    async def runUpdate(self, event):
        cog = self.client.get_cog('Updater')
        await cog.updateEmbed(event)


def setup(client):
    client.add_cog(EventSignupHandler(client))
