"""
Commandline tool to interface with cppy
"""
import argparse, sys, os

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="cppy interface - python to c++ the hard way"
    )
    parser.add_argument(
        "-i",
        type=str, #argparse.FileType("r"),
        help="The name of the python module file to convert to c++. "
             "Should be a fully qualified filename")
    parser.add_argument(
        "-n",
        type=str,
        help="The name of the output file, defaults to the name of the module file. "
             "Example -n mymod, to generate mymod.h/mymod.cpp")
    #parser.add_argument(
    #    '-o', default=sys.stdout, type=argparse.FileType('w'),
    #    help='The output file, defaults to stdout')
    #parser.add_argument(
    #    'command', type=str,
    #    default="dump",
    #    help='What to do')

    args = parser.parse_args()

    if not args.i:
        parser.print_help()
        exit(-1)

    module_file = args.i
    module_name = os.path.basename(module_file).split(".")[0]
    if args.n:
        out_name = str(args.n)
    else:
        out_name = module_name
    out_name = os.path.join(os.path.dirname(module_file), out_name)

    print("Importing module '%s'" % module_name)

    # Python 3.4 way
    from importlib.machinery import SourceFileLoader
    module = SourceFileLoader(module_name, module_file).load_module()

    from cppy import compiler
    ctx = compiler.compile(module)

    print("Writing output to %s.cpp" % out_name)
    ctx.write_to_file(out_name + ".h", ctx.render_hpp())
    ctx.write_to_file(out_name + ".cpp", ctx.render_cpp())

    #ctx.context.dump()



    #eval("import %s" % args.i)


