## cppy
python to cpp - the hard way

#### Abstract

cppy is a python module that helps embedding python in c++ applications by creating the required 
c-api wrapping code from annotated python code, targeting python3.4+ and c++11

The basic idea is to write an interface in python and annotate it with 
the c++ code to work with your c++ application's data types and runtime 
structures. cppy is not mainly intended to make python programs run faster but 
to help embedding python in your software and expose internal types 
efficiently.

C++ code must be explicitly written and embedded in the doc-strings. like so: 

```python
def add(a, b):
    """
    add(float, float) -> float
    Adds the numbers
    
    _CPP_: // <- doc-string tag
    
    double a, b;
    if (!PyArg_ParseTuple(arg1, "dd", &a, &b))
        return NULL;
    return PyFloat_FromDouble(a+b);
    """
    pass 
```

Knowledge of the *CPython API* is required. However, you do not 
have to write much boiler-plate code. Instead you only define the c++ data-members 
and function bodies for class methods. Everything else is generated and 
can be included with 
```c++
void main() {
    cppy_initialize_my_module(); 
    Py_Initialize();
}
```
