import discord # noqa
import managedMessages
from constants import Constants
from discord.ext import tasks, commands

# TODO: Rearrange and group methods, coroutines, events, commands etc.


class ChannelModerator(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Checks
    def isAdmin(self, ctx):
        boolean = False
        if ctx.author.id == Constants.ADMIN_ID:
            boolean = True
        return boolean

    async def moveMessage(self, message):

        chnl = self.client.get_channel(685608763901739011)  # TODO: Refactor
        string = f"{message.author.mention} says:\n" + message.content
        botMessage = await chnl.send(string)
        await message.delete()
        str1 = (
            "To keep the event channel clean, "
            "your message has been moved to event-discussion. "
            "To delete your message type !delete in "
            )
        str2 = chnl.mention
        str3 = " channel."
        await message.channel.send(str1 + str2 + str3, delete_after=20)

        return botMessage

    @commands.command()
    async def delete(self, ctx):
        # Remove the users command input in discord (!delete)
        await ctx.message.delete()
        notFoundString = (
            'Cannot find any messages from '
            f'{ctx.author.display_name}'
        )
        for commentor in self.client.managedMessages.commentors:
            if ctx.author.id == commentor.id:
                msg = commentor.removeMessage
                if msg:
                    # Get the event-discussion channel
                    channel = self.client.get_channel(685608763901739011)  # TODO: Refactor
                    discordMsg = await channel.fetch_message(msg.id)
                    await discordMsg.delete()
                    if msg.last:
                        self.client.managedMessages.removeCommentor(commentor)
                else:
                    await ctx.channel.send(notFoundString, delete_after=10.0)
                break
        else:
            await ctx.channel.send(notFoundString, delete_after=10.0)

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
        if message.channel.id == Constants.MAIN_CHANNEL_ID:
            if message.guild:
                roles = message.author.roles
                moderatorRole = message.guild.get_role(687134536571945000)  # TODO: refactor
            if message.author.bot:
                pass
            elif message.author.id == Constants.ADMIN_ID:
                pass
            elif moderatorRole in roles:
                # Check if user is overriding auto-removal, by checking the
                # beginning of the string for a specific key-string.
                if message.content.startswith('⚫'):
                    pass
                else:
                    botMsg = await self.moveMessage(message)  # TODO: Add messages to watchlist for moderators as well
                    self.manageMessage(botMsg, message)
                    string = (
                        '\u200b'
                        '\n'
                        'Your message was automatically moved from the main '
                        'event channel. However, you have the autority to '
                        'post messages there.'
                        '\nTo override removal, prepend your message with the '
                        '\\:black_circle: emoji.'
                        '\nExample:'
                        '\n\t:black_circle:Let my message stay!\n\n'
                        'Please keep in mind that the event channel should '
                        'kept as clean as possible, only post messages in '
                        'main event channel if strictly necessary.'
                    )
                    await message.author.send(string, delete_after=120.0)
            else:
                # Move message from user and store users copied message.
                botMsg = await self.moveMessage(message)
                self.manageMessage(botMsg, message)

    def manageMessage(self, botMessage, userMessage):
        # TODO: Docstring

        # Instanciate a message object.
        m = managedMessages.Message(
            id=botMessage.id,
            content=botMessage.content
        )

        # Check if user exists in commentors list
        for commentor in self.client.managedMessages.commentors:
            if commentor.id == userMessage.author.id:
                commentor.addMessage(m)
                break
        else:
            c = managedMessages.Commentor(
                id=userMessage.author.id,
                name=userMessage.author.name
            )
            c.addMessage(m)
            self.client.managedMessages.addCommentor(c)

    def cog_check(self, ctx):
        # Check if channel is event-discussion
        return ctx.channel.id == 685608763901739011  # TODO: Refactor.


def setup(client):
    client.add_cog(ChannelModerator(client))
