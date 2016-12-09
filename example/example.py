"""
Example module to demonstrate cppy

_CPP_:
// This part will be included in the generated .cpp file
// We pull in some helper functions here because CPython is really low-level..
#include "py_utils.h"
"""

CONSTANT1 = 1
CONSTANT2 = 2


def func_a():
    """
    func_a() -> float
    Returns 444.
    _CPP_:
    return toPython(444.);
    """
    pass

def func_add(a, b):
    """
    func_add(float, float) -> float
    Adds two numbers
    _CPP_:
    double a, b;
    if (!PyArg_ParseTuple(arg1, "dd", &a, &b))
        return NULL;
    return toPython(a+b);
    """
    pass


class Abel:
    """
    An example to create a embedded class object

    _CPP_:
        // These are c++ members of the class
        std::string* data;
    _CPP_(NEW):
        // When object is created we have to initialize all members ourselves
        CPPY_PRINT("NEW $NAME()");
        data = new std::string();
    _CPP_(FREE):
        CPPY_PRINT("FREE $NAME()");
        delete data;
    _CPP_(COPY):
        // An internal copy function you can use later
        // Should copy all members to instance 'copy'
        *copy->data = *data;
    """
    member = 1.
    def __init__(self, arg):
        """
        Constructor, argument can be a string
        _CPP_:
        // __init__ functions are always called as METH_VARARGS function
        // so 'arg1' is always a tuple and 'arg2' is a dict with keywords
        arg1 = removeArgumentTuple(arg1);
        if (fromPython(arg1, self->data))
            return 0;
        return 0;
        """
        pass

    def __eq__(self, other):
        """
        Test for equality of content
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
        copy() -> Abel
        Returns a copy of the object
        _CPP_:
        return (PyObject*)$COPY(self);
        """
        pass

    def set(self, arg):
        """
        set(string) -> self
        Sets the contents of the object
        _CPP_:
        if (!expectFromPython(arg1, self->data))
            return NULL;
        Py_RETURN_SELF;
        """
        pass

    @property
    def wisdom(self):
        """
        A property
        _CPP_:
        // A property is like a normal class function in the c-api
        return toPython(7.);
        """
        pass

    def get(self):
        """
        get() -> string
        Returns the contents as string
        _CPP_:
        return toPython(self->data);
        """


class Kain(Abel):
    """
    A derived class
    All _CPP_ parts are pulled in from base classes
    """
    def slay(self):
        """
        Slays Abel
        _CPP_:
        CPPY_PRINT("Kain(" << *self->data << ") slew Abel");
        Py_RETURN_NONE;
        """
        pass

