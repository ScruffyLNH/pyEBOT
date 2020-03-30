from datetime import datetime
from typing import List
from pydantic import BaseModel


# class User(BaseModel):
#     id: int
#     name = 'John Doe'
#     signup_ts: datetime = None
#     friends: List[int] = []


# external_data = {
#     'id': '123',
#     'signup_ts': '2019-06-01 12:22',
#     'friends': [1, 2, '3']
# }
# user = User(**external_data)
# print(user.id)
# print(repr(user.signup_ts))
# print(user.friends)
# print(user.dict())


class Foo(BaseModel):
    count: int
    size: float = None


class Bar(BaseModel):
    apple = 'x'
    banana = 'y'


class Shape(BaseModel):
    round = 'yes'
    square = 'yes'


class Cheezeit(BaseModel):

    porosity: float = 0.9
    cheezyness: float = 0.94
    scrumpsicity: float = 0.99
    shape: List[Shape] = []

    def returnSomething(self):
        return('Uggahbuggah')


class Spam(BaseModel):
    foo: Foo
    bars: List[Bar]
    cheeze: Cheezeit = None
    testDict: dict = None
    exStr: str = None
    testList: List[Cheezeit] = []

    def editExStr(self, newString):
        self.exStr = newString


chz = Cheezeit()

cheezeit = Cheezeit()
cheezeit.shape.append(Shape())
m = Spam(foo={'count': 4}, bars=[{'apple': 'x1'}, {'apple': 'x2'}], testList=[chz])
m.cheeze = cheezeit
m.cheeze.shape.append(Shape())
m.editExStr('SuppeHue')
m.testList = [chz]

print(f'exStr is the following.......... {m.exStr}')

myDict = {
    'key1': Cheezeit(),
    'key2': Cheezeit()
}
m.testDict = myDict
# print(m)
# print(m.dict())
print(m.json(indent=2))
jString = m.json(indent=2)

newObj = Spam.parse_raw(jString)
print(newObj.dict())

print(newObj.cheeze.returnSomething())

print('Now printing testDict\n')
print(newObj.testDict)
print('\nEnd print of testDict\n')

print(f'The value of testDict key2 is: {newObj.testDict["key2"]}')

myBar = Bar()

print(myBar.apple)
myBar.apple = 'somethng'

print(myBar.apple)

print(newObj.exStr)
