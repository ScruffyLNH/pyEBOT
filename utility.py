import json


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
        print(e)
        data = None
    return data


def saveData(fileName, data):
    """Save data to persistent file. If file does not already exist it will
    be created. The function will return 0 if save was successful. If not 1
    will be returned.

    :param fileName: Name of the file to save to.
    :type fileName: string
    :param data: The data object to save
    :type data: var
    :return: Status. 0 if successful, 1 if unsuccessful.
    :rtype: int
    """
    pass


def packData(obj):
    pass


def unpackData(fileName):
    pass


def initialize(clientObject):
    pass
    # Post resources to resource channel

    # Get the URL links to resourses

    # Identify the org logo url and store the link in Constants class
