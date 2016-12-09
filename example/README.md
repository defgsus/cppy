### Example project for cppy usage

run **make** and **make test** and see if it works.

Requires **python3.4-dev** and **g++11** and tested on linux only
 
The Makefile will use **../cppy.py** to compile the *example.py* module and 
create the *example.h* and *example.cpp* files. 
It then builds a python interpreter executable with the embedded module.

You can also start the generated ./python-mod and play with an interactive 
shell with the module compiled in.

The **py_utils.h/cpp** contains convenience functions to make CPython 
programming less painful. It will probably be extended and become part of 
the cppy package.
