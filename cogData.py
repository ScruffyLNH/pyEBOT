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
        self.eventId = 0
        self.sheetInfo = sheetInfo
        self.eventName = sheetInfo['Event']
        # Convert date and time from string to datetime object and store.
        self.dateTime = datetime.strptime(
            sheetInfo['Date Time'], Event.shtDateTimeFormat)
        self.registrationDeadline = None
        self.channels = None
        self.participants = None

    @classmethod
    def setTopString(cls, string):
        cls.topString = string

    @classmethod
    def setBottomString(cls, string):
        cls.bottomString = string

    def msgBuilder(self, sheetInfo):

        stringBuffer = []
        stringBuffer.append(f'**Event Name: {sheetInfo["Event"]}**')

        if self.registrationDeadline is not None:
            dlStr = self.registrationDeadline.strftime("%A %B %#d, %H:%M UTC")
            stringBuffer.append(f'Registration Deadline: {dlStr}')

        dlStr = self.registrationDeadline.strftime("%A %B %#d, %H:%M UTC")
        stringBuffer.append(f'Date and Time: {dlStr}')
        stringBuffer.append(f'Location: {sheetInfo["Location"]}')
        stringBuffer.append(f'Description: {sheetInfo["Description"]}')
        stringBuffer.append(f'Duration: {sheetInfo["Duration"]}')
        stringBuffer.append(
            f'**ROLL CALL**: React with a :white_check_mark: to sign up.')

        if sheetInfo["Additional Info"] is not None:
            stringBuffer.append(sheetInfo["Additional Info"])

        # TODO: Put this in footer maybe?
        if self.registrationDeadline is not None:
            if datetime.utcnow() > self.registrationDeadline:
                stringBuffer.append(f'\n**Registration Closed**\n')

        # TODO: Add text for what channel to use. If custom it should
        # read: A voice and text channel for this eventhas been opened in
        # #events group.

        # TODO: Put all this in an embed

        if self.participants is not None:
            stringBuffer.append('Participants: (In chronological order)')
            # Get the name of every participant and put it in a list.
            people = [p.name for p in self.participants]
            # Add string with all names separated with a comma to the buffer.
            stringBuffer.append(f'{", ".join(people)}')

        msg = '\n'.join(stringBuffer)

        if self.registrationDeadline is not None:
            # Format the deadline timedate object into a readable string.

            # TODO: Add logic for expired signup,
            # additional information if present etc...

            dlStr = self.registrationDeadline.strftime("%A %B %#d, %H:%M UTC")
            msg = (
                f'{EventData.topString}\n'
                f'**Event Name: {sheetInfo["Event"]}**\n'
                f'Registration Deadline: {dlStr}\n'
                f'Date and Time: {dlStr}\n'
                f'Location: {sheetInfo["Location"]}\n'
                f'Description: {sheetInfo["Description"]}\n'
                f'Duration: {sheetInfo["Duration"]}\n'
                f'**ROLL CALL**: React with a :white_check_mark: to sign up.'
            )
        else:
            msg = (
                f'{EventData.topString}\n'
                f'**Event Name: {sheetInfo["Event"]}**\n'
                f'ENDTEST\n'
            )
        return msg


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
