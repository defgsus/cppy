
INDENT = "    "

def to_c_string(text):
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "")
    text = text.replace('"', '\\"')
    return text

def indent_code(code, indent):
    import re
    return indent + re.sub(r"\n[ |\t]*", "\n"+indent, code.strip())



def render_struct(structtypename, struct_table, name, dictionary, indent="", first_line=""):
    name_width = 1
    type_width = 1
    for i in struct_table:
        name_width = max(name_width, len(i[0]))
        type_width = max(type_width, len(i[1]))

    code = "%(indent)sstatic %(type)s %(name)s =\n%(indent)s{\n" % {
        "indent": indent, "type": structtypename, "name": name
    }
    if first_line:
        code += indent + INDENT + first_line + "\n"
    for i in struct_table:
        code += "%(indent)s%(name)s %(type)s(%(value)s)" % {
            "indent": indent+INDENT,
            "name" : ("/* %s */" % i[0]).ljust(name_width + 6),
            "type" : ("(%s)" % i[1]).ljust(type_width + 13),
            "value" : str(dictionary.get(i[0], "NULL"))
        }
        if not i == struct_table[-1]:
            code += ","
        code += "\n"
    code += indent + "}; /* %s */\n" % name
    return code