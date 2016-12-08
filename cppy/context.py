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
        else:
            raise NotImplementedError("Unhandled class %s" % o)

    def dump(self):
        print("# -- global functions --")
        for i in self.functions:
            print(i)
        print("# -- global classes --")
        for clas in self.classes:
            print(clas)
            if clas.functions:
                print("    -- functions --")
                for i in clas.functions:
                    print("   ", i)
            if clas.properties:
                print("    -- properties --")
                for i in clas.properties:
                    print("   ", i)


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
        code = strip_newlines(code1)
        return change_text_indent(code, self.indent_length())

    def get_template_arg(self, tag, the_args):
        """Returns the value for a template tag '$tag(name)'"""
        args = the_args.split(",")
        args = [x.strip() for x in args]
        if not args:
            raise ValueError("No arguments to template tag '%s'" % tag)
        class_name = args[-1]
        bad_arg = False

        if tag == "STRUCT":
            for i in self.classes:
                if i.name == class_name:
                    return i.class_struct_name
            bad_arg = True

        if tag == "TYPE_STRUCT":
            for i in self.classes:
                if i.name == class_name:
                    return i.type_struct_name
            bad_arg = True

        if tag == "NEW":
            for i in self.classes:
                if i.name == class_name:
                    return "%s(&%s,NULL,NULL)" % (i.class_new_func_name, i.type_struct_name)
            bad_arg = True

        if tag == "IS_INSTANCE":
            class_name = args[1]
            for i in self.classes:
                if i.name == class_name:
                    return "%s(%s)" % (i.class_is_instance_func_name, args[0])
            raise ValueError("$IS_INSTANCE for %s not known" % class_name)

        if tag == "COPY":
            class_name = args[1]
            for i in self.classes:
                if i.name == class_name:
                    return "%s(%s)" % (i.class_copy_func_name, args[0])
            bad_arg = True

        if bad_arg:
            raise ValueError("Bad arguments '%s' to template tag '%s'" % (class_name, tag))
        raise ValueError("Unknown template tag '%s'" % tag)



