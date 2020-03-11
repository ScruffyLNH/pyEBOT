import discord # noqa
from constants import Constants
from discord.ext import tasks, commands


class ChannelModerator(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Checks
    def isAdmin(self, ctx):
        boolean = False
        if ctx.author.id == Constants.ADMIN_ID:
            boolean = True
        return boolean

    @commands.command()
    async def tstNew(self, ctx):
        print(ctx.message)

    # Events
    @commands.Cog.listener()
    async def on_message(self, message):
        # Checks:
        # Message was posted in event-signup channel.
        # Is admin.
        # Is regular user
        # Is not admin, but have permission to post.
        # Not admin, but permission to post and msg begins with #stay#
        # DM: "Your message was automatically moved, however you do have the
        # proper permission to post in event channel. To post message in event
        # channel tag your message with #stay#. Example:
        #   #stay#This is my message that will remain in the event channel."

        # Messages must be stored in a message history object or something
        # if message.channel.id == Constants.MAIN_CHANNEL_ID:
        #     if message.author.id == Constants.ADMIN_ID:
        #         pass
        #     if message.author.top_role > memberRole

        if message.author.id == Constants.ADMIN_ID:
            pass
        elif message.author.bot:
            pass
        elif message.channel.id == Constants.MAIN_CHANNEL_ID:
            chnl = self.client.get_channel(685608763901739011)
            string = f"{message.author.mention} says:\n" + message.content
            await chnl.send(string)
            await message.delete()
            str1 = (
                "To keep the event channel clean, "
                "your message has been moved to event-discussion. "
                "To delete your message type !delete in "
                )
            str2 = chnl.mention
            str3 = " channel."
            await message.channel.send(str1 + str2 + str3, delete_after=20)

    def cog_check(self, ctx):
        ret = False
        if ctx.channel.id == Constants.MAIN_CHANNEL_ID:
            ret = True
        return ret


def setup(client):
    client.add_cog(ChannelModerator(client))
