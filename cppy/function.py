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
        if not self.cpp:
            #self.cpp = "#error %s not implemented" % self.name
            self.cpp = "Py_RETURN_NOTIMPLEMENTED;"

        self.func = func
        self.args = inspect.getargspec(self.func)
        self.for_class = for_class
        if self.for_class:
            self.func_name = "cppy_classmethod_%s_%s" % (self.for_class.name, self.name)
        else:
            self.func_name = "cppy_%s" % self.name
        # self.doc += "\n" + str(self.args)

    def get_return_type(self):
        return SPECIAL_RETURN_TYPES.get(self.name, "PyObject*")

    def render_cpp_declaration(self, struct_name=None):
        """Returns the whole cpp function declaration"""
        s = """
        /* %(src_pos)s */
        /* %(debug)s */
        static const char* %(func_name)s_doc = "%(doc)s";
        static %(return)s %(func_name)s(%(PyObject)s* self%(args)s)
        {
            %(code)s
            }
        """
        return s % {"indent": self.indent(),
                    "func_name": self.func_name,
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


    def render_cpp_member_struct_entry(self):
        args = self.get_args_data()
        return """/* %(debug)s */{ "%(name)s", reinterpret_cast<PyCFunction>(%(funcname)s), %(args)s, %(funcname)s_doc },
""" % {
            "name": self.name,
            "funcname": self.func_name,
            "args": args[1],
            "func_type": args[0],
            "debug": str(self.args)
       }
