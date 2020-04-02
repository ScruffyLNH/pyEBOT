import discord
from enum import Enum
from typing import List
from pydantic import BaseModel
from constants import Constants
from datetime import datetime


class TestClass:
    def __init__(self, cogData):
        self.cogData = cogData


class EventRecord(BaseModel):

    eventId: int
    eventName: str


class Role(BaseModel):

    id: int
    name: str


class ChannelType(Enum):

    text = 1
    voice = 2
    private = 3
    group = 4
    category = 5
    news = 6
    store = 7


class Channel(BaseModel):

    id: int
    name: str
    channelType: ChannelType


class Person(BaseModel):

    id: int
    name: str
    roles: List[Role] = []
    ships: List[str] = []
    events: List[EventRecord] = []

    def getRole(self, id):
        for role in self.roles:
            if role.id == id:
                return role
                break
        else:
            return None

    def removeRole(self, id):
        """Removes role from Person object given a valid id, and returns it.
        Also removes duplicates if they exist. In that case, the returned role
        will be the last duplicate found. Returns None if role was not found.

        :param id: Id of the role to be removed
        :type id: int
        """

        indices = [i for i, role in enumerate(self.roles) if role.id == id]
        foundRole = None
        count = 0
        for i in indices:
            foundRole = self.roles.pop(i - count)
            count += 1
        return foundRole


