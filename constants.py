
class Constants:
    """Contains project constants.
    """

    # Command prefix.
    CMD_PREFIX = '!'

    # Name of the file where data for events is stored.
    FILENAME = 'eventData.json'

    # Index touple of the google sheet cell where the update integer is set.
    CELL_INDEX = (2, 26)

    # ID of the guild using this bot.
    GUILD_ID = 676186916118331392  # TODO: This must be updated to the correct guild.

    # ID of the main channel in discord.
    MAIN_CHANNEL_ID = 676567548568797266  # TODO: This must be updated to the correct channel.

    # ID of the events category channel.
    EVENTS_CAT_CHANNEL_ID = 688305223164494048

    # Discord ID of the bots admin.
    ADMIN_ID = 312381318891700224

    # Discord ID of the event manager.
    EVENT_MANAGER_ID = 312381318891700224

    # Id of member role.
    MEMBER_ROLE_ID = 676793547197775873

    # Path to the directory where resources are stored.
    RES_PATH = 'Res/'

    # Url link to the discord logo.
    ORG_LOGO_URL = 'somethingsomething.jpg'  # TODO: Get actual link.

    # Url link to default event image.
    DEFAULT_IMG_URL = 'somethingsomething.jpg'  # TODO: Get actual link.

    # Date-time parser string to convert from date time in sheets to python
    # dateTime
    DT_SHEET_PARSE = "%m/%d/%Y %H:%M:%S"

    # Date-time parser string to convert python dateTime to the desired
    # formatting. (Weekdayname Monthname daysofmonth, HOURS:MINUTES UTC)
    DT_TEXT_PARSE = "%A %B %#d, %H:%M UTC"

    # Default event color.
    EVENT_COLOR = 0x6b90b5
