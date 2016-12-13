"""
Example module to demonstrate cppy

_CPP_(HEADER):
    // This part will be included in the generated .h file
    // We pull in some helper functions here because CPython is really low-level by itself..
    #include "py_utils.h"

_CPP_:
    // This part will be included in the generated .cpp file
    using namespace PyUtils;
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
    An example to create an embedded class object

    _CPP_:
        // These are the C members of the class
        // (Since we are in 'C namespace' they are not constructed by default!)
        std::string* data;
        long justice;

    _CPP_(NEW):
        // When object is created we have to initialize all members ourselves
        data = new std::string();
        justice = 23;
        // template tags make life easier
        // $NAME() resolves to Abel or Kain, when Kain is derived from Abel
        CPPY_PRINT("NEW $NAME()");

    _CPP_(FREE):
        CPPY_PRINT("FREE $NAME()");
        delete data;

    _CPP_(COPY):
        // A low-level copy function you can use later
        // should copy all members to instance 'copy'
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
            // if we got a string, that's fine
            if (fromPython(arg1, self->data))
                return 0;
            // An empty argument is also acceptable
            if (PyTuple_Check(arg1) && PyTuple_Size(arg1) == 0)
                return 0;
            // otherwise raise an error
            setPythonError(PyExc_TypeError, SStream() << "Invalid argument " << typeName(arg1)
                                            << " to $NAME() constructor");
            // The __init__ function is also special in it's return-type!
            return -1;
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
            return SStream() << "$NAME()@" << (void*)self;
        """
        pass

    def __str__(self):
        """
        _CPP_:
            return SStream() << "$NAME()(\\"" << *self->data << "\\")";
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
            // A property getter is like a normal class function in the c-api
            return toPython((long)(size_t(self) % 23));
        """
        pass

    @property
    def justice(self):
        """
        _CPP_:
            return toPython(self->justice);
        _CPP_(SET):
            // Use ^ this annotation to implement the setter code
            if (!expectFromPython(arg1, &self->justice))
                return -1;
            return 0; // setters have a special return type as well
        """

    def get(self):
        """
        get() -> string
        Returns the contents as string
        _CPP_:
            return toPython(*self->data);
        """

    def spawn(self):
        """
        Spawn new instance of a Kain
        _CPP_:
            auto k = $NEW(Kain);
            *k->data = "from_" + *self->data;
            k->setAbel(self);
            // k is of type $STRUCT(Kain), we need to cast to PyObject* on return
            return (PyObject*)k;
        """

class Kain(Abel):
    """
    A derived class
    All _CPP_ parts are pulled in from base classes

    _CPP_:
        // Again, template tags help a lot.
        // STRUCT(classname) gets you the struct name of any class known to cppy
        $STRUCT(Abel)* abel;

        // A function to set the Abel class as member of Kain
        void setAbel($STRUCT(Abel)* a) { Py_CLEAR(abel); abel = a; Py_XINCREF(abel); }

    _CPP_(NEW):
        // Initialize memory
        abel = nullptr;

    _CPP_(FREE):
        // The recommended method to give away a reference
        Py_CLEAR(abel);

    _CPP_(COPY):
        copy->abel = abel;
        Py_XINCREF(copy->abel);

    """
    def __init__(self):
        """
        _CPP_:
            PyObject *a1=0, *a2=0;
            if (!PyArg_ParseTuple(arg1, "|OO", &a1, &a2))
                return -1;

            if (a1 && !expectFromPython(a1, self->data))
                return -1;

            if (a2)
            {
                if (!$is_instance(a2, Abel))
                {
                    setPythonError(PyExc_TypeError, SStream() << "Invalid argument " << typeName(a1) );
                    return -1;
                }
                self->setAbel($CAST(a2, Abel));
            }
            return 0;
        """
        pass

    def slay(self):
        """
        Slays Abel
        _CPP_:
            std::string s = SStream() << "Kain(" << *self->data << ") slew Abel("
                       << (self->abel ? *self->abel->data : std::string()) << ")";
            CPPY_PRINT(s);
            return toPython(s);
        """
        pass

    def spawn(self):
        """
        Spawn new instance of an Abel
        _CPP_:
            auto a = $NEW(Abel);
            *a->data = "from_" + *self->data;
            return (PyObject*)a;
        """

