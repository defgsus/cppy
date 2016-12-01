import inspect

TYPE_STRUCT_MEMBER = [
    ("const char*", "tp_name"),
    ("Py_ssize_t", "tp_basicsize"),
    ("Py_ssize_t", "tp_itemsize"),
    ("destructor", "tp_dealloc"),
    ("printfunc", "tp_print"),
    ("getattrfunc", "tp_getattr"),
    ("setattrfunc", "tp_setattr"),
    ("void*", "tp_reserved"),
    ("reprfunc", "tp_repr"),
    ("PyNumberMethods*", "tp_as_number"),
    ("PySequenceMethods*", "tp_as_sequence"),
    ("PyMappingMethods*", "tp_as_mapping"),
    ("hashfunc", "tp_hash"),
    ("ternaryfunc", "tp_call"),
    ("reprfunc", "tp_str"),
    ("getattrofunc", "tp_getattro"),
    ("setattrofunc", "tp_setattro"),
    ("PyBufferProcs*", "tp_as_buffer"),
    ("unsigned long", "tp_flags"),
    ("const char*", "tp_doc"),
    ("traverseproc", "tp_traverse"),
    ("inquiry", "tp_clear"),
    ("richcmpfunc", "tp_richcompare"),
    ("Py_ssize_t", "tp_weaklistoffset"),
    ("getiterfunc", "tp_iter"),
    ("iternextfunc", "tp_iternext"),
    ("struct PyMethodDef*", "tp_methods"),
    ("struct PyMemberDef*", "tp_members"),
    ("struct PyGetSetDef*", "tp_getset"),
    ("struct _typeobject*", "tp_base"),
    ("PyObject*", "tp_dict"),
    ("descrgetfunc", "tp_descr_get"),
    ("descrsetfunc", "tp_descr_set"),
    ("Py_ssize_t", "tp_dictoffset"),
    ("initproc", "tp_init"),
    ("allocfunc", "tp_alloc"),
    ("newfunc", "tp_new"),
    ("freefunc", "tp_free"),
    ("inquiry", "tp_is_gc"),
    ("PyObject*", "tp_bases"),
    ("PyObject*", "tp_mro"),
    ("PyObject*", "tp_cache"),
    ("PyObject*", "tp_subclasses"),
    ("PyObject*", "tp_weaklist"),
    ("destructor", "tp_del"),
    ("unsigned int", "tp_version_tag"),
    ("destructor", "tp_finalize")
]

class CodeObject:
    def __init__(self, name, doc="", src_pos=""):
        self.name = name
        self.doc = doc if doc else ""
        self.src_pos = src_pos

    def __str__(self):
        return "%s" % self.name

    def render_cpp_declaration(self):
        raise NotImplementedError

class Function(CodeObject):
    def __init__(self, func):
        super().__init__(
            name=func.__name__,
            doc=inspect.getdoc(func),
            src_pos="%s:%d" % (func.__code__.co_filename, func.__code__.co_firstlineno),
        )
        self.func = func
        self.cpp = None

    def get_cpp(self):
        if not self.cpp:
            return "#error Not implemented"
        else:
            return self.cpp

    def render_cpp_declaration(self, prefix="", struct_name=None):
        s = """
    /* %(src_pos)s */
    static const char* %(prefix)s%(name)s_doc = "%(doc)s"
    static PyObject* %(prefix)s%(name)s(%(PyObject)s* self, PyObject* args)
    {
        %(code)s
    }
    """
        return s % {"prefix":prefix, "name":self.name,
                    "doc": self.doc.replace("\n", "\\n").replace("\r", ""),
                    "src_pos": self.src_pos, "code": self.get_cpp(),
                    "PyObject": "PyObject" if struct_name is None else struct_name }

    def render_cpp_struct_entry(self, prefix=""):
        return '{ "%(name)s", (PyCFunction)%(prefix)s%(name)s, %(args)s, %(prefix)s%(name)s_doc },\n' % {
            "name":self.name, "prefix":prefix, "args":"METH_VARARGS"}


