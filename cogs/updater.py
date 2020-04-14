import discord # noqa
import asyncio
import copy
from constants import Constants
from datetime import datetime
from discord.ext import tasks, commands


class Updater(commands.Cog):
    # TODO: DOCUMENT COG

    def __init__(self, client):
        # TODO: DOCUMENT INIT
        self.client = client
        self.prevOrgEvents = copy.deepcopy(self.client.orgEvents)

        try:
            self.updateChecking.start()
        except RuntimeError as e:
            self.client.logger.warning(
                'Exception thrown while attempting to start update-'
                'checking loop. Error message reads as follows:\n'
                f'{e}\n'
            )

    # Stop running loops if the cog is unloaded.
    def cog_unload(self):

        self.updateChecking.cancel()

    # Methods
    def checkForChanges(self):
        """Checks for differences between last event update and
        the clients events

        Returns the event for which the change took place,
        Ignores changes to the header message stating the
        time until event as that is handled by another loop.
        """

        pass

    async def updateEmbed(self, event):

        channel = self.client.get_channel(Constants.MAIN_CHANNEL_ID)
        msg = await channel.fetch_message(event.id)

        # Get the discord user object for the event organizer.
        user = self.client.get_user(event.organizer.id)

        embed = event.makeEmbed(True, user)

        await msg.edit(embed=embed)

        event.lastUpdate = datetime.utcnow()

        # Update previous events
        for oldEvent in self.prevOrgEvents.events:
            if oldEvent.id == event.id:
                index = self.prevOrgEvents.events.index(oldEvent)
                self.prevOrgEvents.events[index] = copy.deepcopy(event)
                break
        else:
            self.prevOrgEvents.events.append(event)

    @tasks.loop(seconds=13)
    async def updateChecking(self):

        # Make a copy of the up to date events list to check witch are tracked.
        # List items will be removed as they are found leaving a list of
        # untracked events.
        remainingEvents = copy.deepcopy(self.client.orgEvents.events)

        matchedEvents = []
        for event in self.prevOrgEvents.events:

            # Find matching event from the updated events by comparing ids.
            # eventMatch will be None if match was not found.
            eventMatch = next(
                (e for e in self.client.orgEvents.events if e.id == event.id),
                None
            )

            # Remove found events from remainingEvents
            [remainingEvents.remove(e) for e in remainingEvents
             if e.id == event.id]

            if eventMatch is None:
                # Remove the old event if matching event was not found.
                self.prevOrgEvents.events.remove(event)
            else:

                matchedEvent = {
                    'old': event,  # .makeEmbed(True, event.organizer.id),
                    'new': eventMatch  # .makeEmbed(True, eventMatch.organizer.id)
                }
                matchedEvents.append(matchedEvent)

        # Add the untracked events to tracking list.
        [self.prevOrgEvents.events.append(e) for e in remainingEvents]

        # Run through all event matches and update embed if required.
        for eventMatch in matchedEvents:

            # Create bool to determine if embed should be updated.
            # any check discovering update is needed will set update to True.
            update = False

            # Get the number of hours since last update.
            hoursSinceUpdate = (
                datetime.utcnow() - eventMatch['old'].lastUpdate
            ).total_seconds() / 3600.0

            # If last update was longer than 2 hours ago event will be updated.
            if hoursSinceUpdate > 2.0:
                update = True

            oldUser = self.client.get_user(eventMatch['old'].organizer.id)
            newUser = self.client.get_user(eventMatch['new'].organizer.id)
            # Make new and old embeds for comparison.
            oldEmbed = eventMatch['old'].makeEmbed(True, oldUser)
            newEmbed = eventMatch['new'].makeEmbed(True, newUser)

            # Check if description has changed.
            if oldEmbed.description != newEmbed.description:
                update = True

            # Check if footer has changed. (Means change in participants.)
            if oldEmbed.footer.text != newEmbed.footer.text:
                update = True

            if update:
                await self.client.loop.create_task(
                    self.updateEmbed(eventMatch['new'])
                )

    @updateChecking.before_loop
    async def before_updateChecking(self):

        print('Update-checking loop is waiting for client to get ready.')
        await self.client.wait_until_ready()
        await asyncio.sleep(0.6)
        print('Update-checking loop has started.')


def setup(client):
    client.add_cog(Updater(client))
