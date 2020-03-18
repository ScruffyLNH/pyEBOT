import discord # noqa
from constants import Constants
import event
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
        messageId = payload.message_id
        # Check which event was reacted to
        orgEvent = self.findEvent(messageId)
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
        # Get current utc time
        currentTime = datetime.utcnow()

        if orgEvent and not member.bot:
            # Check if event has passed.
            if currentTime > orgEvent.data['Date Time']:
                await member.send(
                    'Sorry, you\'d need a time machine to join this event.',
                    delete_after=60.0
                    )
                await message.remove_reaction('✅', member)
                return

            # Check if within deadline.
            if orgEvent.data['Deadline'] != '':
                if currentTime > orgEvent.data['Deadline']:
                    await member.send(
                        'Sorry, signup deadline has passed.',
                        delete_after=60.0
                    )
                    await message.remove_reaction('✅', member)
                    return

            # If event is private, check if user has proper authorization.
            if orgEvent.data['Members Only'].upper() == 'YES':
                if memberRole not in member.roles:
                    await member.send(
                        'Sorry, this event is for members only.',
                        delete_after=60.0
                    )
                    await message.remove_reaction('✅', member)
                    return

            # Check if user already exists in the Event object.
            _user = orgEvent.getParticipant(member.id)  # TODO: Make this check for the acual role instead of person to determine if user is already signed up.
            if _user:
                # Check if user already has the role.
                r = _user.getRole(orgEvent.roles['participant'].id)
                if r:
                    await member.send(
                        'Hmm, you seem to already be registered for the event.'
                        ' Strange. :shrug:',
                        delete_after=60.0
                    )
                    return

            # If user has passed all flags, add user to event and update
            # the embed.
            p = event.Person(member.id, member.name)
            if not p.getRole(orgEvent.roles['participant'].id):
                r = event.Role(memberRole.name, memberRole.id)
                p.roles.append(r)  # TODO: Change persons roles to list
                orgEvent.participants.append(p)

                # TODO: Update the embed.

            # If event has separate channel add roles to user, and send a
            # welcome mention in the text channel.
            if orgEvent.roles:
                participantRole = guild.get_role(
                    orgEvent.roles['participant'].id
                )
                if participantRole not in member.roles:
                    await member.add_roles(participantRole)

                # TODO: Refactor. Make reference to orgEvent channel more robust.
                eventChannel = self.client.get_channel(
                    orgEvent.channels[0].id
                )
                welcomeMsg = (
                    f'Welcome to the event {member.mention}, '
                    'glad to have you!'
                )
                await eventChannel.send(welcomeMsg, delete_after=60.0)
        elif member.bot:
            pass
        else:
            print(
                'Someone tried to sign up for an event that no longer exists.'
            )

        # If private event check if user is member.
        # Instanciate user and add to client.orgEvents.
        # Update embed.
        # Grant user roles if the event has a private channel.
        # Mention user in event channel: "@examplePerson Welcome to the event!"

    async def handleCancellation(self, payload):  # TODO: generalize method to handle more emojis and roles.

        messageId = payload.message_id
        # Check which event was reacted to
        orgEvent = self.findEvent(messageId)
        # Get channel object
        channel = self.client.get_channel(payload.channel_id)
        # Get the Message object.
        message = await channel.fetch_message(messageId)
        # Get the Guild object.
        guild = message.guild
        # Get the user who reacted
        member = guild.get_member(payload.user_id)

        if orgEvent.roles:
            roleId = orgEvent.roles['participant'].id
            participantRole = guild.get_role(roleId)
            await member.remove_roles(participantRole)

            person = orgEvent.getParticipant(member.id)
            if person:
                person.removeRole(roleId)

    def findEvent(self, id):
        for orgEvent in self.client.orgEvents:
            if orgEvent.id == id:
                return orgEvent
                break
        else:
            return False

    def findUser(self, id, orgEvent):
        for user in orgEvent.participants:
            if user.id == id:
                return user
                break
        else:
            return False


def setup(client):
    client.add_cog(EventSignupHandler(client))
