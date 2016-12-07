import inspect
import datetime
from .c_types import *
from .renderer import *

class CodeObject:
    """Base class of python things that have a cpp representation"""
    def __init__(self, name, doc="", src_pos=""):
        self.name = name
        self.doc = doc if doc else ""
        self.src_pos = src_pos
        self.cpp = ""
        self.indent_level = 0
        self.module = None

        cpp = self.doc.split("_CPP_:")
        if len(cpp) > 1:
            self.doc = cpp[0]
            self.cpp = cpp[1]

    def __str__(self):
        return "%s" % self.name

    def push_indent(self): self.indent_level += 1
    def pop_indent(self):
        if self.indent_level <= 0:
            raise RuntimeWarning("pop_indent() called without push")
        self.indent_level -= 1

    def indent(self):
        return INDENT * self.indent_level
    def newline(self):
        return "\n" + self.indent()

    def get_cpp(self):
        code = self.cpp
        return indent_code(code, self.indent() + INDENT)

    def render_cpp_declaration(self):
        raise NotImplementedError



class Function(CodeObject):
    def __init__(self, func, for_class):
        super().__init__(
            name=func.__name__,
            doc=inspect.getdoc(func),
            src_pos="%s:%d" % (func.__code__.co_filename, func.__code__.co_firstlineno),
        )
        if not self.cpp:
            #self.cpp = "#error %s not implemented" % self.name
            self.cpp = "Py_RETURN_NOTIMPLEMENTED;"

        self.func = func
        self.args = inspect.getargspec(self.func)
        self.for_class = for_class
        self.prefix = "cppy_classmethod_%s_" % for_class.name
        # self.doc += "\n" + str(self.args)

    def get_func_name(self):
        return "%s%s" % (self.prefix, self.name)

    def get_return_type(self):
        return SPECIAL_RETURN_TYPES.get(self.name, "PyObject*")

    def render_cpp_declaration(self, struct_name=None):
        s = """
%(indent)s/* %(src_pos)s */
%(indent)s/* %(debug)s */
%(indent)sstatic const char* %(prefix)s%(name)s_doc = "%(doc)s";
%(indent)sstatic %(return)s %(prefix)s%(name)s(%(PyObject)s* self%(args)s)
%(indent)s{
%(code)s
%(indent)s}
"""
        return s % {"indent": self.indent(),
                    "prefix": self.prefix,
                    "name": self.name,
                    "return": self.get_return_type(),
                    "doc": to_c_string(self.doc),
                    "src_pos": self.src_pos,
                    "code": self.get_cpp(),
                    "PyObject": "PyObject" if struct_name is None else struct_name,
                    "args": SPECIAL_ARGUMENTS.get(self.name, self.get_args_data()[2]),
                    "debug": str(self.args)
                    }

    def get_args_data(self):
        if self.args.varargs and len(self.args.varargs):
            return ("PyFunctionWithKeywords", "METH_VARARGS", ", PyObject* args, PyObject* kwargs",)

        if self.for_class:
            if self.name == "__init__":
                return ("PyFunctionWithKeywords", "METH_VARARGS", ", PyObject* args, PyObject* kwargs",)
            num_args = len(self.args.args)
            if not num_args:
                raise TypeError("class method %s has no parameters" % self.name)
            if num_args == 1:
                return ("PyCFunction", "METH_NOARGS", "",)
            else:
                return ("PyCFunction", "METH_VARARGS", ", PyObject* args",)

        if len(self.args.args) == 1:
            return ("PyCFunction", "METH_O", ", PyObject* arg", )
        if len(self.args.args) > 1:
            return ("PyCFunction", "METH_VARARGS", ", PyObject* args",)

        return ("PyNoArgsFunction", "METH_NOARGS", "")


    def render_cpp_struct_entry(self):
        args = self.get_args_data()
        return """/* %(debug)s */{ "%(name)s", reinterpret_cast<PyCFunction>(%(funcname)s), %(args)s, %(funcname)s_doc },
""" % {
            "name": self.name,
            "funcname": self.get_func_name(),
            "args": args[1],
            "func_type": args[0],
            "debug": str(self.args)
       }





