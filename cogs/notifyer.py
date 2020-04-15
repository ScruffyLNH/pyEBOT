import discord # noqa
import asyncio
from constants import Constants
from datetime import datetime
from discord.ext import tasks, commands


class Updater(commands.Cog):
    # TODO: DOCUMENT COG

    def __init__(self, client):
        # TODO: DOCUMENT INIT
        self.client = client

        try:
            self.notificationChecking.start()
        except RuntimeError as e:
            self.client.logger.warning(
                'Exception thrown while attempting to start notification-'
                'checking loop. Error message reads as follows:\n'
                f'{e}\n'
            )

    # Stop running loops if the cog is unloaded.
    def cog_unload(self):
        self.notificationChecking.cancel()

    # Methods

    # Loop
    @tasks.loop(seconds=11)
    async def notificationChecking(self):

    @updateChecking.before_loop
    async def before_updateChecking(self):

        print('Notification-checking loop is waiting for client to get ready.')
        await self.client.wait_until_ready()
        await asyncio.sleep(0.6)
        print('Notification-checking loop has started.')


def setup(client):
    client.add_cog(Notifyer(client))
