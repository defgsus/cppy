import inspect
from .function_ import *
from .renderer import *

class Class(CodeObject):
    """A python c-api implementation of a class"""
    def __init__(self, the_class):
        super().__init__(
            name=the_class.__name__,
            doc=inspect.getdoc(the_class)
        )
        self.the_class = the_class
        self.bases = []
        self.functions = []
        self.properties = []
        self.class_struct_name = "%s_struct" % self.name
        self.type_struct_name = "%s_type_static_mem" % self.name
        self.method_struct_name = "%s_method_struct" % self.name
        self.number_struct_name = "%s_number_struct" % self.name
        self.mapping_struct_name = "%s_mapping_struct" % self.name
        self.sequence_struct_name = "%s_sequence_struct" % self.name
        self.getset_struct_name = "%s_getset_struct" % self.name
        self.class_new_func_name = "cppy_new_%s" % self.class_struct_name
        self.class_copy_func_name = "cppy_copy_%s" % self.class_struct_name
        self.class_dealloc_func_name = "cppy_dealloc_%s" % self.class_struct_name
        self.class_is_instance_func_name = "cppy_is_instance_%s" % self.class_struct_name

    @property
    def all_objects(self):
        return self.functions + self.properties


    def has_cpp(self, key=None):
        for i in self.bases:
            if i.has_cpp(key):
                return True
        return super(Class, self).has_cpp(key)

    def cpp(self, key=None, formatted=True):
        cpp = ""
        for i in self.bases:
            cpp += i.cpp(key, False) + "\n"
        cpp += "\n" + super(Class, self).cpp(key, False)
        if formatted:
            cpp = self.format_code(cpp)
        return cpp

    def append(self, o):
        if isinstance(o, Function):
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

    def render_forward_decl(self):
        code = """
        /* %(name)s forward decl */
        struct %(struct_name)s;
        static %(struct_name)s* %(new_func)s(struct _typeobject *, PyObject *, PyObject *);
        static void %(dealloc_func)s(PyObject* self);
        static %(struct_name)s* %(copy_func)s(%(struct_name)s* self);
        static bool %(is_instance_func)s(PyObject* arg);
        """
        code %= {
            "name": self.name,
            "struct_name": self.class_struct_name,
            "new_func": self.class_new_func_name,
            "copy_func": self.class_copy_func_name,
            "dealloc_func": self.class_dealloc_func_name,
            "is_instance_func": self.class_is_instance_func_name,
        }
        for i in self.all_objects:
            code += "\n" + i.render_forward_decl()
        return self.format_code(code)

    def render_impl_decl(self):
        return ""
        #code = ""
        #for i in self.all_objects:
        #    code += "\n" + i.render_impl_decl()
        #return self.format_code(code)

    def render_cpp_declaration(self):
        """Renders the complete cpp code to define the class and it's functions"""
        code = ""
        code += self.indent() + 'extern "C" {'
        self.push_indent()
        code += "\n" + self.render_class_struct()
        if self.functions:
            code += "\n\n/* ---------- %s methods ----------- */\n\n" % self.name
            for i in self.functions:
                code += i.render_cpp_declaration(struct_name=self.class_struct_name)
        if self.properties:
            code += "\n\n/* ---------- %s properties ----------- */\n\n" % self.name
            for i in self.properties:
                code += i.render_cpp_declaration()
        code += "\n\n/* ---------- %s structs ----------- */\n\n" % self.name
        code += "\n" + self.render_method_struct()
        if self.properties:
            code += "\n" + self.render_getset_struct()
        if self.has_sequence_function():
            code += "\n" + self.render_sequence_struct()
        if self.has_number_function():
            code += "\n" + self.render_number_struct()
        code += "\n" + self.render_type_struct()
        code += "\n\n/* ---------- %s ctor/dtor ----------- */\n\n" % self.name
        code += "\n" + self.render_ctor_impl()
        self.pop_indent()
        code += self.indent() + '\n} // extern "C"\n'
        code += self.indent() + "\n" + self.render_init_func()
        for i in self.all_objects:
            c = i.render_impl_decl()
            if c:
                code += "\n" + c

        return code

    def render_class_struct(self):
        code = """
        /* class '%(name)s' */
        struct %(struct_name)s
        {
            PyObject_HEAD
%(decl)s
            void cppy_new()
            {
%(decl_new)s
            }
            void cppy_free()
            {
%(decl_free)s
            }
            void cppy_copy(%(struct_name)s* copy)
            {
                CPPY_UNUSED(copy);
%(decl_copy)s
            }
        };
        static const char* %(struct_name)s_doc_string = "%(doc)s";
""" % {
            "name": self.name,
            "struct_name": self.class_struct_name,
            "doc": to_c_string(self.doc),
            "decl": change_text_indent(self.cpp(), 12),
            "decl_new": change_text_indent(self.cpp("NEW"), 16),
            "decl_free": change_text_indent(self.cpp("FREE"), 16),
            "decl_copy": change_text_indent(self.cpp("COPY"), 16),
        }
        return self.format_code(code)

    def render_method_struct(self):
        code = "static PyMethodDef %s[] =\n{\n" % self.method_struct_name
        for i in self.functions:
            if i.is_normal_function():
                code += "    " + i.render_cpp_member_struct_entry()
        code += "\n    { NULL, NULL, 0, NULL }\n};\n"
        return self.format_code(code)

    def render_getset_struct(self):
        code = "static PyGetSetDef %s[] =\n{\n" % self.getset_struct_name
        for i in self.properties:
            code += "    " + i.render_cpp_getset_struct_entry()
        code += "\n    { NULL, NULL, NULL, NULL, NULL }\n};\n"
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
        if self.properties:
            dic.update({"tp_getset": self.getset_struct_name})

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
        /* ###### class %(name)s ###### */

        /** Creates new instance of %(name)s class.
            @note Original function signature requires to return PyObject*,
            but here we return the actual %(name)s struct for convenience. */
        %(struct_name)s* %(new_func)s(struct _typeobject *, PyObject* , PyObject* )
        {
            auto o = PyObject_New(%(struct_name)s, &%(type_struct)s);
            // Needs to be implemented by user in class %(name)s's cpp annotation
            o->cppy_new();
            return o;
        }

        /** Deletes a %(name)s instance */
        void %(dealloc_func)s(PyObject* self)
        {
            // Needs to be implemented by user in class %(name)s's cpp annotation
            reinterpret_cast<%(struct_name)s*>(self)->cppy_free();
            self->ob_type->tp_free(self);
        }

        /** Makes a copy of the %(name)s instance @p self,
            using user-supplied %(struct_name)s::cppy_copy() */
        %(struct_name)s* %(copy_func)s(%(struct_name)s* self)
        {
            %(struct_name)s* copy = $NEW(%(name)s);
            // Needs to be implemented by user in class %(name)s's cpp annotation
            self->cppy_copy(copy);
            return copy;
        }

        /** Wrapper for type checking after declaration of %(type_struct)s */
        bool %(is_instance_func)s(PyObject* arg)
        {
            return PyObject_TypeCheck(arg, &%(type_struct)s);
        }
"""
        code %= {
            "name": self.name,
            "struct_name": self.class_struct_name,
            "type_struct": self.type_struct_name,
            "new_func": self.class_new_func_name,
            "copy_func": self.class_copy_func_name,
            "dealloc_func": self.class_dealloc_func_name,
            "is_instance_func": self.class_is_instance_func_name,
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

