
class TestClass:
    def __init__(self, cogData):
        self.cogData = cogData


class EventData:
    # Strings to separate messages in discord
    topString = '\n_ _'
    bottomString = '_ _\n'

    def __init__(self, messageId, rowData):
        self.messageId = messageId
        self.message = self.eventStringBuilder(rowData)

    @classmethod
    def setTopString(cls, string):
        cls.topString = string

    @classmethod
    def setBottomString(cls, string):
        cls.bottomString = string

    def eventStringBuilder(self, rowData):
        outputString = (
            f'{EventData.topString}\n'
            f'**Event Name: {rowData["Event"]}**\n'
            f'Date and Time: {rowData["Date"]}, {rowData["Time"]}\n'
            f'Description: {rowData["Description"]}\n'
            f'Participants (in order of signup)\n {rowData["Participants"]}'
            f'{EventData.bottomString}\n'
        )
        return outputString
