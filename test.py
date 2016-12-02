import cppy.compiler

#import test_module
#objs = cppy.compiler.compile(test_module)

import vec3
objs = cppy.compiler.compile(vec3)

objs.dump()


objs.namespaces = ["MO", "PYTHON34"]

objs.write_to_file("test.h", objs.render_hpp())
objs.write_to_file("test.cpp", objs.render_cpp())

mo_path = "/home/defgsus/prog/qt_project/mo/matrixoptimizer/src/python/34/"
objs.write_to_file(mo_path + "test_mod.h", objs.render_hpp())
objs.write_to_file(mo_path + "test_mod.cpp", objs.render_cpp())
