import cppy.compiler

import test_module

objs = cppy.compiler.compile(test_module)

objs.dump()


objs.h_header = """
namespace MO {
namespace PYTHON34 {
"""
objs.h_footer = """
} // namespace PYTHON34
} // namespace MO
"""
objs.cpp_header = str(objs.h_header)
objs.cpp_footer = str(objs.h_footer)

objs.write_to_file("test.h", objs.render_hpp())
objs.write_to_file("test.cpp", objs.render_cpp())

mo_path = "/home/defgsus/prog/qt_project/mo/matrixoptimizer/src/python/34/"
objs.write_to_file(mo_path + "test_mod.h", objs.render_hpp())
objs.write_to_file(mo_path + "test_mod.cpp", objs.render_cpp())
