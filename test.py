import cppy.compiler

#import test_module
#objs = cppy.compiler.compile(test_module)

def doit():
    #import pector
    #objs = cppy.compiler.compile(pector)
    #import vec3
    #objs = cppy.compiler.compile(vec3)
    from trash import test_module
    objs = cppy.compiler.compile(test_module)

    objs.context.dump()

    #objs.namespaces = ["MO", "PYTHON34"]

    objs.write_to_file("test.h", objs.render_hpp())
    objs.write_to_file("test.cpp", objs.render_cpp())

    #path = "/home/defgsus/prog/qt_project/mo/matrixoptimizer/src/python/34/"
    path = "./example/"
    objs.write_to_file(path + "test_mod.h", objs.render_hpp())
    objs.write_to_file(path + "test_mod.cpp", objs.render_cpp())

def test_render():
    from cppy import renderer
    code = """
    for i in a:
        if i in a:
            break
    """
    print(code)
    print(renderer.change_text_indent(code, 0))

def split_doc_cpp(text):
    if not "_CPP_" in text:
        return (text, {})
    doc_end = 0
    idxs = []
    import re
    for i in re.finditer(r"_CPP_(\([A-Za-z]*\))?:", text):
        if not doc_end:
            doc_end = i.start()
        if i.groups():
            key = i.groups()[0]
            if key:
                key = key.replace("(", "").replace(")", "").upper()
            idxs.append((key, i.start(), i.end()))

    dic = {}
    for i, x in enumerate(idxs):
        end = len(text)
        if i+1 < len(idxs):
            end = idxs[i+1][1]
        dic.setdefault(x[0], text[x[2]:end])

    return (text[:doc_end].strip(), dic)


def test_split():
    doc = """
Base class
_CPP_:
    QString* data;
_CPP_(NEW):
    MO_PRINT("NEW $NAME()");
    self->data = new QString();
_CPP_(FREE):
    MO_PRINT("FREE $NAME()");
    delete data;
_CPP_(COPY):
    *copy->data = *data;"""
    doc2 = """
    """
    doc3 = """_CPP_:return false;"""
    t = split_doc_cpp(doc3)
    print("DOC[%s]" % t[0])
    for i in t[1]:
        print("%s[%s]" % (i, t[1][i]))

#test_split()
doit()
#test_render()
