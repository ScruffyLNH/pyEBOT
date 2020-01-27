import discord # noqa
import sheets
import cogData
from discord.ext import tasks, commands


class ExperimentalCog(commands.Cog):

    def __init__(self, client):
        self.client = client
        # self.printer.start()
        self.checkSheetStatus.start()
        self.updateCellIndices = (2, 17)

    # Code to be executed when cog is unloaded
    def cog_unload(self):
        # self.printer.cancel()
        self.checkSheetStatus.cancel()

    # Functions
    def updateDiscord(self):
        print('Discord has been updated.')

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        messageId = message.id
        print(f'Message ID is: {messageId}')

    # Commands
    @commands.command()
    async def createMessage(self, ctx):
        messageId = ctx.message.id
        await ctx.send(f'The id of your message is {messageId}')

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

    """
    # Background tasks
    @tasks.loop(seconds=3.0)
    async def printer(self):
        await self.client.wait_until_ready()
        data = sheets.getRow(1)
        print(data)
    """

    # Check google sheets status
    @tasks.loop(seconds=2.5)
    async def checkSheetStatus(self):
        await self.client.wait_until_ready()
        # Status is either 0,1,2 depending on the state of google sheet
        status = int(sheets.getCell(
            self.updateCellIndices[0],
            self.updateCellIndices[1]))

        if (status == 2):
            self.updateDiscord()
            status = 0
            sheets.setCell(
                self.updateCellIndices[0],
                self.updateCellIndices[1],
                status)


def setup(client):
    client.add_cog(ExperimentalCog(client))