class Class(CodeObject):
    def __init__(self, name, doc=""):
        super().__init__(name=name, doc=doc)
        self.functions = []
        self.prefix = "cppy_classdef_%s_" % name
        self.struct_name = "cppy_class_struct_%s" % name
        self.method_struct_name = "cppy_method_def_%s" % name
        self.type_def_struct_name = "cppy_type_def_%s" % name

    def append(self, o):
        if isinstance(o, Function):
            self.functions.append(o)

    def render_cpp_declaration(self):
        code = ""
        code += 'extern "C" {'
        code += "\n" + self.render_struct()
        for i in self.functions:
            code += i.render_cpp_declaration(prefix=self.prefix, struct_name=self.struct_name)
        code += "\n" + self.render_method_struct()
        code += "\n" + self.render_type_struct()
        code += '\n} // extern "C"\n'

        return code

    def render_struct(self):
        code = """
    struct %(name)s
    {
        PyObject_HEAD
        %(decl)s

        static %(name)s* new_func();
        static %(name)s* copy_func(%(name)s*);
        static void dealloc(%(name)s* self)
        {
            self->ob_base.ob_type->tp_free(reinterpret_cast<PyObject*>(self));
        }
        static const char* doc_string = "%(doc)s";
    };
"""
        code %= { "name": self.struct_name, "doc":self.doc, "decl": "// decl" }
        return code

    def render_method_struct(self):
        code = "static PyMethodDef %s[] =\n{\n" % self.method_struct_name
        for i in self.functions:
            code += "    " + i.render_cpp_struct_entry(self.prefix)
        code += "\n    { NULL, NULL, 0, NULL }\n}"
        return code

    def render_type_struct(self):
        dic = {}
        for i in TYPE_STRUCT_MEMBER:
            dic[i[1]] = "NULL"
        dic.update({
            "tp_name": '"%s"' % self.name,
            "tp_basicsize": "sizeof(%s)" % self.struct_name,
            "tp_dealloc": "%s::dealloc" % self.struct_name,
            "tp_getattro": "PyObject_GenericGetAttr",
            "tp_setattro": "PyObject_GenericSetAttr",
            "tp_flags": "Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE",
            "tp_doc": "%s::doc_string" % self.struct_name,
            "tp_methods": self.method_struct_name,
            "tp_new": "%s::new_func" % self.struct_name,
            "tp_init": "%s::init_func" % self.struct_name,
        })

        code = "static PyTypeObject %s =\n{\n    PyVarObject_HEAD_INIT(NULL, 0),\n" % self.type_def_struct_name
        for i in TYPE_STRUCT_MEMBER:
            code += "    /* %(name)s */ static_cast<%(type)s>(%(val)s),\n" % {
                "name": i[1], "type": i[0], "val": dic.get(i[1])
            }
        code += "}; /* %s */\n" % self.type_def_struct_name
        return code


