/** @brief helper for python c-api

    <p>(c) 2016, stefan.berke@modular-audio-graphics.com</p>
    <p>All rights reserved</p>
*/

#ifndef PY_UTILS_H
#define PY_UTILS_H

#include <string>
#include <sstream>
#include <functional>

#include <python3.4/Python.h>
#include <python3.4/structmember.h>
#undef T_NONE
#undef T_OBJECT

#ifndef CPPY_PRINT
#   include <iostream>
#   define CPPY_PRINT(arg__) { std::cout << arg__ << std::endl; }
#endif

#ifndef CPPY_ERROR
#   define CPPY_ERROR(arg__) { CPPY_PRINT(arg__); exit(EXIT_FAILURE); }
#endif

#ifndef Py_RETURN_SELF
#   define Py_RETURN_SELF return Py_INCREF(self), reinterpret_cast<PyObject*>(self)
#endif

namespace PyUtils {

PyObject* toPython(const std::string&);
PyObject* toPython(long);
PyObject* toPython(double);
PyObject* toPython(bool);

bool fromPython(PyObject*, std::string*);
bool fromPython(PyObject*, long*);
bool fromPython(PyObject*, double*);

bool expectFromPython(PyObject*, std::string*);
bool expectFromPython(PyObject*, long*);
bool expectFromPython(PyObject*, double*);

// Writes 'len' entries from the python sequence into 'vec'
bool fromPythonSequence(PyObject* seq, std::string* vec, size_t len);
bool fromPythonSequence(PyObject* seq, long* vec, size_t len);
bool fromPythonSequence(PyObject* seq, double* vec, size_t len);

bool expectFromPythonSequence(PyObject* seq, std::string* vec, size_t len);
bool expectFromPythonSequence(PyObject* seq, long* vec, size_t len);
bool expectFromPythonSequence(PyObject* seq, double* vec, size_t len);

/** If @p arg is a tuple with one object, then return the object, otherwise arg */
PyObject* removeArgumentTuple(PyObject* arg);

void setPythonError(PyObject* exc, const std::string& txt);

std::string typeName(const PyObject* arg);

/** Iterates over every item in the PySequence. If seq is not sequencable,
    sets PyErr and returns false. If foo returns false, the iteration is stopped
    and false is returned. */
bool iterateSequence(PyObject* seq, std::function<bool(PyObject*item)> foo);

/** Verify that index < len, raise IndexError otherwise */
bool checkIndex(Py_ssize_t index, Py_ssize_t len);

/** print object internals */
void dumpObject(PyObject* arg, bool introspect);

/** A std::stringstream wrapper that converts to
    std::string or PyObject* automatically */
class SStream
{
    std::stringstream sstream_;
public:
    template <class T>
    SStream& operator << (const T& t) { sstream_ << t; return *this; }

    operator std::string() { return sstream_.str(); }
    operator PyObject*() { return toPython(sstream_.str()); }
};


} // namespace PyUtils


#endif // PY_UTILS_H

