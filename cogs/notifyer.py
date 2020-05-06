import discord # noqa
import asyncio
import utility
import event
from constants import Constants
from datetime import datetime, timedelta
from discord.ext import tasks, commands


class Notifyer(commands.Cog):
    # TODO: DOCUMENT COG

    def __init__(self, client):
        # TODO: DOCUMENT INIT
        self.client = client

        # TODO: Need to track the following in some sort of structure.
        # event id, time until event, has 5 min msg been sent?, has now message been sent?

        try:
            self.participantsNotifyer.start()
            self.eventNotifyer.start()
            self.managerNotifyer.start()
        except RuntimeError as e:
            self.client.logger.warning(
                'Exception thrown while attempting to start a notification '
                'loop. Error message reads as follows:\n'
                f'{e}\n'
            )

    # Stop running loops if the cog is unloaded.
    def cog_unload(self):
        self.participantsNotifyer.cancel()
        self.eventNotifyer.cancel()
        self.managerNotifyer.cancel()

    # Methods
    def timeDeltaToHoursMins(self, td):  # TODO: Move to utility?
        """Converts datetime.timedelta object to remaining hours and minutes.

        :param td: timedelta object to convert.
        :type td: timedelta
        :return: hours and minutes in a tuple.
        :rtype: tup(int, int)
        """

        if td.total_seconds() > 0:
            hours = td.seconds // 3600
            minutes = td.seconds // 60 - hours * 60
        else:
            hours = td.total_seconds() // 3600
            minutes = td.total_seconds() // 60 + hours * 60

        return(hours, minutes)

    def formatTimeRemaining(self, time):
        """Formats the difference between now and input time into
        days or hours and minutes depending on span between now and inout time.

        :param time: Input time.
        :type time: datetime
        :return: Human readable formatted time difference.
        :rtype: string
        """
        delta = time - datetime.utcnow()
        # Check the time of day and add an extra day if now time-of-day
        # is greater than input time-of-day.
        if(
            datetime.utcnow().time() > time.time() and not
            datetime.utcnow() > time
        ):
            delta += timedelta(days=1)
        days = delta.days
        hours, minutes = self.timeDeltaToHoursMins(delta)

        if days == 1:
            timeRemainingString = 'starts in 1 day'
        elif days > 1:
            timeRemainingString = f'starts in {delta.days} days'
        else:
            timeRemainingString = f'starts in {hours} hour(s), {minutes} min'

        if delta.total_seconds() < 5:
            timeRemainingString = 'has started'

        return timeRemainingString

    def makeMentionString(self, alert, participants=[], roles=[]):
        # Mention types are:
        # none = 0
        # everyone = 1
        # participants = 2
        # participantsNotInVc = 3

        m = alert.mentions
        if m == event.Mentions.none:
            return ''
        elif m == event.Mentions.everyone:
            return '@everyone'
        elif m == event.Mentions.participants:
            if roles:
                roleMentions = [f'<@&{role.id}>' for role in roles]
                mentions = ', '.join(roleMentions)
            else:
                pMentions = [f'<@{p.id}>' for p in participants]
                mentions = ', '.join(pMentions)
        elif m == event.Mentions.participantsNotInVc:
            # Get the events voice channel and aquire all members from it.
            voiceChannel = self.client.get_channel(alert.voiceChannelId)
            vcMembers = voiceChannel.members
            # Make a list of id for all members in voice channel.
            idsInVc = [m.id for m in vcMembers]
            # Remove voice channel member ids from event participant to be
            # able to only mention participants not in voice channel.
            idsLeft = [p.id for p in participants if p.id not in idsInVc]
            pMentions = [f'<@{id}>' for id in idsLeft]
            mentions = ', '.join(pMentions)

        return mentions

    def handleEventNotification(self, alert, eventTime):  # TODO: Move eventTime to alert?

        timeRemainingString = self.formatTimeRemaining(eventTime)
        msgList = []
        msgList.append(self.makeMentionString(alert))
        msgList.append(
            f'\n {alert.eventName} {timeRemainingString}.\n'
            f'Sign up in <#{self.client.config.signupChannelId}>'
        )
        msg = ''.join(msgList)

        self.client.loop.create_task(
            self.sendNotification(msg, alert.textChannelId)
        )

    def handleParticipantNotification(
        self,
        alert,
        eventTime,
        participants,
        roles=[]
    ):

        timeRemainingString = self.formatTimeRemaining(eventTime)

        msgList = []
        msgList.append(
            f'{alert.eventName} {timeRemainingString}.\n'
        )

        mentions = self.makeMentionString(alert, participants, roles)
        msgList.append(mentions)

        msg = ''.join(msgList)
        self.client.loop.create_task(
            self.sendNotification(msg, alert.textChannelId)
        )

    async def sendNotification(self, message, channelId):
        """Sends notification message to channel with specified channel id.

        :param message: Message to be sent.
        :type message: string
        :param channelId: ID of the channel where message should be sent.
        :type channelId: int
        """
        guild = self.client.get_guild(self.client.config.guildId)
        channel = guild.get_channel(channelId)
        await channel.send(message)

    # Loops
    @tasks.loop(seconds=3)
    async def participantsNotifyer(self):
        for orgEvent in self.client.orgEvents.events:
            # Alerts to be removed.
            discardAlerts = []
            for alert in orgEvent.notifications.participantAlerts:
                if(
                    datetime.utcnow() > alert.time and
                    datetime.utcnow() - alert.margin < alert.time
                ):
                    roles = []
                    if orgEvent.roles:
                        roles.append(orgEvent.roles['participant'])

                    self.handleParticipantNotification(
                        alert,
                        orgEvent.dateAndTime,
                        orgEvent.participants,
                        roles
                    )

                if datetime.utcnow() > alert.time:
                    discardAlerts.append(alert)

            for alert in discardAlerts:
                orgEvent.notifications.participantAlerts.remove(alert)

            if discardAlerts:
                utility.saveData(
                    Constants.EVENT_DATA_FILENAME,
                    self.client.orgEvents.json(indent=2)
                )

    @participantsNotifyer.before_loop
    async def before_participantsNotifyer(self):

        print('Participants notifyer loop is waiting for client to get ready.')
        await self.client.wait_until_ready()
        await asyncio.sleep(0.6)
        print('Notification-checking loop has started.')

    @tasks.loop(seconds=83)
    async def eventNotifyer(self):
        for orgEvent in self.client.orgEvents.events:
            # Indices of alerts to be removed.
            discardAlerts = []
            for alert in orgEvent.notifications.generalAlerts:
                if(
                    datetime.utcnow() > alert.time and
                    datetime.utcnow() - alert.margin < alert.time
                ):
                    self.handleEventNotification(alert, orgEvent.dateAndTime)

                if datetime.utcnow() > alert.time:
                    discardAlerts.append(alert)

            for alert in discardAlerts:
                orgEvent.notifications.generalAlerts.remove(alert)

            if discardAlerts:
                utility.saveData(
                    Constants.EVENT_DATA_FILENAME,
                    self.client.orgEvents.json(indent=2)
                )

    @eventNotifyer.before_loop
    async def before_eventNotifyer(self):

        print('Event notifyer loop is waiting for client to get ready.')
        await self.client.wait_until_ready()
        await asyncio.sleep(0.6)
        print('Event notifyer loop has started.')

    @tasks.loop(seconds=97)
    async def managerNotifyer(self):
        pass

    @managerNotifyer.before_loop
    async def before_managerNotifyer(self):

        print('Manager notifyer loop is waiting for client to get ready.')
        await self.client.wait_until_ready()
        await asyncio.sleep(0.6)
        print('Manager notifyer loop has started.')


def setup(client):
    client.add_cog(Notifyer(client))
