
__doc__ = """
Test module desc.
Bladiblubb
_CPP_:
#include "py_utils.h"
#include "io/log.h"
"""

CONSTANT1 = 1
CONSTANT2 = 2


def func_a():
    """
    Returns 1.
    :return: float
    _CPP_:
    return PyFloat_FromDouble(444.);
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
    if (!PyArg_ParseTuple(args, "dd", &a, &b))
        return NULL;
    return PyFloat_FromDouble(a+b);
    """
    return float(a + b)


class Abel:
    """
    Base class
    _CPP_:
    double v[4];
    """
    member = 1.
    def __init__(self):
        pass

    def __eq__(self, other):
        return member == other.member

    def __repr__(self):
        """
        _CPP_:
        return fromString(QString("Abel(%1, %2, %3, %4)")
            .arg(self->v[0]).arg(self->v[1]).arg(self->v[2]).arg(self->v[3]) );
        """
    def __str__(self):
        """
        _CPP_:
        return fromString(QString("Abel(%1, %2, %3, %4)")
            .arg(self->v[0]).arg(self->v[1]).arg(self->v[2]).arg(self->v[3]) );
        """

    @property
    def amazingness(self):
        "This property is amazing"
        return 10.

    def set(self, arg):
        """
        Set values
        :param lst: sequence of float
        :return: self
        _CPP_:
        PyObject* arg;
        if (!PyArg_ParseTuple(args, "O", &arg))
            return NULL;
        if (!PySequence_Check(arg))
        {
            PyErr_Set(PyExc_TypeError, QString("Expected sequence, got %1").arg(typeName(arg)));
            return NULL;
        }
        if (PySequence_Size(arg) != 4)
        {
            PyErr_Set(PyExc_TypeError, QString("Expected sequence of length %1, got %2")
                                        .arg(4).arg(PySequence_Size(arg)));
            return NULL;
        }
        for (int i=0; i<4; ++i)
        {
            auto o = PySequence_GetItem(arg, i);
            self->v[i] = PyFloat_AsDouble(o);
        }
        Py_INCREF(self);
        return (PyObject*)self;
        """
        return self

    def get(self):
        """
        Returns the contents as float list of length 4
        _CPP_:
        auto list = PyList_New(4);
        for (int i=0; i<4; ++i)
            PyList_SetItem(list, i, PyFloat_FromDouble(self->v[i]));
        return list;
        """

class Kain(Abel):
    """
    Derived class
    _CPP_:
    double v[4];
    """
    member = 2.
    def slay(self):
        "Slays Abel"
        pass

