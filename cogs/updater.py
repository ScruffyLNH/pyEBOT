import discord # noqa
import asyncio
from discord.ext import tasks, commands


class Updater(commands.Cog):
    # TODO: DOCUMENT COG

    def __init__(self, client):
        # TODO: DOCUMENT INIT
        self.client = client

        try:
            self.updateChecking.start()
        except RuntimeError as e:
            print(e)

    def cog_unload(self):

        self.updateChecking.cancel()

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
