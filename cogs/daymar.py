import discord # noqa
import sheets
import utility
import event
from constants import Constants
from discord.ext import commands


class Daymar(commands.Cog):

    def __init__(self, client):
        self.client = client

    def addParticipant(self, member, memberType='Security'):
        rsiCol = 0
        serverCol = 2
        idCol = 4

        sheetData = sheets.getAllValues(daymar=True)

        # Get the rsi names column.
        rsiNames = [row[rsiCol] for row in sheetData]
        serverNums = [row[serverCol] for row in sheetData]
        memberIds = [row[idCol] for row in sheetData]

        # Get available row index
        try:
            rowIndex = rsiNames.index('')
        except ValueError:
            rowIndex = len(rsiNames)

        # Check if user already exists in sheet.
        for index, id in enumerate(memberIds):
            try:
                pId = int(id)
                if member.id == pId:
                    rowIndex = index
                    server = int(serverNums[index])
                    break
            except ValueError:
                server = ''

        startIndex = (rowIndex, 0)
        endIndex = (rowIndex, 4)

        # Write values to sheet.
        if member.rsiHandle is not None:
            data = [member.rsiHandle, memberType, server, '', str(member.id)]
            sheets.setRange(startIndex, endIndex, [data], daymar=True)
        else:
            data = [
                member.name,
                memberType,
                server,
                'RSI handle not verified',
                str(member.id)
            ]
            sheets.setRange(startIndex, endIndex, [data], daymar=True)

    def clearParticipant(self, member):

        idCol = 5

        rowIndex = None

        # Check if user already exists in sheet.
        memberIds = sheets.getCol(idCol, daymar=True)
        for index, id in enumerate(memberIds):
            try:
                pId = int(id)
                if member.id == pId:
                    rowIndex = index
                    break
            except ValueError:
                pass

        if rowIndex is not None:
            sheets.deleteRows(rowIndex + 1, daymar=True)

    def clearDaymarSheet(self):

        data = sheets.getAll(daymar=True)
        sheets.deleteRows(2, rowNum=len(data), daymar=True)

    def checkId(ctx):
        id = int(ctx.author.id)
        if id in Constants.DAYMAR_ELEVATED_ACCESS_IDS:
            return True
        else:
            return False

    @commands.command()
    async def set_rsi_handle(self, ctx, *, rsiHandle=''):
        """Sets the RSI handle of the user invoking the command.

        :param rsiHandle: RSI handle
        :type rsiHandle: str

        example:
        !eb.set_rsi_handle myRSIhandle
        """

        if rsiHandle == '':
            await ctx.send(
                'Please specify your RSI handle by typing:\n'
                f'{Constants.CMD_PREFIX}set_rsi_handle <your rsi handle> '
                'without the <>'
            )
            return
        if len(rsiHandle) < 3:
            await ctx.send(
                'RSI handles must be at least 3 characters long. Please enter '
                'a valid RSI handle.'
            )
            return
        if ' ' in rsiHandle:
            await ctx.send(
                'RSI handles cannot contain spaces. Please enter a valid '
                'RSI handle.'
            )
            return

        # Search for user in guild members
        guildMembers = self.client.guildMembers.members
        for m in guildMembers:
            if m.id == ctx.author.id:
                m.rsiHandle = rsiHandle
                break
        else:
            m = event.GuildMember(
                id=ctx.author.id,
                name=ctx.author.name,
                rsiHandle=rsiHandle
            )
            guildMembers.append(m)

        guildMemberData = self.client.guildMembers.json(indent=2)
        utility.saveData(Constants.GUILD_MEMBER_DATA_FILENAME, guildMemberData)

        # TODO: Add to sheet if in daymar event.
        orgEvents = self.client.orgEvents.events
        for e in orgEvents:
            if e.eventType == event.EventType.daymar:
                if e.getParticipant(ctx.author.id) is not None:

                    self.addParticipant(m)
                break

        await ctx.send(
            f'Your RSI handle has been set to: **{rsiHandle}**\n'
            'You may change your registered RSI handle name at any time by '
            'running this command again.'
        )

    @commands.command()
    @commands.check(checkId)
    async def get_csv(self, ctx):

        fileName = 'DaymarSecurity.csv'

        # TODO: Refactor this mess.
        data = sheets.getAll(daymarOverview=True)
        if len(data) < 2:
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


def setup(client):
    client.add_cog(Daymar(client))
