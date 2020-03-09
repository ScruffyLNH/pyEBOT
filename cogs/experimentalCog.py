import discord # noqa
import sheets
import gspread
import asyncio
import pathlib
import event
from discord.ext import tasks, commands

# TODO: sort input sheet list by date.


class ExperimentalCog(commands.Cog):

    def __init__(self, client):
        self.client = client
        # self.printer.start()
        self.checkSheetStatus.start()
        self.updateCellIndices = (2, 26)  # TODO: Refactor this nasty shite
        self.eventDataList = []
        # Obtain channel ID by using devTools (!load devTools !getChannelId)
        self.channelId = 676567548568797266
        if self.client.is_ready():
            self.connectToChannel(self.channelId)

    # Code to be executed when cog is unloaded
    def cog_unload(self):
        # Cancel repeating tasks
        self.checkSheetStatus.cancel()
        # TODO: remeber to check if there is something that needs to be
        # done upon unload

    # Functions
    def connectToChannel(self, channelId):
        self.channel = self.client.get_channel(channelId)
        print(f'Connected to channel: {self.channel}')

    # def checkParticipants(self, edList, newRecords):
    #     for ed in edList:
    #         matchRecord = filter(
    #             lambda record:
    #             record['MessageId'] == ed.messageId,
    #             newRecords)
    #         if matchRecord:
    #             if not matchRecord['Participants'] == ed.participants:
    #                 ed.participants = matchRecord['Participants']
    #                 ed.message = ed.eventStringBuilder(matchRecord)
    #                 self.updateParticipants(ed)

    # TODO: This must be refactored to take into account that events might not
    # be posted in order.
    def checkMessageId(self, sheetData):
        for i in range(len(sheetData)):
            if sheetData[i]['Id'] == '' or sheetData[i]['Id'] == 0:
                # Slice list from where the first empty messageId appears and
                # pass the bottom slice to function for processing
                sliceIndex = i - len(sheetData)
                self.updateIds(sheetData[sliceIndex:], i)
                break

    def updateIds(self, eventData, index):
        loop = asyncio.get_event_loop()
        try:
            # TODO: check if this will create race condition issue.
            loop.create_task(self.populateIds(eventData, index))
        except Exception as e:
            print(e)

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
            ed = event.Event(sheetData[i])
            post = ed.postBuilder(sheetData[i])
            msg = await self.channel.send(embed=post)
            # msgId = self.channel.last_message_id
            ed.message = msg
            self.eventDataList.append(ed)
            # idIndex = (startIndex + i + 2, 7)  # Cell index for id in sheets
            # sheets.setCell(*idIndex, msgId)

    # Post an embed. To add images send a string with path to the relevant
    # keyword arguments.
    async def sendEmbed(
        self,
        embed,
        image='',
        thumbnail='',
        icon='',
        message=None,
        edit=False
    ):

        files = []
        # TODO: Refacor this (wet code.)
        if not thumbnail == '':
            tnStrings = thumbnail.split('/')
            tnFileName = tnStrings[-1]
            path = pathlib.Path(thumbnail)
            tnFile = discord.File(path, tnFileName)
            embed.set_thumbnail(url=f'attachment://{tnFileName}')
            files.append(tnFile)

        if not image == '':
            imStrings = image.split('/')
            imFileName = imStrings[-1]
            imPath = pathlib.Path(image)
            imFile = discord.File(imPath, imFileName)
            embed.set_image(url=f'attachment://{imFileName}')
            files.append(imFile)

        user = self.client.get_user(312381318891700224)
        embed.set_author(
            name='Event kicking off in x days!',
            icon_url=f'{user.avatar_url}'
        )
        if edit:
            embed.set_image(
                url='https://thumbs.gfycat.com/HomelyRigidGreatdane-size_restricted.gif'
            )
            await message.edit(embed=embed)
        else:
            msg = await self.channel.send(files=files, embed=embed)
            self.client.events.append(msg)

    async def sendMessage(self, msg):
        discordMsg = await self.channel.send(msg)
        return discordMsg.id

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        self.connectToChannel(self.channelId)

    @commands.Cog.listener()
    async def on_message(self, message):
        messageId = message.id
        print(f'Message ID is: {messageId}')

    # Commands
    # TODO: remove the testing commands
    @commands.command()
    async def testEmbed(self, ctx):
        sheetInfo = sheets.getAll()
        ed = event.Event(sheetInfo[2])
        embed = ed.postBuilder(sheetInfo[2])
        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self.sendEmbed(
                embed,
                thumbnail='Res/FR17Logo.png',
                image='Res/Moonbreaker.jpg'))
        except Exception as e:
            print(e)

    @commands.command()
    async def testEmbedNoImage(self, ctx):
        sheetInfo = sheets.getAll()
        ed = event.Event(sheetInfo[2])
        embed = ed.postBuilder(sheetInfo[2])
        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self.sendEmbed(
                embed,
                thumbnail='Res/FR17Logo.png'))
        except Exception as e:
            print(e)

    @commands.command()
    async def editEmbed(self, ctx):
        sheetInfo = sheets.getAll()
        ed = event.Event(sheetInfo[2])
        embed = ed.postBuilder(sheetInfo[2])
        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self.sendEmbed(
                embed,
                thumbnail='Res/FR17Logo.png',
                image='Res/Moonbreaker.jpg',
                message=self.client.events[-1],
                edit=True))
        except Exception as e:
            print(e)

    @commands.command()
    async def printSheetRow(self, ctx, rowNum):
        rowData = sheets.getRow(rowNum)
        await ctx.send(
            f'The values in row {rowNum} are {rowData}'
        )

    # Check google sheets status
    @tasks.loop(seconds=5)
    async def checkSheetStatus(self):
        await self.client.wait_until_ready()
        # Status is either 0,1,2 depending on the state of google sheet

        # Attempt to read cell with gspread.
        for attempt in range(5):
            try:
                status = int(sheets.getCell(*self.updateCellIndices))
            except gspread.exceptions.APIError as e:
                print(e)
                sheets.refreshAuth()
            else:
                break

        # try:
        #     status = int(sheets.getCell(*self.updateCellIndices))
        # except gspread.exceptions.APIError as e:
        #     print(e)
        #     sheets.login()
        # finally:
        #     status = 0
        # TODO: Refactor this. The gspread call will eventually fail. Have to
        # do an event trigger somehow.

        if (status == 2):
            self.updateDiscord()
            status = 0
            sheets.setCell(*self.updateCellIndices, status)

    @checkSheetStatus.before_loop
    async def before_checkSheetStatus(self):
        print('Sheet-checking loop is waiting for client to be ready.')
        await self.client.wait_until_ready()
        print('Sheet-checking loop has started.')


def setup(client):
    client.add_cog(ExperimentalCog(client))
