import discord # noqa
import os
import event
import configuration
import managedMessages
import logging
from logging import handlers
from pydantic import ValidationError
from utility import loadData, saveData, checkConfig, sendMessagePackets
from constants import Constants
from discord.ext import commands

# TODO: Decide if I want to use descriptors for agruments in funcs and meths.
# example def doSomething(arg1: str, arg2: int)

# TODO: Add exception to member only requirement for daymar rally if participants are
# in collaborators

# TODO: Check if await fetch_guild can be replaced by using self.client.get_guild

# TODO: Check if self.client.get_channel is used anywhere and replace with guild.get_channel

if __name__ == "__main__":
    """Instanciate the discord.py client/bot and load event data if it exists.
    """

    # Instanciate the client and set the command prefix.
    client = commands.Bot(Constants.CMD_PREFIX)  # TODO: Make it possible to change prefix with cmd.

    # Remove the default help command.
    client.remove_command('help')

    # Setup the logger
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)  # TODO: Set apropriate logging level. (INFO)
    handler = handlers.RotatingFileHandler(
        filename=Constants.LOG_FILENAME,
        mode='a',  # Append mode? #TODO: Verify
        maxBytes=8*1024*1024,  # Max size is 8MB
        backupCount=2,
        encoding='utf-8'
    )
    handler.setFormatter(
        logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    )
    logger.addHandler(handler)
    client.logger = logger

    # Deserialize configuration data.
    configData = loadData(Constants.CONFIG_DATA_FILENAME)
    if configData is None:
        client.logger.info('Config data not found.')
        client.config = configuration.Configuration()
        configData = client.config.json(indent=2)
        saveData(Constants.CONFIG_DATA_FILENAME, configData)
    else:
        try:
            # Attempt to parse persistent config data to config.
            client.config = configuration.Configuration.parse_obj(
                configData
            )
            client.logger.info(
                'Config data successfully parsed.'
            )
        except ValidationError as e:
            client.logger.warning(
                'Exception thrown, error message is as follows:\n'
                f'{e}\n'
                'Config data was found, but could not be loaded. '
                'Starting clean'
            )
            # TODO: Clean up wet code.
            client.config = configuration.Configuration()
            configData = client.config.json(indent=2)
            saveData(Constants.CONFIG_DATA_FILENAME, configData)

    # Deserialize orgEvent data.
    eventData = loadData(Constants.EVENT_DATA_FILENAME)
    # If eventData does not exist client.orgEvents will be
    # initialized cleanly.
    if eventData is None:
        client.logger.info('No event record found. Starting clean.')
        print('No event record found. Starting clean.')
        client.orgEvents = event.OrgEvents()
        eventData = client.orgEvents.json(indent=2)
        saveData(Constants.EVENT_DATA_FILENAME, eventData)
    else:
        try:
            # Attempt to parse persistent data to orgEvents.
            client.orgEvents = event.OrgEvents.parse_obj(
                eventData
            )
            client.logger.info(
                'Event record successfully parsed. '
                f'found {len(client.orgEvents.events)} events.'
            )
            print(
                'Event record successfully parsed.\n'
                f'Found {len(client.orgEvents.events)} events.'
            )
        except ValidationError as e:
            client.logger.warning(
                'Exception thrown, error message is as follows:\n'
                f'{e}\n'
                'Record was found, but could not be loaded. '
                'Starting clean'
            )
            # TODO: Clean up wet code.
            client.orgEvents = event.OrgEvents()
            eventData = client.orgEvents.json(indent=2)
            saveData(Constants.EVENT_DATA_FILENAME, eventData)

    messageData = loadData(Constants.MESSAGE_DATA_FILENAME)
    if messageData is None:
        client.logger.info('No message data found.')
        print('No message data found.')
        client.managedMessages = managedMessages.ManagedMessages()
        messageData = client.managedMessages.json(indent=2)
        saveData(Constants.MESSAGE_DATA_FILENAME, messageData)
    else:
        try:
            client.managedMessages = managedMessages.ManagedMessages.parse_obj(
                 messageData
            )
            client.logger.info('Message data successfully parsed.')
            print('Message data successfully parsed.')
        except ValidationError as e:
            client.logger.warning(
                'Exception was thrown. Error message reads as follows:\n'
                f'{e}\n'
                'Message record was found, but could not be loaded.'
            )
            print('Message record was found, but could not be loaded.')
            print(e)


# Check functions
def isAdmin(ctx):
    return ctx.author.id == client.config.adminId

# Events
@client.event
async def on_ready():
    client.logger.info('on_ready event triggered.')
    print('Ready.')

# Commands
@client.command()  # TODO: Add proper authorization checks.
@commands.check(isAdmin)
async def load(ctx, extension):
    remainingFields = checkConfig(client.config)
    if not remainingFields or extension == 'serverConfig':
        client.load_extension(f'cogs.{extension}')
        await ctx.send('Cog has been loaded.')
    else:
        msg = (
            'Cannot load cog, Please make sure bot has been configured for '
            'this guild. Remaining fields to be configured are as follows:\n'
            + '\n'.join(remainingFields)
        )

        await ctx.send(msg)


@client.command()
@commands.check(isAdmin)
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
@commands.check(isAdmin)
async def loadAll(ctx):
    remainingFields = checkConfig(client.config)
    if not remainingFields:
        for filename in os.listdir('./cogs'):
            exclusionList = [
                '__init__.py',
                'experimentalCog.py',  # TODO: Clean up exclusion list.
                'messageWithoutCommand.py',
                'asyncCog.py'
            ]
            if filename not in exclusionList:
                if filename.endswith('.py'):
                    client.load_extension(f'cogs.{filename[:-3]}')
        await ctx.send('Cogs have been loaded.')
    else:
        msg = (
            'Cannot load cogs, Please make sure bot has been configured for '
            'this guild. Remaining fields to be configured are as follows:\n'
            + '\n'.join(remainingFields)
        )

        await sendMessagePackets(ctx, msg)


@client.command()
@commands.check(isAdmin)
async def reload(ctx, extension):
    client.reload_extension(f'cogs.{extension}')


@client.command()
@commands.check(isAdmin)
async def checkTest(ctx):
    await ctx.send('Yes, you are admin')

# Load cogs
remainingFields = checkConfig(client.config)
if not remainingFields:
    for filename in os.listdir('./cogs'):
        # Files in exclusion list will not be loaded.
        exclusionList = [
            '__init__.py',
            'experimentalCog.py',
            'messageWithoutCommand.py',
            'asyncCog.py'
        ]
        if filename not in exclusionList:
            if filename.endswith('.py'):
                client.load_extension(f'cogs.{filename[:-3]}')
else:
    client.load_extension('cogs.devTools')
    client.load_extension('cogs.serverConfig')

# TODO: Make sure every assignments are encapsulated somehow to conform to
# sphinx documentation.

# TODO: BEFORE BOT CAN BE INVITED TO OFFICIAL SERVER A NEW TOKEN MUST BE MADE
# Get client token from file.
token = loadData('token.json')
# Run client by passing in token.
client.run(token)