class Class(CodeObject):
    def __init__(self, the_class):
        super().__init__(
            name=the_class.__name__,
            doc=inspect.getdoc(the_class)
        )
        self.the_class = the_class
        self.functions = []
        self.class_struct_name = "%s_struct" % self.name
        self.type_struct_name = "%s_type_struct" % self.name
        self.method_struct_name = "%s_method_struct" % self.name
        self.number_struct_name = "%s_number_struct" % self.name
        self.mapping_struct_name = "%s_mapping_struct" % self.name
        self.sequence_struct_name = "%s_sequence_struct" % self.name

    def append(self, o):
        if isinstance(o, Function) and o.cpp:
            self.functions.append(o)

    def has_function(self, name):
        for i in self.functions:
            if i.name == name:
                return True
        return False

    def get_function(self, name):
        for i in self.functions:
            if i.name == name:
                return i
        return None

    def has_sequence_function(self):
        for i in SEQUENCE_FUNCS:
            if self.has_function(i[0]):
                return True
        return False

    def has_number_function(self):
        for i in NUMBER_FUNCS:
            if self.has_function(i[0]):
                return True
        return False

    def render_cpp_declaration(self):
        code = ""
        code += self.indent() + 'extern "C" {'
        self.push_indent()
        code += "\n" + self.render_class_struct()
        for i in self.functions:
            i.indent_level = self.indent_level
            code += i.render_cpp_declaration(struct_name=self.class_struct_name)
        code += "\n" + self.render_method_struct()
        if self.has_sequence_function():
            code += "\n" + self.render_sequence_struct()
        if self.has_number_function():
            code += "\n" + self.render_number_struct()
        code += "\n" + self.render_type_struct()
        code += "\n" + self.render_ctor_impl()
        self.pop_indent()
        code += '\n} // extern "C"\n'
        code += "\n" + self.render_init_func()

        return code

    def render_forwards(self):
        code = """struct %s;\n""" % self.class_struct_name
        return code

    def render_class_struct(self):
        code = """
    /* class '%(name)s' */
    struct %(struct_name)s
    {
        PyObject_HEAD
%(decl)s
    };
    static const char* %(struct_name)s_doc_string = "%(doc)s";
    static PyObject* %(struct_name)s_new_func(struct _typeobject *, PyObject *, PyObject *);
    //static int %(struct_name)s_init_func(PyObject*, PyObject*, PyObject*);
    //static void %(struct_name)s_copy_func(%(struct_name)s*);
    static void %(struct_name)s_dealloc(PyObject* self);
"""
        code %= {
            "name": self.name,
            "struct_name": self.class_struct_name,
            "doc": to_c_string(self.doc),
            "decl": self.get_cpp() }
        return code

    def render_method_struct(self):
        code = "static PyMethodDef %s[] =\n{\n" % self.method_struct_name
        for i in self.functions:
            add_here = True
            #for j in SPECIAL_FUNCS:
            #    if i.name == j[0]:
            #        add_here = False
            #        break
            if add_here:
                code += "    " + i.render_cpp_struct_entry()
        code += "\n    { NULL, NULL, 0, NULL }\n};\n"
        return code

    def scoped_name(self):
        return "%s.%s" % (self.the_class.__name__, self.name)

    def render_type_struct(self):
        dic = {}
        for i in PyTypeObject:
            dic[i[0]] = "NULL"
        dic.update({
            "tp_name": '"%s"' % self.scoped_name(),
            "tp_basicsize": "sizeof(%s)" % self.class_struct_name,
            "tp_dealloc": "%s_dealloc" % self.class_struct_name,
            "tp_getattro": "PyObject_GenericGetAttr",
            "tp_setattro": "PyObject_GenericSetAttr",
            "tp_flags": "Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE",
            "tp_doc": "%s_doc_string" % self.class_struct_name,
            "tp_methods": self.method_struct_name,
            "tp_new": "%s_new_func" % self.class_struct_name,
            # "tp_init": "%s_init_func" % self.struct_name,
        })
        for i in SPECIAL_FUNCS:
            if self.has_function(i[0]):
                dic.update({ i[1]: self.get_function(i[0]).get_func_name() })
        if self.has_sequence_function():
            dic.update({"tp_as_sequence": "&" + self.sequence_struct_name})
        if self.has_number_function():
            dic.update({"tp_as_number": "&" + self.number_struct_name})

        return render_struct("PyTypeObject", PyTypeObject,
                             self.type_struct_name, dic,
                             first_line="PyVarObject_HEAD_INIT(NULL, 0)")

    def render_mapping_struct(self):
        dic = {
            "mp_length" : self.has_function("__get")
        }
        code = """
        static PyMappingMethods cppy_mapping_%(name)s[] =
        {
            (lenfunc)%(mp_length)s,
            (binaryfunc)%(mp_subscript)s,
            (objobjargproc)%(mp_ass_subscript)s
        };
        """

    def render_sequence_struct(self):
        dic = { "name": self.name }
        for i in SEQUENCE_FUNCS:
            val = "nullptr"
            if self.has_function(i[0]):
                val = self.get_function(i[0]).get_func_name()
            dic.update({ i[1]: val })

        return render_struct("PySequenceMethods", PySequenceMethods,
                             self.sequence_struct_name, dic)
    
    def render_number_struct(self):
        dic = {}
        for i in NUMBER_FUNCS:
            val = "nullptr"
            if self.has_function(i[0]):
                val = self.get_function(i[0]).get_func_name()
            dic.update({i: val})
        return render_struct("PyNumberMethods", PyNumberMethods,
                             self.number_struct_name, dic)


    def render_ctor_impl(self):
        code = """
    PyObject* %(struct_name)s_new_func(struct _typeobject *, PyObject *, PyObject *)
    {
        return reinterpret_cast<PyObject*>(
            PyObject_New(%(struct_name)s, &%(type_struct)s)
            );
    }
    //int %(struct_name)s_init_func(PyObject*, PyObject*, PyObject*) { return 0; }
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
            "struct_name": self.class_struct_name,
            "type_struct": self.type_struct_name
        }
        return code

    def render_init_func(self):
        code = """
