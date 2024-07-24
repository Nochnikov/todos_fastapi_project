import pytest

def test_equal_or_not_equal():
    assert 1 == 1
    assert 1 != 2


def test_is_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('this is not a string', int)

def test_boolean():
    validated = True
    assert validated is True
    assert ('hello' == 'world') is False

def test_type():
    assert type('this is a string' is str)
    assert type('this is a string' is not int)


def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10

def test_list():
    numbers = [1, 2, 3, 4, 5]
    any_list = [False, False]
    assert 1 in numbers
    assert 7 not in numbers
    assert all(numbers)
    assert not any(any_list)



class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def default_student():
    return Student(first_name='John', last_name='Doe', major='Math', years=5)

def test_person_initialization(default_student):
    assert default_student.first_name == 'John', 'First name should be John'
    assert default_student.last_name == 'Doe', 'Last name should be Doe'
    assert default_student.major == 'Math', 'Major should be Math'
    assert default_student.years == 5, 'Years should be 5'




