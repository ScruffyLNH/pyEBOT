import discord # noqa
import sheets
from utility import sendMessagePackets
from constants import Constants
from discord.ext import commands


class Daymar(commands.Cog):

    def __init__(self, client):
        self.client = client

    def updateDaymarSheet(self, member, memberType='Security'):
        rsiCol = 1
        memberTypeCol = 2
        notesCol = 4

        # Get the rsi names column.
        rsiNames = sheets.getCol(rsiCol, daymar=True)

        # Get available row index
        try:
            rowIndex = rsiNames.index('') + 1
        except ValueError:
            rowIndex = len(rsiNames) + 1

        # Write values to sheet.
        sheets.setCell(rowIndex, rsiCol, member.rsiName, daymar=True)
        sheets.setCell(rowIndex, memberTypeCol, memberType, daymar=True)
        if not member.verifiedHandle:
            sheets.setCell(
                rowIndex, notesCol, 'RSI handle not verified', daymar=True
            )

    def clearDaymarSheet(self):

        data = sheets.getAll(daymar=True)
        sheets.deleteRows(2, rowNum=len(data), daymar=True)

    # Commands
    @commands.command()
    async def getValue(self, ctx, rowIndex, colIndex):

        value = sheets.getCell(int(rowIndex), int(colIndex), daymar=True)
        await ctx.send(f'Value of cell is {value}.')

    @commands.command()
    async def getCol(self, ctx, colIndex):

        values = sheets.getCol(int(colIndex), daymar=True)

        try:
            index = values.index('') + 1
        except ValueError:
            index = len(values) + 1

        sheets.setCell(index, colIndex, 'Security', daymar=True)

        print(values)

    @commands.command()
    async def delRows(self, ctx, start, rowNum):
        start = int(start)
        rowNum = int(rowNum)

        sheets.deleteRows(start, rowNum, daymar=True)

    @commands.command()
    async def clearSheet(self, ctx):
        self.clearDaymarSheet()

    @commands.command()
    async def getCsv(self, ctx):

        fileName = 'DaymarSecurity.csv'

        # TODO: Refactor this mess.
        data = sheets.getAll(daymar=True)
        if len(data) < 1:
            try:
                with open(fileName, 'rb') as fp:
                    attachment = discord.File(fp=fp)
                await ctx.author.send(
                    'Could not find data from active Daymar Rally. Attaching '
                    'last saved csv file.',
                    file=attachment
                )
            except FileNotFoundError:
                await ctx.author.send('No Daymar Rally data found.')
        else:
            sheets.exportCsv(fileName)
            with open(fileName, 'rb') as fp:
                attachment = discord.File(fp=fp)
            await ctx.author.send(
                'Attaching latest Daymar Rally data.',
                file=attachment
            )

    # Command check for entire cog.
    def cog_check(self, ctx):
        """Check that the user of commands in this cog is the admin.

        :return: True if user is admin, else False
        :rtype: bool
        """
        return ctx.author.id == self.client.config.adminId


def setup(client):
    client.add_cog(Daymar(client))
