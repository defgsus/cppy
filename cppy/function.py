import inspect
from .codeobject import *
from .c_types import *
from .renderer import to_c_string

class Function(CodeObject):
    """A python c-api implementation of a global or member function"""
    def __init__(self, func, for_class):
        super().__init__(
            name=func.__name__,
            doc=inspect.getdoc(func),
            src_pos="%s:%d" % (func.__code__.co_filename, func.__code__.co_firstlineno),
        )
        self.func = func
        self.args = inspect.getargspec(self.func)
        self.for_class = for_class
        if self.for_class:
            self.func_name = "cppy_classmethod_%s_%s" % (self.for_class.name, self.name)
        else:
            self.func_name = "cppy_%s" % self.name
        # self.doc += "\n" + str(self.args)

        self.has_cpp = True
        if not self.cpp:
            self.has_cpp = False
            self.cpp = "#error %s not implemented" % self.name
            #self.cpp = "Py_RETURN_NOTIMPLEMENTED;"

    def is_normal_function(self):
        """Returns True if this function should go into the general PyMethodDef"""
        if not self.for_class:
            return True
        return not (self.is_type_function() or self.is_number_function() or self.is_sequence_function())

    def is_type_function(self):
        """
        Returns True if this function should be part of the PyTypeObject struct
        """
        if not self.for_class:
            return False
        for i in TYPE_FUNCS:
            if i[0] == self.name:
                return True
        return False

    def is_number_function(self):
        """
        Returns True if this function should be part of the PyNumberMethods struct
        """
        if not self.for_class:
            return False
        for i in NUMBER_FUNCS:
            if i[0] == self.name:
                return True
        return False

    def is_sequence_function(self):
        """
        Returns True if this function should be part of the PySequenceMethods struct
        """
        if not self.for_class:
            return False
        for i in SEQUENCE_FUNCS:
            if i[0] == self.name:
                return True
        return False

    def get_return_type(self):
        if not self.name in FUNCNAME_TO_TYPE:
            return "PyObject*"
        type = FUNCNAME_TO_TYPE[self.name]
        if not type in FUNCTIONS:
            raise ValueError("Function type for %s not in c_types.FUNCTIONS" % type)
        return FUNCTIONS[type][0]
        #return SPECIAL_RETURN_TYPES.get(self.name, "PyObject*")

    def get_argument_types(self):
        if not self.name in FUNCNAME_TO_TYPE:
            return ("PyObject*", )
        type = FUNCNAME_TO_TYPE[self.name]
        if not type in FUNCTIONS:
            raise ValueError("Function type for %s not in c_types.FUNCTIONS" % type)
        return FUNCTIONS[type][1]

    def get_cpp_argument_string(self):
        if not self.is_normal_function():
            args = self.get_argument_types()
            str = ""
            for i, a in enumerate(args):
                str += "%s arg%d" % (a, i)
                if i+1 < len(args):
                    str += ", "
            return str
        return "PyObject* arg0" + self.get_args_data()[2]

    def get_args_data(self):
        if self.args.varargs and len(self.args.varargs):
            return ("PyFunctionWithKeywords", "METH_VARARGS", ", PyObject* arg1, PyObject* kwargs",)

        if self.for_class:
            if self.name == "__init__":
                return ("PyFunctionWithKeywords", "METH_VARARGS", ", PyObject* arg1, PyObject* kwargs",)
            num_args = len(self.args.args)
            if not num_args:
                raise TypeError("class method %s has no parameters" % self.name)
            if num_args == 1:
                return ("PyCFunction", "METH_NOARGS", "",)
            else:
                return ("PyCFunction", "METH_VARARGS", ", PyObject* arg1",)

        if len(self.args.args) == 1:
            return ("PyCFunction", "METH_O", ", PyObject* arg", )
        if len(self.args.args) > 1:
            return ("PyCFunction", "METH_VARARGS", ", PyObject* args",)

        return ("PyNoArgsFunction", "METH_NOARGS", "")


    def render_cpp_declaration(self, struct_name=None):
        """Returns the whole cpp function declaration"""
        s = """
/* %(src_pos)s */
/* %(debug)s */
%(doc)sstatic %(return)s %(func_name)s(%(args)s)
{
%(get_self)s
%(code)s
}
"""
        doc = ""
        if self.doc:
            doc = 'static const char* %s_doc = "%s";\n' % (self.func_name, to_c_string(self.doc))
        get_self = ""
        if struct_name:
            get_self = "    %(struct)s* self = reinterpret_cast<%(struct)s*>(arg0);\n" % {
                "struct": struct_name
            }
        s %= {      "indent": self.indent(),
                    "func_name": self.func_name,
                    "return": self.get_return_type(),
                    "doc": doc,
                    "src_pos": self.src_pos,
                    "get_self": get_self,
                    "code": self.get_cpp(),
                    "PyObject": "PyObject" if struct_name is None else struct_name,
                    "args": self.get_cpp_argument_string(),
                    "debug": str(self.args)
                    }
        return self.format_code(s)


    def render_cpp_member_struct_entry(self):
        args = self.get_args_data()
        s = """/* %(debug)s */\n{ "%(name)s", reinterpret_cast<PyCFunction>(%(funcname)s), %(args)s, %(doc_name)s },
""" % {
            "name": self.name,
            "doc_name": ("%s_doc" % self.func_name) if self.doc else "NULL",
            "funcname": self.func_name,
            "args": args[1],
            "func_type": args[0],
            "debug": str(self.args)
       }
        return self.format_code(s)
