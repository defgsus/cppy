import inspect
import datetime

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


def to_c_string(text):
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "")
    text = text.replace('"', '\\"')
    return text


class CodeObject:
    def __init__(self, name, doc="", src_pos=""):
        self.name = name
        self.doc = doc if doc else ""
        self.src_pos = src_pos
        self.cpp = ""

        cpp = self.doc.split("_CPP_:")
        if len(cpp) > 1:
            self.doc = cpp[0]
            self.cpp = cpp[1]

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
        self.args = inspect.getargspec(self.func)
        # self.doc += "\n" + str(self.args)

    def get_cpp(self):
        if not self.cpp:
            # return "#error %s not implemented" % self.name
            return "return PyLong_FromLong(23);"
        else:
            return self.cpp

    def render_cpp_declaration(self, prefix="", struct_name=None):
        s = """
    /* %(src_pos)s */
    static const char* %(prefix)s%(name)s_doc = "%(doc)s";
    static PyObject* %(prefix)s%(name)s(%(PyObject)s* self%(args)s)
    {
        %(code)s
    }
    """
        return s % {"prefix":prefix, "name":self.name,
                    "doc": to_c_string(self.doc),
                    "src_pos": self.src_pos, "code": self.get_cpp(),
                    "PyObject": "PyObject" if struct_name is None else struct_name,
                    "args": self.get_args_data()[2]
                    }

    def get_args_data(self):
        if self.args.varargs and len(self.args.varargs):
            return ("PyCFunction", "METH_VARARGS", ", PyObject* args, PyObject* kwargs",)
        if self.args.args and len(self.args.args):
            return ("PyCFunction", "METH_VARARGS", ", PyObject* args", )
        return ("PyNoArgsFunction", "METH_NOARGS", "")


    def render_cpp_struct_entry(self, prefix=""):
        args = self.get_args_data()
        return """{ "%(name)s", reinterpret_cast<PyCFunction>(%(prefix)s%(name)s), %(args)s, %(prefix)s%(name)s_doc },
""" % {"name": self.name,
       "prefix": prefix,
       "args": args[1],
       "func_type": args[0]
       }


class Class(CodeObject):
    def __init__(self, the_class):
        super().__init__(
            name=the_class.__name__,
            doc=inspect.getdoc(the_class)
        )
        self.the_class = the_class
        self.functions = []
        self.prefix = "cppy_classdef_%s_" % self.name
        self.struct_name = "cppy_class_struct_%s" % self.name
        self.method_struct_name = "cppy_method_def_%s" % self.name
        self.type_def_struct_name = "cppy_type_def_%s" % self.name

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
        code += "\n" + self.render_ctor_impl()
        code += '\n} // extern "C"\n'
        code += "\n" + self.render_init_func()

        return code

    def render_struct(self):
        code = """
    /* base class definition for class '%(name)s' */
    struct %(struct_name)s
    {
        PyObject_HEAD
        %(decl)s
    };
    static const char* %(struct_name)s_doc_string = "%(doc)s";
    static PyObject* %(struct_name)s_new_func(struct _typeobject *, PyObject *, PyObject *);
    static int %(struct_name)s_init_func(PyObject*, PyObject*, PyObject*);
    //static void %(struct_name)s_copy_func(%(struct_name)s*);
    static void %(struct_name)s_dealloc(PyObject* self);
"""
        code %= {
            "name": self.name,
            "struct_name": self.struct_name,
            "doc":to_c_string(self.doc),
            "decl": "\n// decl" }
        return code

    def render_method_struct(self):
        code = "static PyMethodDef %s[] =\n{\n" % self.method_struct_name
        for i in self.functions:
            code += "    " + i.render_cpp_struct_entry(self.prefix)
        code += "\n    { NULL, NULL, 0, NULL }\n};\n"
        return code

    def scoped_name(self):
        return "%s.%s" % (self.the_class, self.name)

    def render_type_struct(self):
        dic = {}
        for i in TYPE_STRUCT_MEMBER:
            dic[i[1]] = "NULL"
        dic.update({
            "tp_name": '"%s"' % self.scoped_name(),
            "tp_basicsize": "sizeof(%s)" % self.struct_name,
            "tp_dealloc": "%s_dealloc" % self.struct_name,
            "tp_getattro": "PyObject_GenericGetAttr",
            "tp_setattro": "PyObject_GenericSetAttr",
            "tp_flags": "Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE",
            "tp_doc": "%s_doc_string" % self.struct_name,
            "tp_methods": self.method_struct_name,
            "tp_new": "%s_new_func" % self.struct_name,
            "tp_init": "%s_init_func" % self.struct_name,
        })

        code = """
/* type definition for class %(name)s */
static PyTypeObject %(struct_name)s =
{
    PyVarObject_HEAD_INIT(NULL, 0)
""" % { "name": self.name, "struct_name":self.type_def_struct_name }

        for i in TYPE_STRUCT_MEMBER:
            code += "    /* %(name)s */ static_cast<%(type)s>(%(val)s),\n" % {
                "name": i[1], "type": i[0], "val": dic.get(i[1])
            }
        code += "}; /* %s */\n" % self.type_def_struct_name
        return code

    def render_ctor_impl(self):
        code = """
    PyObject* %(struct_name)s_new_func(struct _typeobject *, PyObject *, PyObject *)
    {
        return reinterpret_cast<PyObject*>(
            PyObject_New(%(struct_name)s, &%(type_struct)s)
            );
    }
    int %(struct_name)s_init_func(PyObject*, PyObject*, PyObject*) { }
    /*void %(struct_name)s_copy_func(%(struct_name)s* other)
    {
        auto copy = reinterpret_cast<PyObject*>(
            PyObject_New(%(struct_name)s, &%(type_struct)s)
            );
        // decl
        return copy
    }*/
    void %(struct_name)s_dealloc(PyObject* self)
    {
        self->ob_type->tp_free(self);
    }
"""
        code %= {
            "name": self.name,
            "struct_name": self.struct_name,
            "type_struct": self.type_def_struct_name
        }
        return code

    def render_init_func(self):
        code = """
bool initialize_class_%(name)s(void* vmodule)
{
    PyObject* module = reinterpret_cast<PyObject*>(vmodule);

    if (0 != PyType_Ready(&%(struct_name)s))
    {
        CPPY_ERROR("Failed to readify class %(name)s for Python 3.4 module");
        return false;
    }

    PyObject* object = reinterpret_cast<PyObject*>(&%(struct_name)s);
    Py_INCREF(object);
    if (0 != PyModule_AddObject(module, "%(name)s", object))
    {
        Py_DECREF(object);
        CPPY_ERROR("Failed to add class %(name)s to Python 3.4 module");
        return false;
    }
    return true;
}
"""
        code %= {
            "name": self.name,
            "struct_name": self.type_def_struct_name
        }
        return code

