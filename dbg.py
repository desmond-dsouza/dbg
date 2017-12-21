import inspect
import logging
import sys
from functools import wraps
import pprint

logging.basicConfig(format='%(message)s', level=0)

DBG = True


class TraceCalls(object):
    """ Use as a decorator on functions that should be traced. Several
        functions can be decorated - they will all be indented according
        to their call depth.
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
            msg = '>>%s(%s)' % (fn.__name__, argstr)
            debug(msg, frame_index=2, traced=True)

            TraceCalls.cur_indent += self.indent_step
            ret = fn(*args, **kwargs)
            TraceCalls.cur_indent -= self.indent_step

            if self.show_ret:
                debug('<< %s' % str(ret), frame_index=2, traced=True)
            return ret
        return wrapper if DBG else fn


def debug(obj, frame_index=1, traced=False, pp=False):
    if not DBG:
        return
    f = inspect.currentframe()
    # fs = inspect.getouterframes(f)
    frame,filename,line_number,function_name,lines,index=inspect.getouterframes(
        inspect.currentframe())[frame_index]
    line = lines[0]
    call_level = TraceCalls.cur_indent
    tab_level = 0 if traced else line.find(line.lstrip()) // 4
    msg = pprint.pformat(obj, indent=call_level*3 + tab_level*2) if pp else str(obj)
    # indentation_level = (call_level + indent_level) * 2 #((TraceCalls.cur_indent-1) * 2) + (line.find(line.lstrip()) // 2)
    logging.debug('{:<3d}{c}{i} {m}'.format(
        line_number,
        c=' | ' * call_level,
        i='  ' * tab_level,
        m=msg
    ))
    sys.stdout.flush()
    sys.stderr.flush()
    return msg


def check(msg, lam):
    if not DBG:
        return
    if not lam():
        debug("FAILED *** " + msg, frame_index=2)
        raise AssertionError()

