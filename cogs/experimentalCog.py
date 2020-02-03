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
        self.updateCellIndices = (2, 17)  # TODO: refactor this bullshit
        self.eventDataList = []
        # Obtain channel ID by using devTools (!load devTools !getChannelId)
        self.channelId = 665424669871964170
        if self.client.is_ready():
            self.connectToChannel(self.channelId)

    # Code to be executed when cog is unloaded
    def cog_unload(self):
        pass  # TODO: remeber to check if there is something that needs to be
        # done upon unload

    # Functions
    def connectToChannel(self, channelId):
        self.channel = self.client.get_channel(channelId)
        print(f'Connecting to channel: {self.channel}')

    def updateDiscord(self):
        sheetData = sheets.getAll()
        # Process sheet data
        for i in range(len(sheetData)):
            # If a record is found without messageId an async loop will be
            # triggered to populate all missing message ids
            if sheetData[i]['MessageId'] == '':
                loop = asyncio.get_event_loop()
                try:
                    sliceIndex = i - len(sheetData)  # (Negative number)
                    # Pass sliced list from current index to end of list
                    loop.run_until_complete(
                        self.populateIds(
                            sheetData[sliceIndex:], i))
                except Exception as e:
                    print(e)
                finally:
                    loop.close
                break

    # Coroutines
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

    @commands.command()
    async def editMessage(self, ctx, messageId, *, newContent):
        msg = await ctx.channel.fetch_message(messageId)
        await msg.edit(content=newContent)

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
