from django.test import TestCase

# Create your tests here.


class Person(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

alex = Person('alex')
print(alex)
print(alex.__str__())
print(str(alex))