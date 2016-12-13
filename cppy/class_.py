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
        self.type_struct_name = "%s_type_struct" % self.name
        self.method_struct_name = "%s_method_struct" % self.name
        self.number_struct_name = "%s_number_struct" % self.name
        self.mapping_struct_name = "%s_mapping_struct" % self.name
        self.sequence_struct_name = "%s_sequence_struct" % self.name
        self.getset_struct_name = "%s_getset_struct" % self.name
        self.class_new_func_name = "create_%s" % self.name
        self.class_copy_func_name = "copy_%s" % self.name
        self.class_dealloc_func_name = "destroy_%s" % self.name
        self.class_is_instance_func_name = "is_%s" % self.name

    @property
    def all_objects(self):
        return self.functions + self.properties

    def supported_doc_tags(self):
        return [None, "DEF", "IMPL", "NEW", "COPY", "FREE"]

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

    def render_header_forwards(self):
        """Stuff that needs to be known by all other code in the .h file"""
        return self._render_forward_def()

    def render_header_impl(self):
        """Stuff that implements stuff in the .h file"""
        return self._render_class_struct()

    def render_forwards(self):
        """Stuff that needs to be known by all other code in .cpp file"""
        return ""

    def render_impl(self):
        """Implementation that need final definition of all type structs, etc.."""
        return ""

    def render_python_api(self):
        """The general python c-api constructs"""
        return self._render_cpp_declaration()

    def _render_forward_def(self):
        code = """
        /* %(name)s forward decl */
        struct %(struct_name)s;
        %(struct_name)s* %(new_func)s();
        void %(dealloc_func)s(PyObject* self);
        %(struct_name)s* %(copy_func)s(%(struct_name)s* self);
        bool %(is_instance_func)s(PyObject* arg);
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
            code += "\n" + i.render_forwards()
        return self.format_code(code)

    def _render_cpp_declaration(self):
        """Renders the complete cpp code to define the class and it's functions"""
        code = ""
        code += "\n" + self._render_doc_string()
        code += "\n" + self._render_class_struct_impl()
        if self.functions:
            code += "\n\n/* ---------- %s methods ----------- */\n\n" % self.name
            for i in self.functions:
                code += "\n" + i.render_python_api()
        if self.properties:
            code += "\n\n/* ---------- %s properties ----------- */\n\n" % self.name
            for i in self.properties:
                code += "\n" + i.render_python_api()
        code += "\n\n/* ---------- %s structs ----------- */\n\n" % self.name
        code += "\n" + self._render_method_struct()
        if self.properties:
            code += "\n" + self._render_getset_struct()
        if self.has_sequence_function():
            code += "\n" + self._render_sequence_struct()
        if self.has_number_function():
            code += "\n" + self._render_number_struct()
        code += "\n" + self._render_type_struct()
        code += "\n\n/* ---------- %s ctor/dtor ----------- */\n\n" % self.name
        code += "\n" + self._render_ctor_impl()

        code = apply_string_dict('extern "C" {\n' + INDENT + '%(decl)s\n} // extern "C"\n',
                                 { "decl": code })

        code += "\n" + self._render_init_func()
        for i in self.all_objects:
            c = i.render_impl()
            if c:
                code += "\n" + c

        return code

    def _render_class_struct(self):
        code = """
        /* class '%(name)s' */
        struct %(struct_name)s
        {
            PyObject_HEAD
            %(decl)s

            void cppy_new();
            void cppy_free();
            void cppy_copy(%(struct_name)s* copy);
        };
        """
        code = change_text_indent(code, 0)

        code = apply_string_dict(code, {
            "name": self.name,
            "struct_name": self.class_struct_name,
            "decl": self.cpp() or self.cpp("DEF"),
        })
        return self.format_code(code)

    def _render_class_struct_impl(self):
        code = """

        /* -- '%(name)s' struct member impl -- */
        void %(struct_name)s::cppy_new()
        {
            %(decl_new)s
        }
        void %(struct_name)s::cppy_free()
        {
            %(decl_free)s
        }
        void %(struct_name)s::cppy_copy(%(struct_name)s* copy)
        {
            CPPY_UNUSED(copy);
            %(decl_copy)s
        }
"""
        code = change_text_indent(code, 0)
        code = apply_string_dict(code, {
            "name": self.name,
            "struct_name": self.class_struct_name,
            "decl_new": change_text_indent(self.cpp("NEW"), 12),
            "decl_free": change_text_indent(self.cpp("FREE"), 12),
            "decl_copy": change_text_indent(self.cpp("COPY"), 12),
        })
        return self.format_code(code)

    def _render_method_struct(self):
        code = "static PyMethodDef %s[] =\n{\n" % self.method_struct_name
        for i in self.functions:
            if i.is_normal_function():
                code += INDENT + i.render_member_struct_entry()
        code += "\n" + INDENT + "{ NULL, NULL, 0, NULL }\n};\n"
        return self.format_code(code)

    def _render_getset_struct(self):
        code = "static PyGetSetDef %s[] =\n{\n" % self.getset_struct_name
        for i in self.properties:
            code += INDENT + i.render_cpp_getset_struct_entry()
        code += "\n" + INDENT + "{ NULL, NULL, NULL, NULL, NULL }\n};\n"
        return self.format_code(code)

    def _render_type_struct(self):
        dic = {}
        for i in PyTypeObject:
            dic[i[0]] = "NULL"
        dic.update({
            "tp_name": '"%s.%s"' % (self.context.name, self.name),
            "tp_basicsize": "sizeof(%s)" % self.class_struct_name,
            "tp_dealloc": self.class_dealloc_func_name,
            "tp_getattro": "PyObject_GenericGetAttr",
            "tp_setattro": "PyObject_GenericSetAttr",
            "tp_flags": "Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE",
            "tp_doc": "%s_doc_string" % self.class_struct_name,
            "tp_methods": self.method_struct_name,
            "tp_new": self.class_new_func_name
        })
        if self.bases:
            dic.update({ "tp_base": "&" + self.bases[0].type_struct_name })
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
                "/* https://docs.python.org/3/c-api/typeobj.html */\n" +
                render_struct("PyTypeObject", PyTypeObject,
                             self.type_struct_name, dic,
                             first_line="PyVarObject_HEAD_INIT(NULL, 0)") )

    def _render_mapping_struct(self):
        pass

    def _render_sequence_struct(self):
        dic = dict()
        for i in SEQUENCE_FUNCS:
            if self.has_function(i[0]):
                val = self.get_function(i[0]).func_name
                dic.update({i[1]: val})

        return self.format_code(render_struct("PySequenceMethods", PySequenceMethods,
                             self.sequence_struct_name, dic))

    def _render_number_struct(self):
        dic = {}
        for i in NUMBER_FUNCS:
            if self.has_function(i[0]):
                val = self.get_function(i[0]).func_name
                dic.update({i[1]: val})
        return self.format_code(render_struct("PyNumberMethods", PyNumberMethods,
                             self.number_struct_name, dic))

    def _render_doc_string(self):
        return self.format_code(
            "static const char* %s_doc_string = \"%s\";\n" % (self.class_struct_name, to_c_string(self.doc))
        )

    def _render_ctor_impl(self):
        code = """
        /** Creates new instance of %(name)s class.
            @note Original function signature requires to return PyObject*,
            but here we return the actual %(name)s struct for convenience. */
        %(struct_name)s* %(new_func)s()
        {
            auto o = PyObject_New(%(struct_name)s, &%(type_struct)s);
            o->cppy_new();
            return o;
        }

        /** Deletes a %(name)s instance */
        void %(dealloc_func)s(PyObject* self)
        {
            reinterpret_cast<%(struct_name)s*>(self)->cppy_free();
            self->ob_type->tp_free(self);
        }

        /** Makes a copy of the %(name)s instance @p self,
            using user-supplied %(struct_name)s::cppy_copy() */
        %(struct_name)s* %(copy_func)s(%(struct_name)s* self)
        {
            %(struct_name)s* copy = $NEW(%(name)s);
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

    def _render_init_func(self):
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
        """ % {
            "name": self.name,
            "struct_name": self.type_struct_name
        }
        return self.format_code(code)