class Objects:
    def __init__(self, module):
        self.module = module
        self.functions = []
        self.classes = []
        self.name = module.__name__
        self.struct_name = "cppy_module_%s" % self.name
        self.method_struct_name = "cppy_module_methods_%s" % self.name
        self.doc = inspect.getdoc(module)
        self.h_header=""
        self.h_footer=""
        self.cpp_header=""
        self.cpp_footer=""

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

    @classmethod
    def write_to_file(self, filename, code):
        import codecs
        with codecs.open(filename, "w", "utf-8") as file:
            file.write(code)

    def render_hpp(self):
        code = """
/* generated by cppy on %(date)s */

%(header)s

%(init_types)s

/* Call this before Py_Initialize() */
bool initialize_module_%(name)s();

%(footer)s
"""
        init_types = ""
        for i in self.classes:
            init_types += "bool initialize_class_%s(void* pyObject_module);\n" % i.name
        code %= { "name":self.name, "header":self.h_header, "footer":self.h_footer,
                  "date":datetime.datetime.now(),
                  "init_types":init_types}
        return code


    def render_cpp(self):
        code = """
#include <python3.4/Python.h>
#include <python3.4/structmember.h>

#include <iostream>
#define CPPY_ERROR(arg__) { std::cerr << arg__ << std::endl; }

%(header)s

namespace {
"""
        code %= {"header":self.cpp_header }

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

        code += '\nextern "C" {\n'
        code += self.render_module_def()
        code += '} // extern "C"\n'
        code += "\n} // namespace\n"
        code += "\n" + self.render_module_init()
        code += "\n" + self.cpp_footer
        return code

    def render_module_init(self):
        code = """
namespace {
    PyMODINIT_FUNC create_module_func()
    {
        auto module = PyModule_Create(&%(module_def)s);
        if (!module)
            return nullptr;

        // add the classes
%(init_calls)s

        return module;
    }
} // namespace

bool initialize_module_%(name)s()
{
    PyImport_AppendInittab("%(name)s", create_module_func);
    return true;
}
"""
        init_calls = ""
        for i in self.classes:
            init_calls += "        initialize_class_%s(module);\n" % i.name

        code %= {
            "name": self.name,
            "module_def": self.struct_name,
            "init_calls": init_calls
        }

        return code

    def render_module_def(self):
        code = """
        static const char* %(doc_name)s = "%(doc)s";
        /* module definition for '%(name)s' */
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
        """ % { "name": self.name,
                  "struct_name": self.struct_name,
                  "doc_name": "%s_doc" % self.struct_name,
                  "func_struct": self.method_struct_name,
                  "doc": to_c_string(self.doc) }
        return code

    def render_method_struct(self):
        code = "static PyMethodDef %s[] =\n{\n" % self.method_struct_name
        for i in self.functions:
            code += "    " + i.render_cpp_struct_entry()
        code += "\n    { NULL, NULL, 0, NULL }\n};\n"
        return code



class _compiler:
    """
    Class responsible to traverse a module and it's members
    and to generate an Objects instance from it
    """
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
        class_obj = Class(cls)
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