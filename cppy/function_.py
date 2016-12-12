import inspect
from .codeobject import *
from .c_types import *
from .renderer import *

class Function(CodeObject):
    """A python c-api implementation of a global or member function"""
    def __init__(self, func, for_class):
        self.for_class = for_class
        super().__init__(
            name=func.__name__,
            doc=inspect.getdoc(func),
            src_pos="%s:%d" % (func.__code__.co_filename, func.__code__.co_firstlineno),
        )
        self.func = func
        self.args = inspect.getargspec(self.func)
        if self.for_class:
            self.func_name = "cppy_classmethod_%s_%s" % (self.for_class.name, self.name)
        else:
            self.func_name = "cppy_%s" % self.name
        # self.doc += "\n" + str(self.args)

    def supported_doc_tags(self):
        return [None]

    def __str__(self):
        if self.for_class:
            return "Function(%s.%s)" % (self.for_class.name, self.name)
        else:
            return "Function(%s)" % self.name

    def format_code(self, code):
        return self.context.format_cpp(code, self.for_class)

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
            return ("PyFunctionWithKeywords", "METH_VARARGS")

        if self.for_class:
            # TODO: The __init__ func is not part of the normal PyMethodDef and has a special
            # signature anyway. This is covered somewhere else
            #if self.name == "__init__":
            #    return ("PyFunctionWithKeywords", "METH_VARARGS")
            num_args = len(self.args.args)
            if not num_args:
                raise TypeError("class method %s has no parameters" % self.name)
            if num_args == 1:
                return ("PyCFunction", "METH_NOARGS")
            elif num_args == 2:
                return ("PyCFunction", "METH_O")
            else:
                return ("PyCFunction", "METH_VARARGS")

        if len(self.args.args) == 1:
            return ("PyCFunction", "METH_O")
        if len(self.args.args) > 1:
            return ("PyCFunction", "METH_VARARGS")

        return ("PyNoArgsFunction", "METH_NOARGS", "")


    def render_header_forwards(self):
        """Stuff that needs to be known by all other code in the .h file"""
        return ""

    def render_header_impl(self):
        """Stuff that implements stuff in the .h file"""
        return ""

    def render_forwards(self):
        """Stuff that needs to be known by all other code in .cpp file"""
        return ""

    def render_impl(self):
        """Implementation that need final definition of all type structs, etc.."""
        return ""

    def render_python_api(self):
        """The general python c-api constructs"""
        doc = ""
        if self.doc and self.is_normal_function():
            doc = 'static const char* %s_doc = "%s";\n' % (self.func_name, to_c_string(self.doc))
        code = "/* %(src_pos)s */\n/* %(debug)s */\n%(doc)s" % {
            "src_pos": self.src_pos,
            "debug": str(self.args),
            "doc": doc
        }
        func_type = FUNCNAME_TO_TYPE.get(self.name, "binaryfunc")
        code += render_function(self.func_name, func_type, self.cpp(), self.for_class)

        return self.format_code(code)

    def render_member_struct_entry(self):
        args = self.get_args_data()
        s = '{ "%(name)s", reinterpret_cast<PyCFunction>(%(funcname)s), %(args)s, %(doc_name)s },\n' % {
            "name": self.name,
            "doc_name": ("%s_doc" % self.func_name) if self.doc else "NULL",
            "funcname": self.func_name,
            "args": args[1],
            "func_type": args[0]
        }
        return s
