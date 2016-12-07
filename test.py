import cppy.compiler

#import test_module
#objs = cppy.compiler.compile(test_module)

def doit():
    #import pector
    #objs = cppy.compiler.compile(pector)
    import vec3
    objs = cppy.compiler.compile(vec3)

    objs.dump()


    objs.namespaces = ["MO", "PYTHON34"]

    objs.write_to_file("test.h", objs.render_hpp())
    objs.write_to_file("test.cpp", objs.render_cpp())

    mo_path = "/home/defgsus/prog/qt_project/mo/matrixoptimizer/src/python/34/"
    objs.write_to_file(mo_path + "test_mod.h", objs.render_hpp())
    objs.write_to_file(mo_path + "test_mod.cpp", objs.render_cpp())

def test_render():
    from cppy import renderer
    from cppy import c_types
    print(renderer.render_struct("PySequenceMethods", "my_struct", c_types.PySequenceMethods, {}))

doit()
#test_render()
