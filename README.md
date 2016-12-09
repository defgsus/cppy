## cppy
python to cpp converter - the hard way

#### Introduction

Cppy is a python library that scans other modules and exports 
their declarations to a c++ python c-api file that can be used for 
extensions in embedded python. Targets python3.4+ and c++11

The basic idea is to write an interface in python and annotate it with 
the c++ code to work with your c++ application's data types.

C++ code must be explicitly written and embedded in the doc-strings. f.e.: 

```python
def add(a, b):
    """
    add(float, float) -> float
    Adds the numbers
    _CPP_:
    double a, b;
    if (!PyArg_ParseTuple(args, "dd", &a, &b))
        return NULL;
    return PyFloat_FromDouble(a+b);
    """
    return float(a + b)
```

Some knowledge of the *CPython API* is required. However, you do not 
have to write much boiler-plate code. Instead you only define the c++ data-members 
and the function bodies for the class methods. Everything else is generated and 
ready to be included in you c++ program by saying **cppy_initialize_my_module()** 
before calling **Py_Initialize()**
