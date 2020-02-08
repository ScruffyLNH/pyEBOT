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
        # TODO: Refactor this. Dry it up.
        if self.registrationDeadline is not None:
            # Format the deadline timedate object into a readable string.

            # TODO: Add logic for expired signup, threat lvl if combat,
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