class Event(BaseModel):
    # TODO: Document this class when structure has been finalized.

    id: int = None
    data: dict
    keys: List[str]
    organizer: Person = None
    roles: dict = {}
    channels: List[Channel] = []
    participants: List[Person] = []
    privateIndication: dict = {}

    # def __init__(
    #     self, id, data, keys, organizer, roles, channels, participants
    # ):
    #     self.id = id
    #     self.data = data
    #     self.keys = keys
    #     self.organizer = organizer
    #     self.roles = roles
    #     self.channels = channels
    #     self.participants = participants

    #     # Background colors in GS is used to indicate whether or not a cell is
    #     # private. Getting formatting info is not supported by the API so info
    #     # on which cells are private are encoded to binary and stored in sheet
    #     # along with all the other data. Information is decoded and applied to
    #     # a copy of the data dictionary where the values are replaced by 1/0
    #     # for all keys.
    #     self.privateIndication = self.decodePrivate(data['Color Code'])

    def getParticipant(self, id):
        for p in self.participants:
            if p.id == id:
                return p
        else:
            return None

    # TODO: Refactor
    def addParticipant(self, person):
        # TODO: Documentation
        exists = False
        for participant in self.participants:
            if participant.id == person.id:
                exists = True

        if not exists:
            self.participants.append(person)

    # TODO: Refactor this using list comprehension
    def removeParticipant(self, person):
        # TODO: Documentation

        for i in range(len(self.participants)):
            if self.participants[i].id == person.id:
                del self.participants[i]

    def makeEmbed(
        self,
        censored,
        user,
        includeAuthor=True,
        includePreamble=True,
        includeBody=True,
        includeVoiceChnl=True,
        includeRollCall=True,
        includeFooter=True,
        includeImage=True
    ):
        # TODO: Document this method. **censored TRUE/FALSE**

        # TODO: Add Type: Open event, anyone may join./
        #                 Closed event, membership required.

        # IF event is private print this somewhere at the start:
        # This is a private event, and may contain classified information.
        # to view the classified info, sign up for the event and check the
        # event channel that will open.

        # Override private keys if censored argument is not True
        if censored:
            privateIndication = self.privateIndication
        else:
            privateIndication = dict.fromkeys(self.keys)

        # Default string to print if value under a key is private.
        privateString = ':no_entry_sign: Classified :no_entry_sign:'

        # Create the buffer that stores strings that forms the preamble.
        preambleBuffer = []

        # If event is private a string explaining this is added to the
        # preamble.
        if self.data['Members Only'].upper() == 'YES':
            preambleBuffer.append(
                ':lock: This is a private event. Membership required.'
                '\n'
            )

        # If separate channels has been created for event a string explaining
        # this will be added to the preamble
        if (self.data['Members Only'].upper() == 'YES' or
                True in self.privateIndication.values() or
                self.data['Add Channels'].upper() == 'YES'):

            preambleBuffer.append(
                ':hash: Separate channels for this event has been created. '
                'To access these channels, sign up for the event.'
                '\n'
            )

        # If any key holds private data, users are notified that event has
        # classified data and how to access that data.
        if True in self.privateIndication.values():
            preambleBuffer.append(
                ':zipper_mouth: '
                'To view classified information, sign up is required. '
                'Full description will be disclosed in this events text '
                'channel.'
                '\n'
            )

        # Check if event has a sign-up deadline.
        if self.data['Deadline'] != '':
            # Check if the sign-up deadline is classified.
            if privateIndication['Deadline']:
                deadlineString = privateString
            else:
                deadlineString = (
                    self.data["Deadline"].strftime(Constants.DT_TEXT_PARSE)
                )
            preambleBuffer.append(
                f':alarm_clock: **Registration Deadline**: {deadlineString}'
                '\n'
            )

        # Make the message preamble from the preambleBuffer.
        preamble = '\n'.join(preambleBuffer)

        # Create the buffer that stores strings forming the body of the msg.
        bodyBuffer = []

        # TODO: Find a way to refactor wet code ↓ Possibly iterate through
        # self.keys Reordering would be necessary.

        # Check if date and time is classified.
        if privateIndication['Date Time']:
            dateTimeString = privateString
        else:
            dateTimeString = self.data['Date Time'].strftime(
                Constants.DT_TEXT_PARSE
            )
        bodyBuffer.append(f':calendar: Date and Time: {dateTimeString}')

        # Check if event location is classified.
        if privateIndication['Location']:
            locationString = privateString
        else:
            locationString = self.data['Location']
        bodyBuffer.append(f':globe_with_meridians: Location: {locationString}')

        # Check if event description is classified.
        if privateIndication['Description']:
            descriptionString = privateString
        else:
            descriptionString = self.data['Description']
        bodyBuffer.append(f':newspaper: Description: \n{descriptionString}\n')

        # Check if event organizer is classified.
        if privateIndication['Organizer']:
            organizerString = privateString
        elif self.data['Organizer'] != '':
            organizerString = self.data['Organizer']
        else:
            organizerString = None
        if organizerString:
            bodyBuffer.append(f':speaking_head: Organizer: {organizerString}')

        # Check if event duration is classified.
        if privateIndication['Duration']:
            durationString = privateString
        else:
            durationString = self.data['Duration']
        bodyBuffer.append(f':stopwatch: Duration: {durationString}')

        # Check if additional info is private.
        # if self.data["Additional Info"]:
        #     if not privateIndication['Additional Info']:
        #         bodyBuffer.append(self.data['Additional Info'])

        # bodyBuffer.append('\n')

        # If voice channel is public, specify in embed body.
        if self.roles:
            voiceString = (
                ':loud_sound: Voice Channel: '
                'A private voice channel has been created for this event. '
                'Sign up to gain access.'
            )
        else:
            voiceString = (
                ':loud_sound: Voice Channel: ---Central Lobby---'
            )

        rollCallString = (
            ':mega: **ROLL CALL**: Click on the :white_check_mark: to sign up.'
        )

        # Create a footer list that will be turned into a string for the embed
        # footer.
        footerBuffer = []

        if self.data['Deadline']:
            if datetime.utcnow() > self.data['Deadline']:
                footerBuffer.append(f'\nRegistration has closed.\n')

        # TODO: Add text for what channel to use.
        # TODO: Add organizer in description of embed.

        if self.participants is not None:
            footerBuffer.append('Participants: (In chronological order).')
            # Get the name of every participant and put it in a list.
            people = [p.name for p in self.participants]
            # Add string with all names separated with a comma to the buffer.
            footerBuffer.append(f'{", ".join(people)}')

        body = '\n'.join(bodyBuffer)

        msg = ''
        if includePreamble:
            msg += (preamble + '\n')
        if includeBody:
            msg += (body + '\n\n')
        if includeVoiceChnl:
            msg += (voiceString + '\n')
        if includeRollCall:
            msg += (rollCallString)

        eventPost = discord.Embed(
            title=self.data["Event"],
            description=msg,
            colour=Constants.EVENT_COLOR
        )

        timeToEvent = self.data['Date Time'] - datetime.utcnow()

        if timeToEvent.days == 0:
            countdownString = 'Event kicking off today!'
        elif timeToEvent.days == 1:
            countdownString = 'Event kicking off tomorrow!'
        elif timeToEvent.days > 1:
            countdownString = f'Event kicking off in {timeToEvent.days} days!'
        else:
            countdownString = 'Event has concluded.'

        if includeAuthor:
            eventPost.set_author(
                name=countdownString,
                icon_url=f'{user.avatar_url}'
            )

        eventPost.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/684911169189838863/684922720722485248/FR17_Logo_Opaque.png'
        )
        if includeImage:
            eventPost.set_image(
                url='https://cdn.discordapp.com/attachments/684911073304117319/684919964049866858/A_CARRACKING_GOOD_TIME.jpg'
            )

        if includeFooter:
            eventPost.set_footer(text=''.join(footerBuffer))

        return eventPost

    def decodePrivate(self, colorCode):
        """Creates a dictionary that holds information about which keys contain
        private information.

        :param colorCode: A number describing what keys should be private.
        :type colorCode: string
        :param keys: Collection of all the keys used for event data dicts.
        :type keys: List of string
        :return: Information about which keys contain private information.
        :rtype: dictionary
        """

        # TODO: REFACTOR. Break method down to smaller methods. Remember to
        # update the docstring after refactoring.

        # Convert strings in colorCode to integers.
        colorCode = int(colorCode)
        # Convert color code to a binary string, and remove the 0b prefix.
        binaryRep = str(bin(colorCode))[2:]
        # Pad with leading zeros, so that there are always 24 binary digits.
        binaryRep = binaryRep.zfill(24)
        # Above code yields a 0bxxx formatted string. Remove the two first
        # characters and put it in a list.
        binaryReps = list(binaryRep)
        # Convert to true/false values
        privateFlags = [False if d == '0' else True for d in binaryReps]

        # Create a new dictionary from keys.
        privateInd = dict.fromkeys(self.keys)

        # Set the values in the dictionary to true if the corresponding key
        # should be marked as private.
        for i in range(len(privateFlags)):
            privateInd[self.keys[i]] = privateFlags[i]

        return privateInd


class OrgEvents(BaseModel):

    events: List[Event] = []
