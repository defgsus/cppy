import inspect
from .codeobject import *
from .renderer import *
from .function import *
from .class_ import *

class ExportContext:
    """
    Class holding all code objects and the template-context
    """
    def __init__(self, module):
        self.module = module
        self.functions = []
        self.classes = []
        self.name = module.__name__
        self.struct_name = "cppy_module_%s" % self.name
        self.method_struct_name = "cppy_module_methods_%s" % self.name
        self.doc = inspect.getdoc(module)
        self.doc = self.doc if self.doc else ""
        self.indent_level = 0

        self.cpp = ""
        self.cpp2 = ""

        cpp = self.doc.split("_CPP_:")
        if len(cpp) > 1:
            self.doc = cpp[0]
            self.cpp = cpp[1]
            if len(cpp) > 2:
                self.cpp2 = cpp[2]

    def append(self, o):
        """Append a CodeObject"""
        o.context = self
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

    def push_indent(self):
        self.indent_level += 1

    def pop_indent(self):
        if self.indent_level <= 0:
            raise RuntimeWarning("pop_indent() called without push")
        self.indent_level -= 1

    def clear_indent(self):
        self.indent_level = 0

    def indent(self):
        return "    " * self.indent_level

    def indent_length(self):
        return self.indent_level * 4

    def format_cpp(self, code):
        """Applies template replacement"""
        code1 = ""
        prev = 0
        import re
        for i in re.finditer(r"\$([A-Z_]+)\(([ ]*[A-Za-z_0-9, ]*)\)", code):
            span = i.span()
            code1 += code[prev:span[0]]
            prev = span[1]
            code1 += self.get_template_arg(i.groups()[0], i.groups()[1])
        code1 += code[prev:]
        code = code1.strip()
        return change_text_indent(code, self.indent_length())

    def get_template_arg(self, tag, name):
        """Returns the value for a template tag '$tag(name)'"""
        args = name.split(",")
        args = [x.strip() for x in args]

        if tag == "STRUCT":
            for i in self.classes:
                if i.name == name:
                    return i.class_struct_name
            raise ValueError("$STRUCT for %s not known" % name)

        if tag == "TYPE_STRUCT":
            for i in self.classes:
                if i.name == name:
                    return i.type_struct_name
            raise ValueError("$TYPE_STRUCT for %s not known" % name)

        if tag == "NEW":
            for i in self.classes:
                if i.name == name:
                    return "%s(&%s,NULL,NULL)" % (i.class_new_func_name, i.type_struct_name)
            raise ValueError("$NEW for %s not known" % name)

        if tag == "COPY":
            for i in self.classes:
                if i.name == name:
                    return "%s(&%s,NULL,NULL)" % (i.class_new_func_name, i.type_struct_name)
            raise ValueError("$NEW for %s not known" % name)

        if tag == "IS_INSTANCE":
            name = args[1]
            for i in self.classes:
                if i.name == name:
                    return "PyObject_TypeCheck(%s, &%s)" % (args[0], i.type_struct_name)
            raise ValueError("$IS_INSTANCE for %s not known" % name)

        raise ValueError("Unknown $ template tag '%s'" % tag)



