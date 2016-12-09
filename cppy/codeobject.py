
class CodeObject:
    """Base class of 'python things' that have a cpp representation"""
    def __init__(self, name, doc="", src_pos=""):
        self.context = None
        self.name = name
        self.doc = doc if doc else ""
        self.src_pos = src_pos
        self.cpp = ""
        self.cpp2 = ""
        self.module = None

        cpp = self.doc.split("_CPP_:")
        if len(cpp) > 1:
            self.doc = cpp[0]
            self.cpp = cpp[1]
            if len(cpp) > 2:
                self.cpp2 = cpp[2]

    def __str__(self):
        return "%s" % self.name

    def push_indent(self): self.context.push_indent()
    def pop_indent(self): self.context.pop_indent()
    def indent(self): return self.context.indent()
    def indent_length(self): return self.context.indent_length()
    def format_code(self, code): return self.context.format_cpp(code, self)

    def get_cpp(self, alternative=None):
        if not alternative:
            alternative = self.cpp
        return self.format_code(alternative) if alternative else ""

    def render_cpp_declaration(self):
        raise NotImplementedError

