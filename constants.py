
class Constants:
    """Contains project constants.
    """

    # Command prefix.
    CMD_PREFIX = '!eb.'

    # Name of the file where data for events is stored.
    EVENT_DATA_FILENAME = 'eventData.json'

    # Name of the file where message data is stored.
    MESSAGE_DATA_FILENAME = 'messageData.json'

    # Name of the file where configuration data is stored.
    CONFIG_DATA_FILENAME = 'config.json'

    # Name of file where guild members are stored.
    GUILD_MEMBER_DATA_FILENAME = 'members.json'

    # Ids of people with elevated access for daymar events.
    DAYMAR_ELEVATED_ACCESS_IDS = [
        312381318891700224,  # Scruffy_90
        287978543336390656  # Cords1
    ]

    # Name of the log file.
    LOG_FILENAME = 'mainLogFile.log'

    # Index touple of the google sheet cell where the update integer is set.
    CELL_INDEX = (2, 26)

    # ID of the guild using this bot.
    # GUILD_ID = 676186916118331392  # TODO: This must be updated to the correct guild.

    # ID of the main channel in discord.
    # MAIN_CHANNEL_ID = 676567548568797266  # TODO: This must be updated to the correct channel.

    # ID of the events category channel.
    # EVENTS_CAT_CHANNEL_ID = 676474908603318272

    # ID of archive channel.
    # ARCHIVE_CHANNEL_ID = 685608894197792783

    # ID of Event-discussion channel.
    # EVENT_DISCUSSION_ID = 685608763901739011

    # ID of the channel where event images are posted.
    IMG_RES_CHANNEL_ID = 684911073304117319

    # ID of default event voice channel.
    # EVENT_VOICE_ID = 676186916118331397

    # Discord ID of the bots admin.
    # ADMIN_ID = 312381318891700224

    # Discord ID of the event manager.
    # EVENT_MANAGER_ID = 312381318891700224

    # Id of member role.
    # MEMBER_ROLE_ID = 676793547197775873

    # Path to the directory where resources are stored.
    RES_PATH = 'Res/'

    # URL link to the FR17 logo.
    DEF_THUMBNAIL_URL = (
        'https://cdn.discordapp.com/attachments/'
        '684911169189838863/684922720722485248/FR17_Logo_Opaque.png'
    )

    # URL link to the default event image.
    DEF_IMAGE_URL = (
        'https://cdn.discordapp.com/attachments/'
        '684911073304117319/706744411618410586/default_event_image.png'
    )

    # Date-time parser string to convert from date time in sheets to python
    # dateTime
    DT_SHEET_PARSE = "%m/%d/%Y %H:%M:%S"

    # Date-time parser string to convert python dateTime to the desired
    # formatting. (Weekdayname Monthname daysofmonth, HOURS:MINUTES UTC)
    DT_TEXT_PARSE = "%A %B %#d, %H:%M UTC"

    # Default event color.
    EVENT_COLOR = 0x6b90b5

    # Valid emoji reactions.
    REACTION_EMOJIS = {
        'participate': '✅',
        'cancel': '❌',
        'spectate': '💬',
        'help': '❔'
    }
