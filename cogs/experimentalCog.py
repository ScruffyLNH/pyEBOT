import discord # noqa
import sheets
from discord.ext import commands


class ExperimentalCog(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        messageId = message.id
        print(f'Message ID is: {messageId}')

    # Commands
    @commands.command()
    async def createMessage(self, ctx):
        messageId = ctx.message.id
        await ctx.send(f'The id of this message is {messageId}')

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


def setup(client):
    client.add_cog(ExperimentalCog(client))
