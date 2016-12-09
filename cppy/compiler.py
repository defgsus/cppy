from .context import *
from .renderer import *
from .class_ import Class
from .function_ import Function
from .property_ import Property

class _Exporter:
    """
    Class responsible to traverse a module and it's members
    and to generate an ExportContext instance from it
    """
    def __init__(self):
        self.scope_stack = []
        self.context = None

    def log(self, str):
        if 0:
            print("  " * len(self.scope_stack) + str)

    def scope_name(self):
        return self.scope_stack[-1] if self.scope_stack else ""

    def full_scope_name(self, name):
        r = ""
        for i in self.scope_stack:
            r += i + "."
        return r + name

    def push_scope(self, name):
        self.scope_stack.append(name)
    def pop_scope(self):
        self.scope_stack.pop()

    def inspect_module(self, module):
        self.context = ExportContext(module)
        mod_name = module.__name__
        self.log("inspect module '%s'" % mod_name)
        self.push_scope(mod_name)
        self.inspect_names(module, dir(module))
        self.pop_scope()
        self.context.finalize()

    def inspect_names(self, parent, names):
        self.log("scanning names in %s" % type(parent))
        self.push_scope(str(type(parent)))
        for name in names:
            try:
                #print(self.full_scope_name(name))
                o = eval("parent.%s" % name)
            except BaseException as e:
                self.log("EXCEPTION %s" % e)
                continue
            self.inspect_entity(o)

        self.pop_scope()

    def inspect_entity(self, o):
        if inspect.isfunction(o):
            self.inspect_function(o)
        elif inspect.isclass(o):
            self.inspect_class(o)
        elif inspect.isgetsetdescriptor(o):
            print("GETSET %s" % o)

    def inspect_function(self, func, class_obj=None):
        self.log("inspecting function %s" % func)
        self.push_scope(func.__name__)
        o = Function(func, class_obj)
        o.context = self.context
        if class_obj is None:
            self.context.append(o)
        else:
            class_obj.append(o)
        self.pop_scope()

    def inspect_property(self, prop, class_obj):
        p = Property(prop, class_obj)
        p.context = self.context
        class_obj.properties.append(p)

    def inspect_class(self, cls):
        self.log("inspecting class %s" % cls)
        self.push_scope(cls.__name__)
        class_obj = Class(cls)
        for n, mem in inspect.getmembers(cls):
            if inspect.isfunction(mem):
                self.inspect_function(mem, class_obj)
            elif isinstance(mem, property):
                self.inspect_property(mem, class_obj)

        self.context.append(class_obj)
        self.pop_scope()




def compile(module):
    """
    Scans the module and returns an cppy.Module class
    :param module: a loaded module
    :return: a Module instance
    """
    if not inspect.ismodule(module):
        raise TypeError("Expected module, got %s" % type(module))

    c = _Exporter()
    c.inspect_module(module)
    return Renderer(c.context)


if __name__ == "__main__":
    pass
    #print("TYPE_STRUCT_MEMBER = [")
    #for i in TYPE_STRUCT_MEMBER:
    #    print('    ("%s", "%s"),' % (i[1], i[0]))
    #print("]")
