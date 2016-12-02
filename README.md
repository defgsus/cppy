# cppy
python to cpp converter - the hard way

a python module that scans other modules and exports their declarations to a c++ python c-api file that can be used for extensions in embedded python. targets python3.4+ and c++11

c++ code must be explicitly written and embedded in the doc-strings. f.e.: 

```python
def add(a, b):
    """
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
```
