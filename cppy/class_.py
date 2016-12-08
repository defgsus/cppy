import inspect
from .function import *
from .renderer import *

class Class(CodeObject):
    """A python c-api implementation of a class"""
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
        self.class_new_func_name = "cppy_new_%s" % self.class_struct_name
        self.class_dealloc_func_name = "cppy_dealloc_%s" % self.class_struct_name

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
        """Renders the complete cpp code to define the class and it's functions"""
        code = ""
        code += self.indent() + 'extern "C" {'
        self.push_indent()
        code += "\n" + self.render_class_struct()
        for i in self.functions:
            code += i.render_cpp_declaration(struct_name=self.class_struct_name)
        code += "\n" + self.render_method_struct()
        if self.has_sequence_function():
            code += "\n" + self.render_sequence_struct()
        if self.has_number_function():
            code += "\n" + self.render_number_struct()
        code += "\n" + self.render_type_struct()
        code += "\n" + self.render_ctor_impl()
        self.pop_indent()
        code += self.indent() + '\n} // extern "C"\n'
        code += self.indent() + "\n" + self.render_init_func()

        return code

    def render_forwards(self):
        code = """struct %s;\n""" % self.class_struct_name
        return self.format_code(code)

    def render_class_struct(self):
        code = """
        /* class '%(name)s' */
        struct %(struct_name)s
        {
            PyObject_HEAD
%(decl)s
        };
        static PyObject* %(new_func)s(struct _typeobject *, PyObject *, PyObject *);
        static void %(dealloc_func)s(PyObject* self);
        //static void %(struct_name)s_copy_func(%(struct_name)s*);
        static const char* %(struct_name)s_doc_string = "%(doc)s";
"""
        code %= {
            "name": self.name,
            "struct_name": self.class_struct_name,
            "new_func": self.class_new_func_name,
            "dealloc_func": self.class_dealloc_func_name,
            "doc": to_c_string(self.doc),
            "decl": change_text_indent(self.cpp, 12) }
        return self.format_code(code)

    def render_method_struct(self):
        code = "static PyMethodDef %s[] =\n{\n" % self.method_struct_name
        for i in self.functions:
            add_here = True
            # for j in SPECIAL_FUNCS:
            #    if i.name == j[0]:
            #        add_here = False
            #        break
            if add_here:
                code += "    " + i.render_cpp_member_struct_entry()
        code += "\n    { NULL, NULL, 0, NULL }\n};\n"
        return self.format_code(code)

    def scoped_name(self):
        return "%s.%s" % (self.the_class.__name__, self.name)

    def render_type_struct(self):
        dic = {}
        for i in PyTypeObject:
            dic[i[0]] = "NULL"
        dic.update({
            "tp_name": '"%s"' % self.scoped_name(),
            "tp_basicsize": "sizeof(%s)" % self.class_struct_name,
            "tp_dealloc": self.class_dealloc_func_name,
            "tp_getattro": "PyObject_GenericGetAttr",
            "tp_setattro": "PyObject_GenericSetAttr",
            "tp_flags": "Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE",
            "tp_doc": "%s_doc_string" % self.class_struct_name,
            "tp_methods": self.method_struct_name,
            "tp_new": self.class_new_func_name
        })
        for i in TYPE_FUNCS:
            if self.has_function(i[0]):
                dic.update({i[1]: self.get_function(i[0]).func_name})
        if self.has_sequence_function():
            dic.update({"tp_as_sequence": "&" + self.sequence_struct_name})
        if self.has_number_function():
            dic.update({"tp_as_number": "&" + self.number_struct_name})

        return self.format_code(
                render_struct("PyTypeObject", PyTypeObject,
                             self.type_struct_name, dic,
                             first_line="PyVarObject_HEAD_INIT(NULL, 0)") )

    def render_mapping_struct(self):
        pass

    def render_sequence_struct(self):
        dic = dict()
        for i in SEQUENCE_FUNCS:
            if self.has_function(i[0]):
                val = self.get_function(i[0]).func_name
                dic.update({i[1]: val})

        return self.format_code(render_struct("PySequenceMethods", PySequenceMethods,
                             self.sequence_struct_name, dic))

    def render_number_struct(self):
        dic = {}
        for i in NUMBER_FUNCS:
            if self.has_function(i[0]):
                val = self.get_function(i[0]).func_name
                dic.update({i[1]: val})
        return self.format_code(render_struct("PyNumberMethods", PyNumberMethods,
                             self.number_struct_name, dic))

    def render_ctor_impl(self):
        code = """
        /* create new instance of %(name)s class */
        PyObject* %(new_func)s(struct _typeobject *, PyObject* arg1, PyObject* arg2)
        {
            return reinterpret_cast<PyObject*>(
                PyObject_New(%(struct_name)s, &%(type_struct)s)
                );
        }
        void %(dealloc_func)s(PyObject* self)
        {
            self->ob_type->tp_free(self);
        }
        /*void %(struct_name)s_copy_func(%(struct_name)s* other)
        {
            auto copy = reinterpret_cast<PyObject*>(
                PyObject_New(%(struct_name)s, &%(type_struct)s)
                );
            // decl
            return copy
        }*/
"""
        code %= {
            "name": self.name,
            "struct_name": self.class_struct_name,
            "new_func": self.class_new_func_name,
            "dealloc_func": self.class_dealloc_func_name,
            "type_struct": self.type_struct_name
        }
        return self.format_code(code)

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
            "indent": self.indent(),
            "name": self.name,
            "struct_name": self.type_struct_name
        }
        return self.format_code(code)

