import discord # noqa
import sheets
import asyncio
import cogData as cd
from discord.ext import tasks, commands


class ExperimentalCog(commands.Cog):

    def __init__(self, client):
        self.client = client
        # self.printer.start()
        self.checkSheetStatus.start()
        self.updateCellIndices = (2, 17)
        self.eventDataList = []
        # Obtain channel ID by using devTools (!load devTools !getChannelId)
        self.channelId = 665424669871964170
        if self.client.is_ready():
            self.connectToChannel(self.channelId)

    # Code to be executed when cog is unloaded
    def cog_unload(self):
        # close loop
        loop = asyncio.get_event_loop()
        loop.close()
        # TODO: remeber to check if there is something that needs to be
        # done upon unload

    # Functions
    def connectToChannel(self, channelId):
        self.channel = self.client.get_channel(channelId)
        print(f'Connecting to channel: {self.channel}')

    def checkMessageId(self, sheetData):
        for i in range(len(sheetData)):
            if sheetData[i]['MessageId'] == '':
                # Slice list from where the first empty messageId appears and
                # pass the bottom slice to function for processing
                sliceIndex = i - len(sheetData)
                self.updateIds(sheetData[sliceIndex:], i)
                break

    def updateIds(self, eventData, index):
        loop = asyncio.get_event_loop()
        try:
            # loop.run_until_complete(self.populateIds(eventData, index))
            # TODO: check if this will create race condition issue.
            loop.create_task(self.populateIds(eventData, index))
        except Exception as e:
            print(e)

    def checkParticipants(self, edList, newRecords):
        for ed in edList:
            matchRecord = filter(
                lambda record:
                record['MessageId'] == ed.messageId,
                newRecords)
            if matchRecord:
                if not matchRecord['Participants'] == ed.participants:
                    ed.participants = matchRecord['Participants']
                    ed.message = ed.eventStringBuilder(matchRecord)
                    self.updateParticipants(ed)

    def updateParticipants(self, record):
        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self.editMessage(record.msgId, record.msg))
        except Exception as e:
            print(e)

    def updateDiscord(self):
        sheetData = sheets.getAll()
        # Check that all messages have ids. If not create message and populate.
        self.checkMessageId(sheetData)

        # Check if new participants have been added to any of the events.
        # self.checkParticipants(self.eventDataList, sheetData)

    # Coroutines
    async def editMessage(self, msgId, msg):
        discordMsg = self.channel.fetch_message(self.msgId)
        await discordMsg.edit(content=msg)

    async def populateIds(self, sheetData, startIndex):
        for i in range(len(sheetData)):
            ed = cd.EventData('', sheetData[i])
            msg = ed.eventStringBuilder(sheetData[i])
            await self.channel.send(msg)
            msgId = self.channel.last_message_id
            ed.message = msg
            ed.messageId = msgId
            self.eventDataList.append(ed)
            idIndex = (startIndex + i + 2, 7)  # Cell index for id in sheets
            sheets.setCell(*idIndex, msgId)

    async def sendMessage(self, msg):
        await self.channel.send(msg)
        return self.channel.last_message_id

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        self.connectToChannel(self.channelId)

    @commands.Cog.listener()
    async def on_message(self, message):
        messageId = message.id
        print(f'Message ID is: {messageId}')

    # Commands
    @commands.command()
    async def printSheetRow(self, ctx, rowNum):
        rowData = sheets.getRow(rowNum)
        await ctx.send(
            f'The values in row {rowNum} are {rowData}'
        )

    # Check google sheets status
    @tasks.loop(seconds=2.5)
    async def checkSheetStatus(self):
        await self.client.wait_until_ready()
        # Status is either 0,1,2 depending on the state of google sheet
        status = int(sheets.getCell(*self.updateCellIndices))

        if (status == 2):
            self.updateDiscord()
            status = 0
            sheets.setCell(*self.updateCellIndices, status)


def setup(client):
    client.add_cog(ExperimentalCog(client))
