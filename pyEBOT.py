import discord # noqa
import os
import event
import managedMessages
from pydantic import ValidationError
from utility import loadData
from utility import saveData
from constants import Constants
from discord.ext import commands

# TODO: Decide if I want to use descriptors for agruments in funcs and mehts.
# example def doSomething(arg1: str, arg2: int)

if __name__ == "__main__":
    """Instanciate the discord.py client/bot and load event data if it exists.
    """

    # Instanciate the client and set the command prefix.
    client = commands.Bot(Constants.CMD_PREFIX)

    # Remove the default help command.
    client.remove_command('help')


    # TODO: Refactor code to deserialize data function.
    # Deserialize orgEvent data.
    eventData = loadData('eventData.json')
    # If eventData.json does not exist client.orgEvents will be
    # initialized cleanly.
    if eventData is None:
        print('No event record found. Starting clean.')
        client.orgEvents = event.OrgEvents()
        eventData = client.orgEvents.json(indent=2)
        saveData('eventData.json')
    else:
        try:
            # Attempt to parse persistent data to orgEvents.
            client.orgEvents = event.OrgEvents.parse_raw(
                eventData
            )
            print(
                'Event record successfully parsed.\n'
                f'Found {len(client.orgEvents)} events.'
            )
        except ValidationError as e:
            print('Record was found, but could not be loaded.')
            print(e)
            print('\n Starting clean.')
            # TODO: Clean up wet code.
            client.orgEvents = event.OrgEvents()
            eventData = client.orgEvents.json(indent=2)
            saveData('eventData.json', eventData)

    messageData = loadData('messageData.json')
    if messageData is None:
        print('No message data found.')
        client.managedMessages = managedMessages.ManagedMessages()
        messageData = client.managedMessages.json(indent=2)
        saveData('messageData.json', messageData)
    else:
        try:
            client.managedMessages = managedMessages.ManagedMessages.parse_raw(
                 messageData
            )
            print('Message data successfully parsed.')
        except ValidationError as e:
            print('Message record was found, but could not be loaded.')
            print(e)


# Check functions
def isAdmin(ctx):
    return ctx.author.id == 312381318891700224

# Events
@client.event
async def on_ready():
    print('Ready.')

# Commands
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    client.reload_extension(f'cogs.{extension}')


@client.command()
@commands.check(isAdmin)
async def checkTest(ctx):
    await ctx.send('Yes, you are admin')

# Load cogs
for filename in os.listdir('./cogs'):
    # Files in exclusion list will not be loaded.
    exclusionList = [
        '__init__.py',
        'experimentalCog.py',
        'messageWithoutCommand.py',
        'asyncCog.py']
    if filename not in exclusionList:
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            # TODO: Add try catch?


# TODO: Make sure every assignments are encapsulated somehow to conform to
# sphinx documentation.

# TODO: BEFORE BOT CAN BE INVITED TO OFFICIAL SERVER A NEW TOKEN MUST BE MADE
# Get client token from file.
token = loadData('token.json')
# Run client by passing in token.
client.run(token)
