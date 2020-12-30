import sys
import getopt


def main(argv=sys.argv[1:]):
    if len(argv) == 0:
        # we need to print help
        pass
    else:
        args, kwargs = _parse_args(argv)


def _parse_args(args):
    argdict = {}
    arglist = []

    arg_iter = enumerate(args)

    for i, arg in arg_iter:
        if arg.startswith('--'):
            argdict.update({arg[2:]: args[i+1]})
            next(arg_iter)
        elif arg.startswith('-'):
            argdict.update({arg[1:]: args[i+1]})
            next(arg_iter)
        else:
            arglist.append(arg)

    return arglist, argdict


if __name__ == '__main__':
    main()
