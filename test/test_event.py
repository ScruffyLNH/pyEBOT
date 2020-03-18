import unittest
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
        participant = event.Person(123456789, 'SomeName')
        eventInstance = event.Event(
            999,
            self.eventData,
            self.keys,
            None,
            {},
            [],
            [participant]
        )
        ret = eventInstance.getParticipant(123456789)
        self.assertIsInstance(ret, event.Person)

    def test_getParticipant_returnIsNoneForInvalidId(self):
        participant = event.Person(123456789, 'SomeName')
        eventInstance = event.Event(
            999,
            self.eventData,
            self.keys,
            None,
            {},
            [],
            [participant]
        )
        ret = eventInstance.getParticipant(12345555)
        self.assertIsNone(ret)

    # Person class tests
    # getRole tests
    def test_getRole_returnIsCorrectRole(self):
        person = event.Person(123456, 'SomeName')
        role = event.Role('roleName', 11112222)
        person.roles.append(role)

        ret = person.getRole(11112222)
        self.assertEqual(ret, role)

    def test_getRole_returnIsNoneForInvalidId(self):
        person = event.Person(123456, 'SomeName')
        role = event.Role('roleName', 11112222)
        person.roles.append(role)

        ret = person.getRole(42)
        self.assertIsNone(ret)

    # removeRole tests
    def test_removeRole_returnIsCorrectRole(self):
        person = event.Person(123456, 'SomeName')
        role = event.Role('roleName', 11112222)
        person.roles.append(role)

        ret = person.removeRole(11112222)
        self.assertEqual(ret, role)

    def test_removeRole_correctRoleIsRemoved(self):
        person = event.Person(123456, 'SomeName')
        roles = [
            event.Role('roleName', 11112222),
            event.Role('otherRole', 123123),
            event.Role('finalRole', 11447788)
        ]
        [person.roles.append(r) for r in roles]

        self.assertIn(roles[1], person.roles)
        person.removeRole(123123)
        self.assertNotIn(roles[1], person.roles)

    def test_removeRole_duplicateRolesAreRemoved(self):
        person = event.Person(123456, 'SomeName')
        roles = [
            event.Role('roleName', 11112222),
            event.Role('dupeRole1', 123123),
            event.Role('otherRole', 11447788),
            event.Role('dupeRole2', 123123),
            event.Role('finalRole', 99999999)
        ]
        [person.roles.append(r) for r in roles]

        self.assertIn(roles[1], person.roles)
        self.assertIn(roles[3], person.roles)
        person.removeRole(123123)
        self.assertNotIn(roles[1], person.roles)
        self.assertNotIn(roles[3], person.roles)
