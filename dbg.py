# Exports:
# DBG = True or False : single point to turn on or off all dbg stuff
# @TraceCalls() - decorator to trace entry & exit
# debug(obj) - indented display of obj (returns obj, so can be used as "tap")
# check(aLambda) - if aLambda does not evaluate to True, print error

# freely borrows / adapts from others, sorry did not keep track

import inspect
import logging
import sys
from functools import wraps
import pprint

logging.basicConfig(format='%(message)s', level=0)

DEBUG = True


class TraceCalls(object):
    """ Use as a decorator on any function(s) to trace call & return values.
    """

    cur_indent = 0

    def __init__(self, stream=sys.stdout, indent_step=1, show_ret=True):
        self.stream = stream
        self.indent_step = indent_step
        self.show_ret = show_ret

        # This is a class attribute since we want to share the indentation
        # level between different traced functions, in case they call
        # each other.
        # TraceCalls.cur_indent = 0

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            argstr = ', '.join(
                [repr(a) for a in args] +
                ["%s=%s" % (a, repr(b)) for a, b in kwargs.items()])
            # self.stream.write('%s%s(%s)\n' % (indent, fn.__name__, argstr))
            msg = f">> {fn.__name__}({argstr})"
            debug(msg, frame_index=2, traced=True)

            TraceCalls.cur_indent += self.indent_step
            ret = fn(*args, **kwargs)
            TraceCalls.cur_indent -= self.indent_step

            if self.show_ret:
                debug('<< %s' % str(ret), frame_index=2, traced=True)
            return ret
        return wrapper if DEBUG else fn


def _pp_indent(obj, indent=0, prefix=""):
    fstring = ' ' * indent + prefix + ' {}'
    lines = pprint.pformat(obj).splitlines(True)
    return ''.join([lines[0]] + [fstring.format(l) for l in lines[1:]])


def debug(obj, label="", frame_index=1, traced=False, pretty=False):
    """Display with indentation for debugging, returns obj. Optional label
    and pretty-printing args"""
    if not DEBUG:
        return obj
    frame, filename, line_number, function_name, lines, index = inspect.getouterframes(
        inspect.currentframe())[frame_index]
    line = lines[0]
    call_level = TraceCalls.cur_indent
    tab_level = 0 if traced else line.find(line.lstrip()) // 4
    call_padding = ' | ' * call_level
    tab_padding = '  ' * tab_level
    msg = _pp_indent(obj, indent=3, prefix=call_padding + tab_padding) if pretty else str(obj)
    lbl = f"{label}: " if label else ""
    logging.debug('{:<3d}{c}{i} {lbl}{m}'.format(
        line_number,
        c=call_padding,
        i=tab_padding,
        lbl=lbl,
        m=msg
    ))
    sys.stdout.flush()
    sys.stderr.flush()
    return obj


def check(msg, a_lambda):
    """If a_lambda() is False display FAILED message"""
    if not DEBUG:
        return
    if not a_lambda():
        debug(f"FAILED {msg} <<<<<<<<<<<<<<<<<<<<<<<<<<", frame_index=2)
        # sys.exit()
    else:
        debug(f"PASSED {msg}", frame_index=2)

