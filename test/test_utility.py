import unittest
import event
import json
import event
import sheets
import utility
import os
from typing import List


class TestUtility(unittest.TestCase):

    # Setup and Teardown
    def setUp(self):

        self.testData = []
        for i in range(3):
            inst = InstanceTestClass()
            self.testData.append(inst)

        try:
            jsonData = json.dumps(
                    self.testData,
                    default=lambda o: o.__dict__,
                    indent=2
                    )
            with open('tstFile.json', 'w', encoding='utf-8') as f:
                json.dump(jsonData, f)
        except Exception as e:
            print(e)

    def tearDown(self):
        os.remove('tstFile.json')

    # Tests
    # loadData tests
    def test_loadData_returnIsNoneForInvalidPath(self):
        ret = utility.loadData('Non-existent-file')
        self.assertIsNone(ret)

    def test_loadData_returnIsStringWhenLoadingString(self):
        ret = utility.loadData('tstFile.json')
        self.assertIsInstance(ret, str)

    # saveData tests
    def test_saveData_fileCreatedForValidData(self):
        testString = 'something'
        success = utility.saveData('saveDataTest.json', testString)
        self.assertTrue(os.path.exists('saveDataTest.json'))
        if success:
            os.remove('saveDataTest.json')

    # formatData tests
    def test_formatData_something(self):  # TODO: More tests for formatData
        o = InstanceTestClass()
        jsonData = utility.formatData(o)

        self.assertIsNotNone(jsonData)


# TODO: Do this properly. Should probably be a class mehtod or something.
class InstanceTestClass():
    def __init__(self):
        self.number = 1
        self.string = 'hello'
        self.dictionary = {
            'key1': 'value1',
            'key2': 2,
            'key3': ('a', 1, 'b', 2),
            'key4': ['a', 1, 'b', 2]
        }


class Student(object):
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name


class Team(object):
    def __init__(self, students: List[Student]):
        self.students = students
