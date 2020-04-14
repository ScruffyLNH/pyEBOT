import json
import logging


def loadData(fileName):
    """Load data from persitent file. Returns None of file is not found.

    :param fileName: Name of the file to load from.
    :type fileName: string
    :return: The data that was loaded
    :rtype: var, None
    """
    try:
        with open(fileName) as f:
            data = json.load(f)
    except FileNotFoundError as e:
        logger = logging.getLogger('discord')
        logger.info(
            'Exception thrown when trying to load data. '
            'Error message reads:\n'
            f'{e}\n'
        )
        data = None
    return data


def saveData(fileName, data):
    """Save data to persistent file. If file does not already exist it will
    be created. The function will return True if successful, else False.

    :param fileName: Name of the file to save to.
    :type fileName: string
    :param data: The data object to save
    :type data: var
    :return: Status. True if successful, False if unsuccessful.
    :rtype: bool
    """
    try:
        with open(fileName, 'w', encoding='utf-8') as f:
            f.write(data)
    except Exception as e:
        logger = logging.getLogger('discord')
        logger.warning(
            'Exception thrown when trying to serialize data. '
            'Error message reads as follows:\n'
            f'{e}\n'
        )
        return False
    return True


def formatData(obj):
    """format data into json string using the dictionary structure as default.
    :param obj: The python object to be formatted.
    :type obj: object
    :return: The object data parsed into json string, or None if formatting was
    unsuccessful.
    :rtype: string, None
    """
    try:
        jsonData = json.dumps(
            obj,
            default=lambda o: o.__dict__,
            indent=2
        )
    except Exception as e:
        logger = logging.getLogger('discord')
        logger.warning(
            'Exception thrown while attempting to format data. '
            'Error message reads as follows:\n'
            f'{e}\n'
        )
        return None
    return jsonData


def unformatData(fileName):
    pass


def initialize(clientObject):
    pass
    # Post resources to resource channel

    # Get the URL links to resourses

    # Identify the org logo url and store the link in Constants class