%(indent)sbool initialize_class_%(name)s(void* vmodule)
%(indent)s{
%(indent)s    PyObject* module = reinterpret_cast<PyObject*>(vmodule);

%(indent)s    if (0 != PyType_Ready(&%(struct_name)s))
%(indent)s    {
%(indent)s        CPPY_ERROR("Failed to readify class %(name)s for Python 3.4 module");
%(indent)s        return false;
%(indent)s    }

%(indent)s    PyObject* object = reinterpret_cast<PyObject*>(&%(struct_name)s);
%(indent)s    Py_INCREF(object);
%(indent)s    if (0 != PyModule_AddObject(module, "%(name)s", object))
%(indent)s    {
%(indent)s        Py_DECREF(object);
%(indent)s        CPPY_ERROR("Failed to add class %(name)s to Python 3.4 module");
%(indent)s        return false;
%(indent)s    }
%(indent)s    return true;
%(indent)s}
"""
        code %= {
            "indent": self.indent(),
            "name": self.name,
            "struct_name": self.type_struct_name
        }
        return code



class Module:
    def __init__(self, module):
        self.module = module
        self.functions = []
        self.classes = []
        self.name = module.__name__
        self.struct_name = "cppy_module_%s" % self.name
        self.method_struct_name = "cppy_module_methods_%s" % self.name
        self.doc = inspect.getdoc(module)
        self.doc = self.doc if self.doc else ""
        self.namespaces = []
        self.h_header=""
        self.h_footer=""
        self.cpp_header=""
        self.cpp_footer=""
        self.cpp = ""
        self.cpp2 = ""
        cpp = self.doc.split("_CPP_:")
        if len(cpp) > 1:
            self.doc = cpp[0]
            self.cpp = cpp[1]
            if len(cpp) > 2:
                self.cpp2 = cpp[2]

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
%(namespace_open)s

%(init_types)s

/* Call this before Py_Initialize() */
bool initialize_module_%(name)s();

%(namespace_close)s
%(footer)s
"""
        init_types = ""
        for i in self.classes:
            init_types += "bool initialize_class_%s(void* pyObject_module);\n" % i.name
        code %= { "name":self.name, "header":self.h_header, "footer":self.h_footer,
                  "date":datetime.datetime.now(),
                  "init_types":init_types,
                  "namespace_open": self.render_namespace_open(),
                  "namespace_close": self.render_namespace_close(),
                  }
        return code


    def render_cpp(self):
        code = """
#include <python3.4/Python.h>
#include <python3.4/structmember.h>

#include <iostream>
#define CPPY_ERROR(arg__) { std::cerr << arg__ << std::endl; }

%(static_asserts)s

%(namespace_open)s
namespace {
extern "C" {
%(forwards)s
} // extern "C"
} // namespace
%(namespace_close)s

%(decl)s

%(header)s

%(namespace_open)s
namespace {
"""
        code %= {
            "static_asserts" : self.render_static_asserts(),
            "header": self.format_cpp(self.cpp_header),
            "decl": self.format_cpp(self.cpp),
            "forwards": self.render_forwards(),
            "namespace_open": self.render_namespace_open(),
            "namespace_close": self.render_namespace_close(),
        }

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

        if self.cpp2:
            code += "\n" + self.format_cpp(self.cpp2) + "\n"

        code += '\nextern "C" {\n'
        code += self.render_module_def()
        code += '} // extern "C"\n'
        code += "\n} // namespace\n"
        code += "\n" + self.render_module_init()
        code += "\n" + self.render_namespace_close()
        code += "\n" + self.cpp_footer
        return code

    def format_cpp(self, code):
        code1 = ""
        prev = 0
        import re
        for i in re.finditer(r"\$([A-Z_]+)\(([A-Za-z_][A-Za-z_0-9]*)\)", code):
            span = i.span()
            code1 += code[prev:span[0]]
            prev = span[1]
            code1 += self.get_template_arg(i.groups()[0], i.groups()[1])
        code1 += code[prev:]
        code = code1
        return code

    def get_template_arg(self, type, name):
        if type == "STRUCT":
            for i in self.classes:
                if i.name == name:
                    return i.class_struct_name
            raise ValueError("$STRUCT for %s not known" % name)
        if type == "TYPE_STRUCT":
            for i in self.classes:
                if i.name == name:
                    return i.type_struct_name
            raise ValueError("$TYPE_STRUCT for %s not known" % name)
        raise ValueError("Unknown $ template call '" % type)

    def render_static_asserts(self):
        code = "#include <type_traits>\n"
        for functype in FUNCTIONS:
            params = FUNCTIONS[functype]
            parstr = params[1][0]
            for j in range(1, len(params[1])):
                parstr += ", %s" % params[1][j]
            typedef = "%(ret)s(*)(%(params)s)" % { "ret": params[0], "params": parstr }
            code += 'static_assert(std::is_same<%s,\n    %s>::value, "cppy/python api mismatch");\n' % (functype, typedef)
        return code

    def render_forwards(self):
        code = ""
        for i in self.classes:
            code += "\n" + i.render_forwards()
        return code

    def render_namespace_open(self):
        code = ""
        for i in self.namespaces:
            code += "namespace %s {\n" % i
        return code

    def render_namespace_close(self):
        code = ""
        for i in reversed(self.namespaces):
            code += "} // namespace %s\n" % i
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
            %(methods)s, /* m_methods */
            nullptr, /* m_reload */
            nullptr, /* m_traverse */
            nullptr, /* m_clear */
            nullptr, /* m_free */
        };
        """
        dic = { "name": self.name,
                "struct_name": self.struct_name,
                "doc_name": "%s_doc" % self.struct_name,
                "methods" : "nullptr",
                "doc": to_c_string(self.doc) }
        if len(self.functions):
            dic.update({ "methods": "reinterpret_cast<PyMethodDef*>(%s)" % self.method_struct_name})
        code %= dic
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
    and to generate an Module instance from it
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
        self.objects = Module(module)
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
        o = Function(func, class_obj)
        if class_obj is None:
            self.objects.append(o)
        else:
            class_obj.append(o)
        self.pop_scope()

    def inspect_class(self, cls):
        self.log("inspecting class %s" % cls)
        self.push_scope(cls.__name__)
        class_obj = Class(cls)
        for n, mem in inspect.getmembers(cls):
            if inspect.isfunction(mem):
                self.inspect_function(mem, class_obj)
        #self.inspect_names(cls)
        self.objects.append(class_obj)
        self.pop_scope()




def compile(module):
    """
    Scans the module and returns an cppy.Module class
    :param module: a loaded module
    :return: a Module instance
    """
    if not inspect.ismodule(module):
        raise TypeError("Expected module, got %s" % type(module))

    c = _compiler()
    c.inspect_module(module)
    return c.objects


if __name__ == "__main__":
    pass
    #print("TYPE_STRUCT_MEMBER = [")
    #for i in TYPE_STRUCT_MEMBER:
    #    print('    ("%s", "%s"),' % (i[1], i[0]))
    #print("]")
