import unittest
import event
import json
import event
import sheets
import utility
from typing import List


class TestUtility(unittest.TestCase):

    # Setup and Teardown
    def setUp(self):

        self.testData = []
        for i in range(3):
            inst = InstanceTestClass()
            self.testData.append(inst)

        try:
            jasonData = json.dumps(
                    self.testData,
                    default=lambda o: o.__dict__,
                    indent=2
                    )
            with open('tstFile.json', 'w', encoding='utf-8') as f:
                json.dump(jasonData, f)
        except Exception as e:
            print(e)

    def tearDown(self):
        pass  # os.remove('tstFile.json')

    # Tests
    # def test_loadData(self):
    #     res = utility.loadData('Non-existent-file')
    #     self.assertIsNone(res)

    def test_myMethod(self):
        pass
        # utility.TestClass.myMethod('Ughhabughha')


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
