"""import discord # noqa
import asyncio
from discord.ext import tasks, commands


class AsyncCog(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.channelId = 665424669871964170
        self.loop = asyncio.get_event_loop()
        if self.client.is_ready():
            self.connectToChannel(self.channelId)

    @commands.Cog.listener()
    async def on_ready(self):
        self.connectToChannel(self.channelId)

    def cog_unload(self):
        pass
        # self.backroundtasks.cancel()

    def connectToChannel(self, channelId):
        self.channel = self.client.get_channel(channelId)
        print(f'Connecting to channel: {self.channel}')

    async def sayHi(self):
        print('Hi!')
        # await self.channel.send('Hi!')
        return self.channel.last_message_id

    async def taskGenerator(self):
        for i in range(4):
            asyncio.ensure_future(self.sayHi())

    async def main(self, coros):
        for futures in asyncio.as_completed(coros):
            print(await(futures))

    @commands.command()
    async def runTest(self, ctx):
        loop = asyncio.get_event_loop()
        try:
            coros = [self.sayHi() for i in range(4)]
            loop.run_until_complete(self.main(coros))
            print('Tasks completed')
        except Exception as e:
            pass
        finally:
            loop.close


def setup(client):
    client.add_cog(AsyncCog(client))

# self.loop.run_until_complete(self.makeTasks)
"""
