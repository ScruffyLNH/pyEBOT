import unittest
import discord # noqa
import datetime
import cogs.eventCog as eventCog
from discord.ext import commands


# TODO: Make unit tests work with py files in subdirectory

class TestEventCog(unittest.TestCase):

    def setUp(self):

        self.client = commands.Bot('!')

        self.eventData = [
            {
                'Event': 'VIKING SNATCH',
                'Id': '123456789',
                'Organizer': '',
                'Date Time': '8/11/2020 15:30:00',
                'Description': 'description for VIKING SNATCH',
                'Location': '',
                'Duration': '',
                'Category': '',
                'Members Only': '',
                'Additional Info': '',
                'Channel': '',
                'Deadline': '1/1/2020 15:30:00',
                '': '',
                'Update Status': 0
            },
            {
                'Event': 'OPERATION BEASTMASTER',
                'Id': '',
                'Organizer': '',
                'Date Time': '8/11/2020 15:30:00',
                'Description': 'description for BEASTMASTER',
                'Location': '', 'Duration': '',
                'Category': '',
                'Members Only': '',
                'Additional Info': '',
                'Channel': '',
                'Deadline': '',
                '': '',
                'Update Status': ''
            },
            {
                'Event': 'OPERATION NICKEL GRASS',
                'Id': '234567891',
                'Organizer': '',
                'Date Time': '',
                'Description': 'description for NICKELGRASS',
                'Location': '',
                'Duration': '',
                'Category': '',
                'Members Only': '',
                'Additional Info': '',
                'Channel': '',
                'Deadline': '1/1/2020 15:30:00',
                '': '',
                'Update Status': ''
            },
            {
                'Event': 'OPERATION NICKEL GRASS',
                'Id': '',
                'Organizer': '',
                'Date Time': '',
                'Description': 'description for NICKELGRASS',
                'Location': '',
                'Duration': '',
                'Category': '',
                'Members Only': '',
                'Additional Info': '',
                'Channel': '',
                'Deadline': '',
                '': '',
                'Update Status': ''
            }
        ]

        self.dateTimeEventData = [
            {
                'Event': 'VIKING SNATCH',
                'Id': '123456789',
                'Organizer': '',
                'Date Time': '8/11/2020 15:30:00',
                'Description': 'description for VIKING SNATCH',
                'Location': '',
                'Duration': '',
                'Category': '',
                'Members Only': '',
                'Additional Info': '',
                'Channel': '',
                'Deadline': '1/1/2020 15:30:00',
                '': '',
                'Update Status': 0
            },
            {
                'Event': 'OPERATION BEASTMASTER',
                'Id': '',
                'Organizer': '',
                'Date Time': '8/11/2020 15:30:00',
                'Description': 'description for BEASTMASTER',
                'Location': '', 'Duration': '',
                'Category': '',
                'Members Only': '',
                'Additional Info': '',
                'Channel': '',
                'Deadline': '',
                '': '',
                'Update Status': ''
            },
            {
                'Event': 'OPERATION NICKEL GRASS',
                'Id': '234567891',
                'Organizer': '',
                'Date Time': '',
                'Description': 'description for NICKELGRASS',
                'Location': '',
                'Duration': '',
                'Category': '',
                'Members Only': '',
                'Additional Info': '',
                'Channel': '',
                'Deadline': '1/1/2020 15:30:00',
                '': '',
                'Update Status': ''
            },
            {
                'Event': 'OPERATION NICKEL GRASS',
                'Id': '',
                'Organizer': '',
                'Date Time': '',
                'Description': 'description for NICKELGRASS',
                'Location': '',
                'Duration': '',
                'Category': '',
                'Members Only': '',
                'Additional Info': '',
                'Channel': '',
                'Deadline': '',
                '': '',
                'Update Status': ''
            }
        ]

        dt = datetime.datetime(2020, 5, 4, 1, 55, second=45)
        self.dateTimeEventData[0]['Date Time'] = (
            dt
            )
        self.dateTimeEventData[1]['Date Time'] = (
            dt + datetime.timedelta(days=5)
            )
        self.dateTimeEventData[2]['Date Time'] = (
            dt - datetime.timedelta(days=2)
            )
        self.dateTimeEventData[3]['Date Time'] = (
            dt - datetime.timedelta(days=1)
            )

        self.unsortedEvents = [
            {
                'index': (1, 2),
                'event': {
                    'Event': 'OPERATION BEASTMASTER',
                    'Id': '', 'Organizer': '',
                    'Date Time': '8/11/2020 15:30:00',
                    'Description':
                    'description for BEASTMASTER',
                    'Location': '',
                    'Duration': '',
                    'Category': '',
                    'Members Only': '',
                    'Additional Info': '',
                    'Channel': '',
                    'Deadline': '',
                    '': '',
                    'Update Status': ''
                }
            },
            {
                'index': (3, 2),
                'event':
                {
                    'Event': 'OPERATION NICKEL GRASS',
                    'Id': '',
                    'Organizer': '',
                    'Date Time': '',
                    'Description': 'description for NICKELGRASS',
                    'Location': '',
                    'Duration': '',
                    'Category': '',
                    'Members Only': '',
                    'Additional Info': '',
                    'Channel': '',
                    'Deadline': '',
                    '': '',
                    'Update Status': ''
                }
            }
        ]
        self.unsortedEvents[0]['event']['datetime'] = (
            dt
        )
        self.unsortedEvents[1]['event']['dateTime'] = (
            dt - datetime.timedelta(days=2)
        )

    def tearDown(self):
        pass

    # Tests

    # SortEvents tests
    def test_sortEvents_returnIsSameLengthAsInput(self):
        ec = eventCog.EventCog(self.client)
        ret = ec.sortEvents(self.unsortedEvents)
        self.assertEqual(len(self.unsortedEvents), len(ret))

    # ConvertDates tests
    def test_convertDates_returnIsSameLengthAsInput(self):
        ec = eventCog.EventCog(self.client)
        ret = ec.convertDates(self.eventData, 'Date Time', 'Deadline')
        self.assertEqual(len(self.eventData), len(ret))

    def test_convertDates_returnTypeIsTimeDate(self):
        ec = eventCog.EventCog(self.client)
        ret = ec.convertDates(self.eventData, 'Date Time', 'Deadline')
        self.assertIsInstance(ret[0]['Date Time'], datetime.datetime)
        self.assertIsInstance(ret[0]['Deadline'], datetime.datetime)

    # CheckId tests
    def test_checkId_indexIsCorrect(self):
        ec = eventCog.EventCog(self.client)
        ret = ec.checkId(self.eventData)
        index = (1, 2)
        self.assertEqual(ret[0]['index'], index)
        index = (3, 2)
        self.assertEqual(ret[1]['index'], index)

    def test_checkId_returnProperNumOfListEntries(self):
        ec = eventCog.EventCog(self.client)
        ret = ec.checkId(self.eventData)
        self.assertEqual(len(ret), 2)
