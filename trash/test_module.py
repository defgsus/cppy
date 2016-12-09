
__doc__ = """
Test module desc.
Bladiblubb
_CPP_:
#include "py_utils.h"
"""

CONSTANT1 = 1
CONSTANT2 = 2


def func_a():
    """
    Returns 1.
    :return: float
    _CPP_:
    return toPython(444.);
    """
    return 1.

def func_add(a, b):
    """
    Adds two numbers
    :param a: any number
    :param b: any number
    :return: float
    _CPP_:
    double a, b;
    if (!PyArg_ParseTuple(arg1, "dd", &a, &b))
        return NULL;
    return toPython(a+b);
    """
    return float(a + b)


class Abel:
    """
    Base class
    _CPP_:
        std::string* data;
    _CPP_(NEW):
        CPPY_PRINT("NEW $NAME()");
        data = new std::string();
    _CPP_(FREE):
        CPPY_PRINT("FREE $NAME()");
        delete data;
    _CPP_(COPY):
        *copy->data = *data;
    """
    member = 1.
    def __init__(self):
        """
        _CPP_:
        arg1 = removeArgumentTuple(arg1);
        if (fromPython(arg1, self->data))
            return 0;
        return 0;
        """
        pass

    def __eq__(self, other):
        """
        _CPP_:
        if (!$IS_INSTANCE(arg1))
        {
            setPythonError(PyExc_TypeError, SStream() << "Expected $NAME(), got " << typeName(arg1));
            return NULL;
        }
        return toPython(*self->data == *($CAST(arg1)->data));
        """
        pass

    def __repr__(self):
        """
        _CPP_:
        return toPython(SStream() << "$NAME()@" << (void*)self);
        """
        pass

    def __str__(self):
        """
        _CPP_:
        return toPython(SStream() << "$NAME()(\\"" << *self->data << "\\")");
        """
        pass

    def copy(self):
        """
        _CPP_:
        return (PyObject*)$COPY(self);
        """
        pass

    def set(self, arg):
        """
        _CPP_:
        if (!expectFromPython(arg1, self->data))
            return NULL;
        Py_RETURN_SELF;
        """
        pass

    @property
    def wisdom(self):
        """
        This property is amazing
        _CPP_:
        return toPython(7.);
        """
        pass

    def get(self):
        """
        Returns the contents as string
        _CPP_:
        return toPython(self->data);
        """

class Kain(Abel):
    """
    Derived class
    """
    member = 2.
    def slay(self):
        """
        Slays Abel
        _CPP_:
        CPPY_PRINT("Kain slew Abel");
        Py_RETURN_NONE;
        """
        pass