class Objects:
    def __init__(self, module):
        self.functions = []
        self.classes = []
        self.name = module.__name__
        self.struct_name = "cppy_module_%s" % self.name
        self.method_struct_name = "cppy_module_methods_%s" % self.name
        self.doc = inspect.getdoc(module)

    def append(self, o):
        if isinstance(o, Function):
            self.functions.append(o)
        elif isinstance(o, Class):
            self.classes.append(o)

    def dump(self):
        print("# -- global functions --")
        for i in self.functions:
            print(i)
        print("# -- global classes --")
        for i in self.classes:
            print(i)

    def render_cpp_to_file(self, filename):
        code = self.render_cpp()
        import codecs
        with codecs.open(filename, "w", "utf-8") as file:
            file.write(code)

    def render_cpp(self):
        code = """
#include <python3.4/Python.h>
#include <python3.4/structmember.h>

#include <iostream>
#define CPPY_ERROR(arg__) { std::cerr << arg__ << std::endl; }

bool cppy_init_python_object(PyObject* module, PyTypeObject* type, const char* name)
{
    if (0 != PyType_Ready(type))
    {
        CPPY_ERROR("Failed to readify " << name << " for Python 3.4");
        return false;
    }

    PyObject* object = reinterpret_cast<PyObject*>(type);
    Py_INCREF(object);
    if (0 != PyModule_AddObject(module, name, object))
    {
        Py_DECREF(object);
        CPPY_ERROR("Failed to add " << name << " to Python 3.4 module");
        return false;
    }
    return true;
}

namespace {
"""
        if self.functions:
            code += "\n/* #################### global functions ##################### */\n\n"
            code += 'extern "C" {\n'
            for i in self.functions:
                code += i.render_cpp_declaration()
            code += "\n" + self.render_method_struct()
            code += '} // extern "C"\n'

        if self.classes:
            for i in self.classes:
                code += "\n/* #################### class %s ##################### */\n\n" % i.name
                code += i.render_cpp_declaration()

        code += """
} // namespace

"""
        return code

    def render_module_def(self):
        code = """
        static const char* %(doc_name)s = "%doc";
        static PyModuleDef %(struct_name)s =
        {
            PyModuleDef_HEAD_INIT,
            "%(name)s",
            %(doc_name)s,
            -1, /* m_size */
            reinterpret_cast<PyMethodDef*>(%(func_struct)s), /* m_methods */
            nullptr, /* m_reload */
            nullptr, /* m_traverse */
            nullptr, /* m_clear */
            nullptr, /* m_free */
        };
        """
        code %= { "name": self.name,
                  "doc_name": "%s_doc" % self.struct_name,
                  "func_struct": self.method_struct_name,
                  "doc": self.doc }
        return code

    def render_method_struct(self):
        code = "static PyMethodDef %s[] =\n{\n" % self.method_struct_name
        for i in self.functions:
            code += "    " + i.render_cpp_struct_entry()
        code += "\n    { NULL, NULL, 0, NULL }\n}"
        return code



class _compiler:

    def __init__(self):
        self.scope_stack = []

    def log(self, str):
        print("  " * len(self.scope_stack) + str)

    def scope_name(self):
        return self.scope_stack[-1] if self.scope_stack else ""

    def full_scope_name(self, name):
        r = ""
        for i in self.scope_stack:
            r += i + "."
        return r + name

    def push_scope(self, name):
        self.scope_stack.append(name)
    def pop_scope(self):
        self.scope_stack.pop()

    def inspect_module(self, module):
        self.objects = Objects(module)
        mod_name = module.__name__
        self.log("inspect module '%s'" % mod_name)
        self.push_scope(mod_name)
        self.inspect_names(module, dir(module))
        self.pop_scope()

    def inspect_names(self, parent, names):
        self.log("scanning names in %s" % type(parent))
        self.push_scope(str(type(parent)))
        for name in names:
            try:
                #print(self.full_scope_name(name))
                o = eval("parent.%s" % name)
            except BaseException as e:
                self.log("EXCEPTION %s" % e)
                continue
            if inspect.isfunction(o):
                self.inspect_function(o)
            elif inspect.isclass(o):
                self.inspect_class(o)

        self.pop_scope()

    def inspect_function(self, func, class_obj=None):
        self.log("inspecting function %s" % func)
        self.push_scope(func.__name__)
        o = Function(func)
        if class_obj is None:
            self.objects.append(o)
        else:
            class_obj.append(o)
        self.pop_scope()

    def inspect_class(self, cls):
        self.log("inspecting class %s" % cls)
        self.push_scope(cls.__name__)
        class_obj = Class(
            name = cls.__name__,
            doc=inspect.getdoc(cls),
        )
        #for i in inspect.getmembers(cls):
        #    print(i)
        for n, mem in inspect.getmembers(cls):
            if inspect.isfunction(mem):
                self.inspect_function(mem, class_obj)
        #self.inspect_names(cls)
        self.objects.append(class_obj)
        self.pop_scope()




def compile(module):
    """
    Scans the module and returns an cppy.Objects class
    :param module: a loaded module
    :return: Objects
    """
    if not inspect.ismodule(module):
        raise TypeError("Expected module, got %s" % type(module))

    c = _compiler()
    c.inspect_module(module)
    return c.objects