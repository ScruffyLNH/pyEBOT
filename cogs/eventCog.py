import discord # noqa
import sheets
import asyncio
import os
import pickle
import cogData as cd
from discord.ext import tasks, commands


class EventCog(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.updateCellIndices = (2, 17)
        self.eventDataList = []
        # Obtain channel ID by using devTools (!load devTools !getChannelId)
        self.mainEventChannel = 665424669871964170
        if self.client.is_ready():
            self.connectToChannel(self.channelId)


def loadData(fileName):
    try:
        with open('eventData.pkl') as dataFile:
            obj = pickle.load(dataFile)
            print(obj)
    except FileNotFoundError as e:
        print(e)


def setup(client):
    client.add_cog(EventCog(client))
