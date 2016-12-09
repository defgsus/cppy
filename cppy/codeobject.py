
class CodeObject:
    """Base class of 'python things' that have a cpp representation"""
    def __init__(self, name, doc="", src_pos=""):
        self.context = None
        self.name = name
        self.doc = doc if doc else ""
        self.src_pos = src_pos
        self._cpp = ""
        self._cpp2 = ""
        self.module = None

        self._has_cpp = False
        self._has_cpp2 = False
        cpp = self.doc.split("_CPP_:")
        if len(cpp) > 1:
            self.doc = cpp[0]
            self._cpp = cpp[1]
            self._has_cpp = True
            if len(cpp) > 2:
                self._cpp2 = cpp[2]
                self._has_cpp2 = True

    def __str__(self):
        return "%s" % self.name

    def push_indent(self): self.context.push_indent()
    def pop_indent(self): self.context.pop_indent()
    def indent(self): return self.context.indent()
    def indent_length(self): return self.context.indent_length()
    def format_code(self, code): return self.context.format_cpp(code, self)

    def render_forward_decl(self):
        """Stuff that needs to be known by all other code"""
        return ""

    def render_impl_decl(self):
        """Implementation that need final definition of all type structs, etc.."""
        return ""

    @property
    def has_cpp(self):
        return self._has_cpp
    @property
    def has_cpp2(self):
        return self._has_cpp2
    @property
    def cpp(self):
        return self.format_code(self._cpp)
    @property
    def cpp2(self):
        return self.format_code(self._cpp2)

    def render_cpp_declaration(self):
        raise NotImplementedError

