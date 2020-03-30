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

        # Process each event by instanciating event objects and posting
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
                p = event.Person(id=member.id, name=member.display_name)
                break
        else:
            # Defaults to event manager if another organizer was not found.
            member = self.client.get_user(Constants.EVENT_MANAGER_ID)
            p = event.Person(id=member.id, name=member.display_name)

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

    def determineRoleCreation(self, eventData):
        if (
            eventData['Color Code'] != 0 or
            eventData['Members Only'].upper() == 'YES' or
            eventData['Add Channels'].upper() == 'YES' or
            eventData['Additional Info'] != ''
        ):
            return True
        else:
            return False

    def makeTextOverwrites(self, guild, roles):
        txtOverwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True
            ),
            roles['participant']: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True
            ),
            roles['spectator']: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True
            )
        }
        return txtOverwrites

    def makeVoiceOverwrites(self, guild, roles):
        voiceOverwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True
            ),
            roles['participant']: discord.PermissionOverwrite(
                view_channel=True
            ),
            roles['spectator']: discord.PermissionOverwrite(
                view_channel=False
            )
        }
        return voiceOverwrites

    # Coroutines
    async def assignId(self, orgEvent):
        # TODO: Docstring...

        # Get the discord user object for the event organizer.
        user = self.client.get_user(orgEvent.organizer.id)

        # Make the embed object that will be posted on discor.
        embed = orgEvent.makeEmbed(True, user)

        # Post the message containing the event embed to discord and get the
        # returned message object.
        msg = await self.channel.send(embed=embed)
        print(f'New event added, ID is: {msg.id}')

        # Add registration emoji.
        await msg.add_reaction('✅')

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
        makeRoles = self.determineRoleCreation(eventData)

        # Make a list that will contain the role objects.
        guild = self.client.get_guild(Constants.GUILD_ID)

        roles = {}
        if makeRoles:
            spectatorRole = await guild.create_role(
                name=eventData['Event'] + ' spectator'
            )
            participantRole = await guild.create_role(
                name=eventData['Event'] + ' participant'
            )

            roles['spectator'] = spectatorRole
            roles['participant'] = participantRole

        return roles

    async def createChannels(self, eventData, roles):

        # Get the position of main event category channel
        eventsCategoryChannel = self.client.get_channel(
            Constants.EVENTS_CAT_CHANNEL_ID
        )
        # Get the number of category channels already created from previous
        # events.
        numCategoryChannels = sum(
            len(e.roles) != 0 for e in self.client.orgEvents
        )
        # Set the position to underneath the last crated event category
        # channel, or under Events category if none exist.
        position = (
            eventsCategoryChannel.position + numCategoryChannels + 1
        )

        guild = self.client.get_guild(Constants.GUILD_ID)

        if roles:
            textOverwrites = self.makeTextOverwrites(guild, roles)
            voiceOverwrites = self.makeVoiceOverwrites(guild, roles)

            categoryChannel = await guild.create_category_channel(
                '📌 ' + eventData['Event'],
                overwrites=voiceOverwrites
            )
            await categoryChannel.edit(position=position)
            briefingChannel = await categoryChannel.create_text_channel(
                'Briefing',
                overwrites=textOverwrites
                # TODO: Concider denying permission to send message by adding
                # kwarg to method that makes textOverwrites.
            )
            discussionChannel = await categoryChannel.create_text_channel(
                'Discussion',
                overwrites=textOverwrites
            )
            mainVoiceChannel = await categoryChannel.create_voice_channel(
                'Event',
                overwrites=voiceOverwrites
            )

            channels = {
                'category': categoryChannel,
                'briefing': briefingChannel,
                'discussion': discussionChannel,
                'mainVoice': mainVoiceChannel
            }

            return channels
        else:
            return{}

    async def processData(self, eventData, keys):

        # Get the event organizer
        organizer = self.getEventOrganizer(eventData)

        # Create roles for event
        discordRoles = await self.createRoles(eventData)
        # Convert discordRoles to internal roles for persistant storage.
        if discordRoles:
            roles = {
                'spectator': event.Role(
                    id=discordRoles['spectator'].id,
                    name=discordRoles['spectator'].name
                ),
                'participant': event.Role(
                    id=discordRoles['participant'].id,
                    name=discordRoles['participant'].name
                )
            }
        else:
            roles = {}

        discordChannels = await self.createChannels(eventData, discordRoles)

        # Convert discordChannels to internal channels for persistent storage.
        channels = {}
        for key, channel in discordChannels.items():
            channels[key] = event.Channel(
                id=channel.id,
                name=channel.name,
                channelType=channel.type  #TODO: CHECK THIS ............................................................................
            )

        # Instanciate event object.
        eventInstance = event.Event(
            data=eventData,
            keys=keys,
            organizer=organizer,
            roles=roles,
            channels=channels
        )
        # TODO: Line below should be done in class initialisation, but idk how
        # to do that correctly with pydantic BaseModel classes.
        # Maybe inherit from datamodel instead?
        eventInstance.privateIndication = eventInstance.decodePrivate(
            eventData['Color Code']
        )

        # Assign ID by posting message to discord and saving the returned ID
        # in the event object.
        registeredEvent = await self.assignId(eventInstance)

        # If event contains private information, post the uncensored embed in
        # the newly opened channel.
        # TODO: Make sure that private channel embed is also updated when the
        # main embed is updated.
        if 'briefing' in discordChannels:
            user = self.client.get_user(registeredEvent.organizer.id)
            embed = registeredEvent.makeEmbed(
                False,
                user,
                includeAuthor=False,
                includeFooter=False,
                includePreamble=False,
                includeRollCall=False,
                includeVoiceChnl=False
            )
            channel = discordChannels['briefing']
            privateMsg = await channel.send(embed=embed)

            if eventData['Additional Info'] != '':
                await channel.send(eventData['Additional Info'])
            # TODO: Figure out how to store privateMsg. This is the embed
            # msg sent to private briefing channels. In order to update, the
            # d.py message object id must be stored.

        # Write IDs back to google sheets.
        self.writeIdToSheets(eventInstance)

        # Append the event to the clients list of events
        self.client.orgEvents.append(registeredEvent)

    # async def postToDiscord(self, orgEvent):  # ##############
    #     """Takes eventData objects and posts it to discord generating an id.
    #     Id is then stored in eventData

    #     takes event data object
    #     """
    #     user = self.client.get_user(Constants.EVENT_MANAGER_ID)
    #     if orgEvent.organizer:
    #         user = self.client.get_user(orgEvent.organizer.id)

    #     embed = orgEvent.makeEmbed(True, user)
    #     msg = await self.channel.send(embed=embed)
    #     print(f'New event added, ID is: {msg.id}')

    #     # Set the id of the event to the message id in discord.
    #     orgEvent.id = msg.id

    # async def instanciateRoles(self, roleNames, eventObject):
    #     """Creates a new discord role. The coroutines generates a role object
    #     and puts it in the passed in eventObject.

    #     :param roleName: Name of the role.
    #     :type roleName: string
    #     :param eventObject: Instance of Event class for which the role is made.
    #     :type eventObject: Event
    #     """
    #     guild = self.client.get_guild(Constants.GUILD_ID)

    #     # TODO: Check if role already exists.

    #     roles = []
    #     for roleName in roleNames:
    #         discordRole = await guild.create_role(name=roleName)
    #         r = event.Role(discordRole.name, discordRole.id)
    #         roles.append(r)
    #     eventObject.roles = roles

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
        authDenied = False  # Track if last authentication attempt failed.
        for attempt in range(5):
            try:
                status = int(sheets.getCell(*Constants.CELL_INDEX))
                if authDenied:
                    print('Reauthentication successful.')
                authDenied = False
            except gspread.exceptions.APIError:
                """ Access token expires after 1 hour. The gspread client needs
                to refresh the access token.
                """
                print('Authentication expired, attempting reauthentication.')
                authDenied = True
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
