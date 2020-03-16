import discord # noqa
import sheets
import asyncio
import event
import gspread
from datetime import datetime
from constants import Constants
from discord.ext import tasks, commands


class EventCog(commands.Cog):
    """Cog responsible for posting events to discord. Event data is read from
    google sheets. Inherits from commands.Cog # TODO: improve this docstring
    """
    def __init__(self, client):
        # TODO: Document this method.
        self.client = client

        # TODO: Figure out how to close Loop in unit test, instead of catching
        # the exception.
        try:
            self.checkSheet.start()
        except RuntimeError as e:
            print(e)

    def cog_unload(self):

        # Cancel periodic tasks.
        self.checkSheet.cancel()
        # TODO: remeber to check if more loops must be closed.

    # Methods
    def connectToChannel(self, channelId):
        self.channel = self.client.get_channel(channelId)
        print(f'Connected to channel: {self.channel}')

    async def updateDiscord(self):
        # TODO: Document this function.

        sheetData = sheets.getAll()
        # Get a list of values from the header row in GS. Theese values will
        # be the keys used in sheetData dictionary.
        sheetKeys = sheets.getRow(1)

        # Parse data from google sheets to event data.
        parsedData = self.parseEventData(sheetData)

        # Process each event by instanciation event objects and posting
        # event messages to discord.
        for eventData in parsedData:
            await self.client.loop.create_task(
                self.processData(eventData, sheetKeys)
            )

        # TODO: save to client
        # TODO: Serialize client events orgEvents.

    # Methods
    def parseEventData(self, eventData):
        # TODO: docstring...

        # Convert the dates from string to datetime objects
        eventData = self.convertDates(eventData, 'Date Time', 'Deadline')

        # Filter out events that already exist. (Existing eventswill have an
        # id.)
        unregisteredEvents = self.checkId(eventData)

        # Sort the new events from date.
        sortedEvents = self.sortEvents(unregisteredEvents)

        return sortedEvents

    def writeIdToSheets(self, eventObject):
        # TODO: docstring...

        # Convert large number to string to prevent google sheets from flooring
        # integers 3 least significant digits.
        id = str(eventObject.id)
        index = eventObject.data['idIndex']
        sheets.setCell(*index, id)

    def instanciateEvent(self, eventData, keys, organizer, roles):
        # TODO: Make docstring...

        orgEvent = event.Event(
            None, eventData, keys, organizer, roles, [], []
        )

        return orgEvent

    def getEventOrganizer(self, eventData):
        """Gets the event organizer from all members in discord server.

        :param eventDatas: Event data from google sheets.
        :type eventDatas: dictionary
        :return: Event organizer object
        :rtype: Person
        """

        # Get all people in guild.
        members = self.client.get_guild(Constants.GUILD_ID).members

        # Check if the organizer exists in the member list.
        for member in members:
            if eventData['Organizer'] == member.display_name:
                p = event.Person(member.id, member.display_name)
                break
        else:
            # Defaults to event manager if another organizer was not found.
            member = self.client.get_user(Constants.EVENT_MANAGER_ID)
            p = event.Person(member.id, member.display_name)

        return p

    def sortEvents(self, events):
        # TODO: Docstring...

        if events is not None:
            sortedEvents = sorted(
                events, key=lambda d: d['Date Time']
            )
            return sortedEvents
        else:
            return []

    def convertDates(self, sheetData, *keys):
        """Converts dates from the format used in google sheets to datetime
        python objects.

        :param sheetData: Event data from google sheets.
        :type sheetData: List of dictionary
        :param *keys: The keys in dict where the value should be converted.
        :type *keys: String (arbitrary number of arguments)
        :return: Converted event data. If a valid date was not found the value
        will be an empty string.
        :rtype: List of dictionary
        """
        for i in range(len(sheetData)):  # TODO: 💩
            if sheetData is not None:
                for key in keys:
                    try:
                        sheetData[i][key] = datetime.strptime(
                            sheetData[i][key], Constants.DT_SHEET_PARSE
                        )
                    # datetime.strptime raises value error if conversion fails.
                    except ValueError:
                        sheetData[i][key] = ''
        return sheetData

    def checkId(self, sheetData):
        """Checks if an ID has been assigned to each event entry. If not the
        event entries will be saved along with the entries ID index in a dict.
        Note that the index is based from 1 rather than 0.

        :param sheetData: Event data gathered from google sheets.
        :type sheetData: List of dictionary
        :return: Processed event data and ID indices.
        :rtype: List of dictionary
        """

        # Make an empty list to store unregistered events.
        newEvents = []

        for i in range(len(sheetData)):
            # TODO: Refactor the way dict keys are used, Maybe all keys can be
            # automotically put in as props in a class so it can be accessed
            # like this Keys.id?
            if sheetData[i]['Id'] == '':
                # index is where the ID will be filled in. (2nd col in g.shts.)
                # Google sheets rows are not zero-indexed, and the first row is
                # used for dictionary keys, therefore 2 is added to row index.
                index = (i + 2, 2)
                eventEntry = sheetData[i]
                eventEntry['idIndex'] = index
                newEvents.append(eventEntry)

        return newEvents

    # Coroutines
    async def assignId(self, orgEvent):
        # TODO: Docstring...

        # Get the discord user object for the event organizer. Defaults to
        # event manager if no other organizer is found.
        user = self.client.get_user(Constants.EVENT_MANAGER_ID)
        if orgEvent.organizer:
            user = self.client.get_user(orgEvent.organizer.id)

        # Make the embed object that will be posted on discor.
        embed = orgEvent.makeEmbed(True, user)

        # Post the message containing the event embed to discord and get the
        # returned message object.
        msg = await self.channel.send(embed=embed)
        print(f'New event added, ID is: {msg.id}')

        # Set the id of the event to the message id in discord.
        orgEvent.id = msg.id

        return orgEvent

    async def createRoles(self, eventData):
        """Creates roles for private events, or events that contains classified
        information.

        :param orgEvents: Event objects containing data for each event.
        :type orgEvents: List of Event
        """

        # Determine if custom roles are required for event.
        # Check if event contains private info by checking color code.
        if eventData['Color Code'] != '0':
            makeRoles = True
        elif eventData['Channel'] != '':
            # If event has a custom channel name, roles should be created.
            makeRoles = True
        else:
            makeRoles = False

        # Make a list of rolenames.
        roleNames = []
        if makeRoles:
            roleNames.append(eventData['Event'] + ' participant')
            roleNames.append(eventData['Event'] + ' viewer')

        # TODO: Check if role already exists. (although it shoulden't)

        # Make a list that will contain the role objects.
        roles = []
        guild = self.client.get_guild(Constants.GUILD_ID)
        for roleName in roleNames:
            discordRole = await guild.create_role(name=roleName)
            r = event.Role(discordRole.name, discordRole.id)
            roles.append(r)

        return roles

    async def createChannels(self, eventData, roles):
        # TODO: Refactor this mess
        if eventData['Channel'] != '':
            txtChannelName = '📌' + eventData['Channel'] + '-info'
            voiceChannelName = eventData['Channel']
        else:
            txtChannelName = '📌' + eventData['Event'] + '-info'
            voiceChannelName = eventData['Event']

        categoryChannel = self.client.get_channel(
            Constants.EVENTS_CAT_CHANNEL_ID
        )
        guild = self.client.get_guild(Constants.GUILD_ID)
        if roles:
            participantRole = guild.get_role(roles[0].id)
            viewerRole = guild.get_role(roles[1].id)
            txtOverwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    read_messages=False
                    ),
                guild.me: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                    ),
                participantRole: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                    ),
                viewerRole: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                    )
            }
            voiceOverwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    read_messages=False  # TODO: Upgrade discord.py to 1.3 and use view_channel
                ),
                participantRole: discord.PermissionOverwrite(
                    read_messages=True
                ),
                viewerRole: discord.PermissionOverwrite(
                    read_messages=False
                )
            }
            channels = []
            txt_chnl = await categoryChannel.create_text_channel(
                txtChannelName,
                overwrites=txtOverwrites
            )
            voice_chnl = await categoryChannel.create_voice_channel(
                voiceChannelName,
                overwrites=voiceOverwrites
            )
            channels.append(txt_chnl)
            channels.append(voice_chnl)
            return channels

    async def processData(self, eventData, keys):

        # Get the event organizer
        organizer = self.getEventOrganizer(eventData)

        # Create roles for event
        roles = await self.createRoles(eventData)

        channels = await self.createChannels(eventData, roles)

        # Instanciate event object.
        eventInstance = self.instanciateEvent(
            eventData,
            keys,
            organizer,
            roles)

        # Assign ID by posting message to discord and saving the returned ID
        # in the event object.
        registeredEvent = await self.assignId(eventInstance)

        # Write IDs back to google sheets.
        self.writeIdToSheets(eventInstance)

        # Append the event to the clients list of events
        self.client.orgEvents.append(registeredEvent)

    async def postToDiscord(self, orgEvent):  # ##############
        """Takes eventData objects and posts it to discord generating an id.
        Id is then stored in eventData

        takes event data object
        """
        user = self.client.get_user(Constants.EVENT_MANAGER_ID)
        if orgEvent.organizer:
            user = self.client.get_user(orgEvent.organizer.id)

        embed = orgEvent.makeEmbed(True, user)
        msg = await self.channel.send(embed=embed)
        print(f'New event added, ID is: {msg.id}')

        # Set the id of the event to the message id in discord.
        orgEvent.id = msg.id

    async def instanciateRoles(self, roleNames, eventObject):
        """Creates a new discord role. The coroutines generates a role object
        and puts it in the passed in eventObject.

        :param roleName: Name of the role.
        :type roleName: string
        :param eventObject: Instance of Event class for which the role is made.
        :type eventObject: Event
        """
        guild = self.client.get_guild(Constants.GUILD_ID)

        # TODO: Check if role already exists.

        roles = []
        for roleName in roleNames:
            discordRole = await guild.create_role(name=roleName)
            r = event.Role(discordRole.name, discordRole.id)
            roles.append(r)
        eventObject.roles = roles

    # Loops
    @tasks.loop(seconds=5)
    async def checkSheet(self):
        """
        Check the status of events in the connected google sheet.
        The staus is read by getting the value of a specified cell.
        If the cell value is 0, the sheet is up to date with discord.
        If the cell value is 1, data is being processed on the sheet side.
        If the cell value is 2, discord should be updated. Message ids from
        discord for each event will be stored in sheet. Also the cell value
        will be reset to 0 if discord was successfully updated.
        """

        # Attempt to read cell.
        for attempt in range(5):
            try:
                status = int(sheets.getCell(*Constants.CELL_INDEX))
            except gspread.exceptions.APIError as e:
                print(e)
                """ Access token expires after 1 hour. The gspread client needs
                to refresh the access token.
                """
                sheets.refreshAuth()
            else:
                break

        if status == 2:
            self.client.loop.create_task(
            self.updateDiscord()
            )
            status = 0
            sheets.setCell(*Constants.CELL_INDEX, status)

    @checkSheet.before_loop
    async def before_checkSheet(self):
        """Make sure client is ready before checkSheet loop runs.
        """
        print('Sheet-checking loop is waiting for client to get ready.')
        await self.client.wait_until_ready()
        await asyncio.sleep(0.5)
        print('Sheet-checking loop has started.')

        self.connectToChannel(Constants.MAIN_CHANNEL_ID)


def setup(client):
    client.add_cog(EventCog(client))
