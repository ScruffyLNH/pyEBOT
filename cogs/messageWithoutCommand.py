import discord # noqa
import asyncio
import sheets
from discord.ext import tasks, commands


class MessageWithoutCommand(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.channelId = 665424669871964170
        self.checkSheetStatus.start()
        self.updateCellIndices = (2, 17)

    # Code to be executed when cog is unloaded
    def cog_unload(self):
        self.checkSheetStatus.cancel()

    # Functions
    def updateDiscord(self):
        print('Updating discord!!!')
        self.client.loop.create_task(self.sendMessage())

    # Coroutines
    async def sendMessage(self):
        channel = self.client.get_channel(self.channelId)
        await channel.send('Helloooo, uncle Leo!')

    # Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

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
    client.add_cog(MessageWithoutCommand(client))
