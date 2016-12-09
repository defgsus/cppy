import inspect
from .codeobject import *
from .renderer import *
from .function_ import *
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

    def finalize(self):
        """To be called after all CodeObjects are added"""
        # first resolve all base classes so we can fetch cpp annotation from bases
        self._resolve_base_classes()
        # remove all objects from export who aren't annotated
        self.functions = self._clear_unused(self.functions)
        self.classes = self._clear_unused(self.classes)
        for i in self.classes:
            i.functions = self._clear_unused(i.functions)
            i.properties = self._clear_unused(i.properties)

        self.all_objects = self.functions + self.classes

    def _clear_unused(self, objs):
        ret = []
        for i in objs:
            if i.has_cpp:
                ret.append(i)
        return ret

    def get_class(self, name):
        for i in self.classes:
            if i.name == name:
                return i
        raise RuntimeError("Required base class '%s' not found" % name)

    def _resolve_base_classes(self):
        for i in self.classes:
            i.bases = []
            #print(i.name, i.the_class.__bases__)
            for j in i.the_class.__bases__:
                name = j.__name__
                if not "builtins.object" in name and not name == "object":
                    i.bases.append(self.get_class(name))

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

    def format_cpp(self, code, for_object):
        """Applies template replacement"""
        code1 = ""
        prev = 0
        import re
        for i in re.finditer(r"\$([A-Za-z_]+)\(([ ]*[A-Za-z_0-9, ]*)\)", code):
            span = i.span()
            code1 += code[prev:span[0]]
            prev = span[1]
            code1 += self.get_template_arg(i.groups()[0], i.groups()[1], for_object)
        code1 += code[prev:]
        code = strip_newlines(code1)
        return change_text_indent(code, self.indent_length())

    def get_template_arg(self, tag, the_args, for_class):
        """Returns the value for a template tag '$tag(the_args)'"""
        if the_args:
            args = the_args.split(",")
            args = [x.strip() for x in args]
        else:
            args = []

        class_name = ""
        if for_class:
            class_name = for_class.name

        bad_arg = False

        tag = tag.upper();
        if tag == "NAME":
            if len(args):
                class_name = args[-1]
            for i in self.classes:
                if i.name == class_name:
                    return i.name
            bad_arg = True

        if tag == "STRUCT":
            if len(args):
                class_name = args[-1]
            for i in self.classes:
                if i.name == class_name:
                    return i.class_struct_name
            bad_arg = True

        if tag == "TYPE_STRUCT":
            if len(args):
                class_name = args[-1]
            for i in self.classes:
                if i.name == class_name:
                    return i.type_struct_name
            bad_arg = True

        if tag == "NEW":
            if len(args):
                class_name = args[-1]
            for i in self.classes:
                if i.name == class_name:
                    return "%s(&%s,NULL,NULL)" % (i.class_new_func_name, i.type_struct_name)
            bad_arg = True

        if tag == "IS_INSTANCE":
            if len(args) > 1:
                class_name = args[-1]
            for i in self.classes:
                if i.name == class_name:
                    return "%s(%s)" % (i.class_is_instance_func_name, args[0])
            bad_arg = True

        if tag == "CAST":
            if len(args) > 1:
                class_name = args[-1]
            for i in self.classes:
                if i.name == class_name:
                    return "reinterpret_cast<%s*>(%s)" % (i.class_struct_name, args[0])
            bad_arg = True

        if tag == "COPY":
            if len(args) > 1:
                class_name = args[-1]
            for i in self.classes:
                if i.name == class_name:
                    return "%s(%s)" % (i.class_copy_func_name, args[0])
            bad_arg = True

        if bad_arg:
            raise ValueError("Bad arguments '%s' to template tag '%s' (object:%s)" % (the_args, tag, class_name))
        raise ValueError("Unknown template tag '%s'" % tag)



