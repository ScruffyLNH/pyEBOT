import discord # noqa
from discord.ext import commands


class eventConfig(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command()
    async def pineling(self, ctx):
        await ctx.send('Pong!')

    # Command check for entire cog.
    def cog_check(self, ctx):
        try:
            roleIds = [r.id for r in ctx.author.roles]
            if self.client.config.eventManagerRoleId in roleIds:
                return True
            else:
                return False
        except AttributeError:
            return False


def setup(client):
    client.add_cog(eventConfig(client))
