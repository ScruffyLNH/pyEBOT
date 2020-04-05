import discord # noqa
import asyncio
from discord.ext import tasks, commands


class Updater(commands.Cog):
    # TODO: DOCUMENT COG

    def __init__(self, client):
        # TODO: DOCUMENT INIT
        self.client = client
        self.prevOrgEvents = self.client.orgEvents

        try:
            self.updateChecking.start()
        except RuntimeError as e:
            print(e)

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

    @tasks.loop(seconds=9)
    async def updateChecking(self):
        pass

    @updateChecking.before_loop
    async def before_updateChecking(self):

        print('Update-checking loop is waiting for client to get ready')
        await self.client.wait_until_ready()
        await asyncio.sleep(0.6)
        print('Update-checking loop has started.')


def setup(client):
    client.add_cog(Updater(client))
