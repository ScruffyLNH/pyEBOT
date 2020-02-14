import discord
from datetime import datetime


class TestClass:
    def __init__(self, cogData):
        self.cogData = cogData


class Event:
    # String to separate discord messages.
    topString = '\n_ _'
    bottomString = '_ _\n'
    shtDateTimeFormat = '%m/%d/%Y %H:%M:%S'

    def __init__(self, sheetInfo):
        self.id = int(0)  # Make doubbly shure this is an int.
        self.message = None
        self.eventResponsible = None
        self.sheetInfo = sheetInfo
        self.eventName = sheetInfo['Event']
        # Convert date and time from string to datetime object and store.
        self.dateTime = datetime.strptime(
            sheetInfo['Date Time'], Event.shtDateTimeFormat)
        self.registrationDeadline = datetime.strptime(
            sheetInfo['Deadline'], Event.shtDateTimeFormat)
        self.channels = None
        self.participants = []

    @classmethod
    def setTopString(cls, string):
        cls.topString = string

    @classmethod
    def setBottomString(cls, string):
        cls.bottomString = string

    def addParticipant(self, person):
        exists = False
        for participant in self.participants:
            if participant.id == person.id:
                exists = True

        if not exists:
            self.participants.append(person)

    # TODO: Refactor this using list comprehension
    def removeParticipant(self, person):
        for i in range(len(self.participants)):
            if self.participants[i].id == person.id:
                del self.participants[i]

    def postBuilder(self, sheetInfo):

        stringBuffer = []
        # stringBuffer.append(f'**Event Name: {sheetInfo["Event"]}**')

        if self.registrationDeadline != '':
            dlStr = self.registrationDeadline.strftime("%A %B %#d, %H:%M UTC")
            stringBuffer.append(f'Registration Deadline: {dlStr}')

        dlStr = self.dateTime.strftime("%A %B %#d, %H:%M UTC")
        stringBuffer.append(f'Date and Time: {dlStr}')
        stringBuffer.append(f'Location: {sheetInfo["Location"]}')
        stringBuffer.append(f'Description: {sheetInfo["Description"]}')
        stringBuffer.append(f'Duration: {sheetInfo["Duration"]}')
        stringBuffer.append(
            f'**ROLL CALL**: React with a :white_check_mark: to sign up.')

        if not sheetInfo["Additional Info"] == '':
            stringBuffer.append(sheetInfo["Additional Info"])

        # Create a footer list that will be turned into a string for the embed
        # footer.
        footerBuffer = []

        if self.registrationDeadline is not None:
            if datetime.utcnow() > self.registrationDeadline:
                footerBuffer.append(f'\nRegistration has closed.\n')

        # TODO: Add text for what channel to use. If custom it should
        # read: A voice and text channel for this event has been opened in
        # #events group.

        if self.participants is not None:
            footerBuffer.append('Participants: (In chronological order).')
            # Get the name of every participant and put it in a list.
            people = [p.name for p in self.participants]
            # Add string with all names separated with a comma to the buffer.
            footerBuffer.append(f'{", ".join(people)}')

        msg = '\n'.join(stringBuffer)

        eventPost = discord.Embed(
            title=f'{sheetInfo["Event"]}',
            description=msg,
            colour=0x6b90b5
        )
        # eventPost.set_author(
        #     name='Event kicking off in x days!',
        #     icon_url='https://i.imgur.com/1hXnSXN.jpg')
        eventPost.set_thumbnail(
            url='https://i.imgur.com/tB7S52z.jpeg'
        )
        eventPost.set_image(
            url='https://thumbs.gfycat.com/HomelyRigidGreatdane-size_restricted.gif')

        eventPost.set_footer(text=''.join(footerBuffer))

        return eventPost


class Person:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.roles = None
        self.Ships = None


class EventData:
    # Strings to separate messages in discord
    topString = '\n_ _'
    bottomString = '_ _\n'

    def __init__(self, messageId, rowData):
        self.messageId = messageId
        self.message = self.eventStringBuilder(rowData)
        # self.participants = rowData['Participants']

    @classmethod
    def setTopString(cls, string):
        cls.topString = string

    @classmethod
    def setBottomString(cls, string):
        cls.bottomString = string

    def eventStringBuilder(self, rowData):
        outputString = (
            f'{EventData.topString}\n'
            # f'**Event Name: {rowData["Event"]}**\n'
            # f'Date and Time: {rowData["Date"]}, {rowData["Time"]}\n'
            # f'Description: {rowData["Description"]}\n'
            # f'Participants (in order of signup)\n {rowData["Participants"]}'
            f'{EventData.bottomString}\n'
        )
        return outputString
