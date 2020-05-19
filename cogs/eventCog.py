import discord # noqa
import sheets
import asyncio
import event
import gspread
import utility
from datetime import datetime, timedelta
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
            self.client.logger.warning(
                'Exception thrown while starting sheet checking loop. '
                'Error message reads as follows:\n'
                f'{e}\n'
            )

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

    def getEventType(self, eventData):

        for eType in event.EventType:
            if eventData['Event Type'] == eType.name:
                eventType = getattr(event.EventType, eType.name)
                return eventType
        return None

    def getEventOrganizer(self, eventData):
        """Gets the event organizer from all members in discord server.

        :param eventDatas: Event data from google sheets.
        :type eventDatas: dictionary
        :return: Event organizer object
        :rtype: Person
        """

        # Get all people in guild.
        members = self.client.get_guild(self.client.config.guildId).members

        # Check if the organizer exists in the member list.
        for member in members:
            if eventData['Organizer'] == member.display_name:
                p = event.Person(id=member.id, name=member.display_name)
                break
        else:
            # Defaults to event manager if another organizer was not found.
            member = self.client.get_user(self.client.config.eventManagerId)
            p = event.Person(id=member.id, name=member.display_name)

        return p

    def sortEvents(self, events):
        # TODO: Docstring...

        # Add temporary key that holds the converted date as datetime obj.
        for e in events:
            date = self.convertDates(e, 'Date Time')[0]
            if date is None:
                date = datetime.utcnow()
            e['formattedDt'] = date

        # TODO: Now that culprit has been found try to revert back to lambda
        # arbitrary evaluated value

        if events is not None:
            sortedEvents = sorted(
                events, key=lambda d: d['formattedDt']
            )
            # Remove temporary key used for sorting.
            [e.pop('formattedDt') for e in sortedEvents]
            return sortedEvents
        else:
            return []

    def convertDates(self, sheetData, *keys):
        """Converts dates from the format used in google sheets to datetime
        python objects. Returns None if date could not be parsed.

        :param sheetData: Event data from google sheets.
        :type sheetData: List[dictionary]
        :param *keys: The keys in dict where the value should be converted.
        :type *keys: String (arbitrary number of arguments)
        :return: Converted event data. If a valid date was not found the value
        will be None.
        :rtype: List[dictionary]
        """

        # TODO: Catch exception and drop event if data could not be parsed.
        dates = []
        # Convert values of specified keys and append to dates list using list
        # comprehension.

        for key in keys:
            try:
                dates.append(
                    datetime.strptime(sheetData[key], Constants.DT_SHEET_PARSE)
                )
            except ValueError:
                dates.append(None)

        # for i in range(len(sheetData)):  # TODO: 💩
        #     if sheetData is not None:
        #         for key in keys:
        #             try:
        #                 sheetData[i][key] = datetime.strptime(
        #                     sheetData[i][key], Constants.DT_SHEET_PARSE
        #                 )
        #             # datetime.strptime raises value error if conversion fails.
        #             except ValueError:
        #                 sheetData[i][key] = ''

        # Return items in dates list as a tuple.
        return tuple(dates)

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

    def makeAlerts(
        self,
        eventName,
        dateAndTime,
        deadline,
        channels,
        general=False,
        deadlineAlerts=False,
        participant=False
    ):
        """Create alerts for notifying members and event participants
        of event info and updates.

        :param dateAndTime: Event start date.
        :type dateAndTime: datetime
        :param deadline: Deadline for event signup.
        :type deadline: datetime
        :param channels: Created channels for the event.
        :type channels: List[event.Channel]
        :param general: True if making general alerts, defaults to False
        :type general: bool, optional
        :param participant: True if making alerts for participants,
        defaults to False
        :type participant: bool, optional
        """
        # TODO: Refactor. Break down to smaller methods.
        # TODO: Add time to deadline if exists somehow. Prob add fld to Alert.

        # Create an empty list to hold alert objects
        alerts = []

        # The default timedeltas for general alerts
        generalTds = [
            timedelta(weeks=2),
            timedelta(weeks=1),
            timedelta(days=2),
            timedelta(days=1)
        ]
        deadlineTds = [
            timedelta(hours=2),
            timedelta(minutes=10)
        ]
        participantTds = [
            timedelta(hours=2),
            timedelta(minutes=30),
            timedelta(minutes=5),
            timedelta(seconds=2)
        ]

        if deadline is not None:
            # Add generalTds from after deadline to participantTds
            def after(td): return dateAndTime - td >= deadline
            extra = list(filter(after, generalTds))
            participantTds = sorted(participantTds + extra, reverse=True)

            # Remove generalTds after deadline by only keeping the before.
            def before(td): return dateAndTime - td < deadline
            generalTds = list(filter(before, generalTds))

            # Add timedelta between deadline and event start to deadlineTds
            delta = dateAndTime - deadline
            deadlineTds = list(map(lambda d: delta + d, deadlineTds))

        activeTds = []
        if general:
            activeTds.extend(generalTds)
        if deadlineAlerts:
            activeTds.extend(deadlineTds)
        if participant:
            activeTds.extend(participantTds)

        activeTds = sorted(activeTds, reverse=True)
        margin = timedelta(minutes=30) if general else timedelta(seconds=15)

        # Private events will always have channels.
        if channels:
            if general or deadlineAlerts:
                textChannelId = self.client.config.discussionChannelId
            else:
                textChannelId = channels['discussion'].id
            voiceChannelId = channels['mainVoice'].id
        else:
            textChannelId = self.client.config.discussionChannelId
            voiceChannelId = self.client.config.defaultVoiceChannelId

        if participant:
            mention = event.Mentions.participants
        if general or deadlineAlerts:
            mention = event.Mentions.everyone

        for delta in activeTds:
            if delta.total_seconds() // 60 <= 10 and participant:
                mention = event.Mentions.participantsNotInVc

            alert = event.Alert(
                eventName=eventName,
                time=dateAndTime - delta,
                margin=margin,
                mentions=mention,
                textChannelId=textChannelId,
                voiceChannelId=voiceChannelId
            )
            alerts.append(alert)
        """
        if general:
            # TODO: Link timedeltas to config defaults.
            alertTimesBeforeStart = [
                timedelta(weeks=2),
                timedelta(weeks=1),
                timedelta(days=2),
                timedelta(days=1)
                ]

            for delta in alertTimesBeforeStart:
                alert = event.Alert(
                    eventName=eventName,
                    time=dateAndTime - delta,
                    margin=timedelta(minutes=30),
                    mentions=event.Mentions.everyone,
                    textChannelId=self.client.config.discussionChannelId,
                    voiceChannelId=voiceChannelId
                )
                if deadline is not None:
                    if (dateAndTime - delta) < deadline:
                        alerts.append(alert)
                else:
                    alerts.append(alert)

            if deadline is not None:
                deadlineAlert = event.Alert(
                    eventName=eventName,
                    time=deadline - timedelta(hours=2),
                    margin=timedelta(minutes=5),
                    mentions=event.Mentions.everyone,
                    textChannelId=textChannelId,
                    voiceChannelId=voiceChannelId
                )

                alerts.append(deadlineAlert)

        if participant:
            # TODO: Link timedeltas to config defaults.
            alertTimesBeforeStart = [
                timedelta(hours=4),
                timedelta(hours=1),
                timedelta(minutes=30),
                timedelta(minutes=5),
                timedelta(seconds=2)
                ]

            for delta in alertTimesBeforeStart:
                # If time to event is more than 10 min, every participant will
                # be mentioned. Else only participants not in the event voice
                # chat will be mentioned.
                if delta.total_seconds() // 60 > 10:
                    mention = event.Mentions.participants
                else:
                    mention = event.Mentions.participantsNotInVc

                alert = event.Alert(
                    eventName=eventName,
                    time=dateAndTime - delta,
                    margin=timedelta(seconds=15),
                    mentions=mention,
                    textChannelId=textChannelId,
                    voiceChannelId=voiceChannelId
                )
                alerts.append(alert)
            """

        return alerts

    # Coroutines
    async def assignId(self, orgEvent):
        # TODO: Docstring...
        guild = self.client.get_guild(self.client.config.guildId)

        # Get the discord user object for the event organizer.
        user = self.client.get_user(orgEvent.organizer.id)

        # Get the name of the main voice channel.
        vc = guild.get_channel(self.client.config.defaultVoiceChannelId)

        # Make the embed object that will be posted on discor.
        embed = orgEvent.makeEmbed(True, user, mainVoiceName=vc.name)

        # Post the message containing the event embed to discord and get the
        # returned message object.
        msg = await self.channel.send(embed=embed)
        self.client.logger.info(
            f'New event added, ID is: {msg.id}'
        )

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
        guild = self.client.get_guild(self.client.config.guildId)

        roles = {}
        if makeRoles:
            spectatorRole = await guild.create_role(
                name=eventData['Event'] + ' spectators',
                mentionable=True
            )
            participantRole = await guild.create_role(
                name=eventData['Event'] + ' participants',
                mentionable=True
            )

            roles['spectator'] = spectatorRole
            roles['participant'] = participantRole

        return roles

    async def createChannels(self, eventData, roles, eventType=None):

        if eventType == event.EventType.daymar:
            daymar = True
        else:
            daymar = False

        # Get the position of main event category channel
        eventsCategoryChannel = self.client.get_channel(
            self.client.config.mainCategoryChannelId
        )
        # Get the number of category channels already created from previous
        # events.
        numCategoryChannels = sum(
            len(e.roles) != 0 for e in self.client.orgEvents.events
        )
        # Set the position to underneath the last crated event category
        # channel, or under Events category if none exist.
        position = (
            eventsCategoryChannel.position + numCategoryChannels + 1
        )

        guild = self.client.get_guild(self.client.config.guildId)

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
            mainVoiceName = 'Event' if not daymar else 'DAYMAR MAIN VOICE'
            mainVoiceChannel = await categoryChannel.create_voice_channel(
                mainVoiceName,
                overwrites=voiceOverwrites
            )

            if daymar:
                extraTextChannels = [
                    'daymar-roster',
                    'general-info'
                ]
                extraVoiceChannels = [
                    'Command',
                    'Team 1',
                    'Team 2',
                    'Team 3',
                    'Team 4',
                    'Team 5'
                ]
                for name in extraTextChannels:
                    await categoryChannel.create_text_channel(
                        name,
                        overwrites=textOverwrites
                    )
                for name in extraVoiceChannels:
                    await categoryChannel.create_voice_channel(
                        name,
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
            return {}

    async def getImageUrl(self, eventName):

        # Get the resource channel.
        channel = self.client.get_channel(Constants.IMG_RES_CHANNEL_ID)

        # Get all messages in the event-posters resource channel.
        messages = await channel.history(limit=30).flatten()
        # Get url from message attachment.
        urls = [m.attachments[0].url for m in messages]

        # Create an empty dictionary that will store image names and url links
        # as key, value pairs.
        imageNames = {}
        for url in urls:
            # Split string on '/' and get the last item.
            rawImageName = url.split('/')[-1]
            # Get only the part of the string before the file extension, and
            # convert to upper case.
            imageName = rawImageName.split('.', 1)[0].upper()
            # Replace '_' with ' '.
            imageName = imageName.replace('_', ' ')
            # Append key, value pairs to dictionary
            imageNames.update({imageName: url})

        for key, value in imageNames.items():
            if key == eventName.upper():
                imageUrl = value
                break
        else:
            imageUrl = None

        return imageUrl

    async def processData(self, eventData, keys):  # TODO: Rename? processEventCreation

        # Get the event type.
        eventType = self.getEventType(eventData)

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

        discordChannels = await self.createChannels(
            eventData,
            discordRoles,
            eventType=eventType
        )

        # Convert discordChannels to internal channels for persistent storage.
        channels = {}
        for key, channel in discordChannels.items():
            channels[key] = event.Channel(
                id=channel.id,
                name=channel.name,
                channelType=event.ChannelType(channel.type.value)
            )

        # Convert the dates from string to datetime objects
        dateAndTime, deadline = self.convertDates(
            eventData, 'Date Time', 'Deadline'
        )

        # Get the image url if found in resource channel.
        imageUrl = await self.getImageUrl(eventData['Event'])

        # Create default general alerts list.
        generalAlerts = self.makeAlerts(
            eventData['Event'],
            dateAndTime,
            deadline,
            channels,
            general=True
        )
        strings = ['The following general alerts were created:\n']
        [strings.append(str(a.time) + '\n') for a in generalAlerts]

        self.client.logger.debug(''.join(strings))

        if deadline is not None:
            deadlineAlerts = self.makeAlerts(
                eventData['Event'],
                dateAndTime,
                deadline,
                channels,
                deadlineAlerts=True
            )

            strings = ['The following deadline alerts were created:\n']
            [strings.append(str(a.time) + '\n') for a in deadlineAlerts]

            self.client.logger.debug(''.join(strings))
        else:
            deadlineAlerts = []

        # Create default participant alerts list.
        participantAlerts = self.makeAlerts(
            eventData['Event'],
            dateAndTime,
            deadline,
            channels,
            participant=True
        )
        strings = ['The following participant alerts was created:\n']
        [strings.append(str(a.time) + '\n') for a in participantAlerts]

        self.client.logger.debug(''.join(strings))

        # Create notifications for event.
        notifications = event.Notifications(
            generalAlerts=generalAlerts,
            deadlineAlerts=deadlineAlerts,
            participantAlerts=participantAlerts
        )

        # Instanciate event object.
        eventInstance = event.Event(
            data=eventData,
            eventType=eventType,
            dateAndTime=dateAndTime,
            deadline=deadline,
            keys=keys,
            organizer=organizer,
            imageUrl=imageUrl,
            roles=roles,
            channels=channels,
            lastUpdate=datetime.utcnow(),
            notifications=notifications
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

        # If event is a daymar event the daymar spreadsheet is cleared.
        if eventInstance.eventType == event.EventType.daymar:
            cog = self.client.get_cog('Daymar')
            cog.clearDaymarSheet()

        # Append the event to the clients list of events
        self.client.orgEvents.events.append(registeredEvent)
        utility.saveData(
            Constants.EVENT_DATA_FILENAME, self.client.orgEvents.json(indent=2)
        )

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
                    self.client.logger.info(
                        'Reauthentication successful.'
                    )
                authDenied = False
            except gspread.exceptions.APIError:
                """ Access token expires after 1 hour. The gspread client needs
                to refresh the access token.
                """
                self.client.logger.info(
                    'Authentication expired, attempting reauthentication.'
                )
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

        self.connectToChannel(self.client.config.signupChannelId)


def setup(client):
    client.add_cog(EventCog(client))
