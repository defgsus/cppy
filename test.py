import cppy.compiler

import test_module

objs = cppy.compiler.compile(test_module)

objs.dump()
print( objs.render_cpp() )
objs.render_cpp_to_file("test.cpp")
