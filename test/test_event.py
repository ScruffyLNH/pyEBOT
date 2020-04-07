import unittest
from datetime import datetime
import event


# TODO: Make unit tests work with py files in subdirectory

class TestEvent(unittest.TestCase):

    def setUp(self):

        self.eventData = {
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
            'Color Code': '0',
            'Update Status': 0
        }
        self.keys = [
            'Event',
            'Id',
            'Organizer',
            'Date Time',
            'Description',
            'Location',
            'Duration',
            'Category',
            'Members Only',
            'Additional Info',
            'Channel',
            'Deadline',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            'Color Code',
            'Update Status',
        ]

    def tearDown(self):
        pass

    # Tests
    # Event class tests
    # getParticipant tests
    def test_getParticipant_returnIsPersonObjectForValidId(self):
        participant = event.Person(id=123456789, name='SomeName')
        eventInstance = event.Event(
            id=999,
            data=self.eventData,
            keys=self.keys,
            participants=[participant],
            lastUpdate=datetime.utcnow()
        )
        ret = eventInstance.getParticipant(123456789)
        self.assertIsInstance(ret, event.Person)

    def test_getParticipant_returnIsNoneForInvalidId(self):
        participant = event.Person(id=123456789, name='SomeName')
        eventInstance = event.Event(
            id=999,
            data=self.eventData,
            keys=self.keys,
            roles={},
            channels=[],
            participants=[participant],
            lastUpdate=datetime.utcnow()
        )
        ret = eventInstance.getParticipant(12345555)
        self.assertIsNone(ret)

    # Person class tests
    # getRole tests
    def test_getRole_returnIsCorrectRole(self):
        person = event.Person(id=123456, name='SomeName')
        role = event.Role(id=11112222, name='roleName')
        person.roles.append(role)

        ret = person.getRole(11112222)
        self.assertEqual(ret, role)

    def test_getRole_returnIsNoneForInvalidId(self):
        person = event.Person(id=123456, name='SomeName')
        role = event.Role(id=11112222, name='roleName')
        person.roles.append(role)

        ret = person.getRole(42)
        self.assertIsNone(ret)

    # removeRole tests
    def test_removeRole_returnIsCorrectRole(self):
        person = event.Person(id=123456, name='SomeName')
        role = event.Role(id=11112222, name='roleName')
        person.roles.append(role)

        ret = person.removeRole(11112222)
        self.assertEqual(ret, role)

    def test_removeRole_correctRoleIsRemoved(self):
        person = event.Person(id=123456, name='SomeName')
        roles = [
            event.Role(id=11112222, name='roleName'),
            event.Role(id=123123, name='otherRole'),
            event.Role(id=11447788, name='finalRole')
        ]
        [person.roles.append(r) for r in roles]

        self.assertIn(roles[1], person.roles)
        person.removeRole(123123)
        self.assertNotIn(roles[1], person.roles)

    def test_removeRole_duplicateRolesAreRemoved(self):
        person = event.Person(id=123456, name='SomeName')
        roles = [
            event.Role(id=11112222, name='roleName'),
            event.Role(id=123123, name='dupeRole1'),
            event.Role(id=11447788, name='otherRole'),
            event.Role(id=123123, name='dupeRole2'),
            event.Role(id=99999999, name='finalRole')
        ]
        [person.roles.append(r) for r in roles]

        self.assertIn(roles[1], person.roles)
        self.assertIn(roles[3], person.roles)
        person.removeRole(123123)
        self.assertNotIn(roles[1], person.roles)
        self.assertNotIn(roles[3], person.roles)
