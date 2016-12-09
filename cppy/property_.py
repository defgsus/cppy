import inspect
from .codeobject import *
from .c_types import *
from .renderer import *

class Property(CodeObject):
    """A python c-api wrapper of a class property"""
    def __init__(self, prop, for_class):
        name = ""
        try:
            name = prop.fget.__name__
            self.has_getter = True
        except:
            self.has_getter = False
        try:
            name = prop.fget.__name__
            self.has_setter = True
        except:
            self.has_setter = False

        super().__init__(
            name=name,
            doc=inspect.getdoc(prop),
            #src_pos="%s:%d" % (func.__code__.co_filename, func.__code__.co_firstlineno),
        )
        self.prop = prop
        self.for_class = for_class
        self.getter_func_name = "%s_%s_getter" % (self.for_class.name, self.name)
        self.setter_func_name = "%s_%s_setter" % (self.for_class.name, self.name)
        self.doc_name = "%s_%s_doc" % (self.for_class.name, self.name)

        self.has_getter &= self.has_cpp
        self.has_setter &= self.has_cpp2

    def __str__(self):
        return "Property(%s.%s)" % (self.for_class.name, self.name)


    def render_cpp_getset_struct_entry(self):
        return '{ (char*)"%s", (getter)%s, (setter)%s, (char*)%s, (void*)NULL },\n' % (
            self.name,
            self.getter_func_name if self.has_getter else "NULL",
            self.setter_func_name if self.has_setter else "NULL",
            self.doc_name if self.doc else "NULL",
        )

    def render_cpp_declaration(self):
        code = ""
        if self.doc:
            code += 'static const char* %s = "%s";\n' % (self.doc_name, to_c_string(self.doc))

        if self.has_getter:
            code += render_function(self.getter_func_name, "getter", self.cpp, self.for_class)
        if self.has_setter:
            code += render_function(self.setter_func_name, "setter", self.cpp2, self.for_class)

        return self.format_code(code)