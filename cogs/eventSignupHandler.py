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
            if payload.emoji.name == '✅':
                self.client.loop.create_task(
                    self.handleSignup(payload)
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id == Constants.MAIN_CHANNEL_ID:
            if payload.emoji.name == '✅':
                self.client.loop.create_task(
                    self.handleCancellation(payload)
                )

    async def handleSignup(self, payload):
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

            # TODO: If user has passed all flags, add user to event and update the
            # embed.
            # Check if user already exists in the Event object.
            # If not, add user.
            # Update the embed.

            # If event has separate channel add roles to user, and send a
            # welcome mention in the text channel.
            if orgEvent.roles:
                participantRole = guild.get_role(
                    orgEvent.roles['participant'].id
                )
                await member.add_roles(participantRole)

                # TODO: Refactor. Make reference to orgEvent channel more robust.
                eventChannel = self.client.get_channel(
                    orgEvent.channels[0].id
                )
                welcomeMsg = (
                    f'Welcome to the event {member.mention}, '
                    'glad you could make it!'
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

    async def handleCancellation(self, payload):
        pass

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
