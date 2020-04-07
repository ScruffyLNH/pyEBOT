import discord # noqa
import asyncio
import copy
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
            print(e)

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

    @tasks.loop(seconds=13)
    async def updateChecking(self):

        # Make a list with all event ids from updated events. List items
        # will be removed as they are found leaving a list of untracked ids.
        remainingEventIds = [e.id for e in self.client.orgEvents.events]

        for event in self.prevOrgEvents.events:

            # Find matching event from the updated events by comparing ids.
            eventMatch = next(
                (e for e in self.prevOrgEvents.events if e.id == event), None
            )

            matchedEvents = []
            if eventMatch is None:
                # Destroy the old event if matching event was not found.
                del(event)
            else:
                # Remove found event id from list.
                remainingEventIds.remove(event.id)

                matchedEvent = {
                    'old': event.makeEmbed(True, event.organizer.id),
                    'new': eventMatch.makeEmbed(True, eventMatch.organizer.id)
                }
                matchedEvents.append(matchedEvent)

        for id in remainingEventIds:
            


        # Create a new embed message from data in orgEvents
        # Check if the message is the same as what is in prevOrgEvents
        # If there are changes edit the embed in discord.
        # If diff between lastUpdates is more than 2 hours update the embed in discord.
        # If an update has occured set the prevOrgevent to the orgEvent
        # 

    @updateChecking.before_loop
    async def before_updateChecking(self):

        print('Update-checking loop is waiting for client to get ready.')
        await self.client.wait_until_ready()
        await asyncio.sleep(0.6)
        print('Update-checking loop has started.')


def setup(client):
    client.add_cog(Updater(client))
