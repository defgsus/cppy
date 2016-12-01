
__doc__ = """
Test module desc.
Bladiblubb
"""

CONSTANT1 = 1
CONSTANT2 = 2


def func_a():
    """
    Returns 1.
    :return: float
    """
    return 1.


def func_add(a, b):
    """
    Adds two numbers
    :param a: any number
    :param b: any number
    :return: float
    """
    return float(a + b)

class Abel:
    """
    Base class
    """
    member = 1.
    def __init__(self):
        pass
    def __eq__(self, other):
        return member == other.member
    @property
    def amazingness(self):
        return 10.

class Kain(Abel):
    """
    Derived class
    """
    member = 2.
    def slay(self):
        pass

