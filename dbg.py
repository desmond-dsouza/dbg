# Exports:
# debugging(level): turn on or off all dbg stuff, or selectively enable
# @TraceCalls() - decorator to trace entry & exit
# debug(obj) - indented display of obj (returns obj, so can be used as "tap")
# check(aLambda_or_bool) - if aLambda does not evaluate to True, print error

# Freely borrowed & adapted from others' code, sorry I did not keep track

import inspect
import logging
import sys
from functools import wraps
import pprint


Dbg_all = "All"
Dbg_none = "Off"
Dbg_enabled_only = "Enabled_Only"


DEBUGGING = Dbg_all


def set_debugging(level):
    global DEBUGGING
    DEBUGGING = level


def is_visible(enabled):
    return DEBUGGING is Dbg_all or (DEBUGGING is Dbg_enabled_only and enabled)


class TraceCalls(object):
    """ Use as a decorator on any function(s) to trace call & return values.
    """

    cur_indent = 0

    def __init__(self, enabled=False):
        self.indent_step = 1
        self.show_ret = True
        self.enabled = enabled

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            argstr = ', '.join(
                [repr(a) for a in args] +
                ["%s=%s" % (a, repr(b)) for a, b in kwargs.items()])
            msg = ">> %s(%s)" % (fn.__name__, argstr)
            _debug(msg, frame_index=2, traced=True, enabled=self.enabled)

            TraceCalls.cur_indent += self.indent_step
            ret = fn(*args, **kwargs)
            TraceCalls.cur_indent -= self.indent_step

            if self.show_ret:
                _debug('<< %s' % str(ret), frame_index=2, traced=True, enabled=self.enabled)
            return ret
        return wrapper if is_visible(self.enabled) else fn


def _pp_indent(obj, indent=0, prefix=""):
    fstring = ' ' * indent + prefix + ' {}'
    lines = pprint.pformat(obj).splitlines(True)
    return ''.join([lines[0]] + [fstring.format(l) for l in lines[1:]])


def debug(obj, label="", pretty=False, enabled=False):
    """Display with indentation for debugging, returns obj.
    Optional label and multi-line pretty-printing, and enabled for selective debugging."""
    return _debug(obj, label=label, pretty=pretty, enabled=enabled, frame_index=2)


logging.basicConfig(format='%(message)s', level=0)


def _debug(obj, label="", frame_index=1, traced=False, checked=None, pretty=False, enabled=False):
    """Internal use with additional args"""
    if not is_visible(enabled):
        return obj
    YELLOW, GREEN, RED, RESET = u"\u001b[33m", u"\u001b[1;32m", u"\u001b[1;31m", u"\u001b[0m"
    COLOR = YELLOW if checked is None else GREEN if checked is True else RED
    frame, filename, line_number, function_name, lines, index = inspect.getouterframes(
        inspect.currentframe())[frame_index]
    line = lines[0]
    call_level = TraceCalls.cur_indent
    tab_level = 0 if traced else line.find(line.lstrip()) // 4
    call_padding = ' | ' * call_level
    tab_padding = '  ' * tab_level
    msg = _pp_indent(obj, indent=3, prefix=call_padding + tab_padding) if pretty else str(obj)
    lbl = ("%s: " % label) if label else ""
    logging.debug(u"%s%3d%s%s %s%s%s%s" % (YELLOW, line_number, call_padding, tab_padding, COLOR, lbl, msg, RESET))
    # logging.debug(f"{YELLOW}{line_number:<3d}{call_padding}{tab_padding} {COLOR}{lbl}{msg}{RESET}")
    sys.stdout.flush()
    sys.stderr.flush()
    return obj


def check(msg, a_lambda, enabled=True):
    """If a_lambda() is False display FAILED message"""
    if not is_visible(enabled):
        return
    if (callable(a_lambda) and not a_lambda()) or (a_lambda is False):
        _debug("FAILED %s <<<<<<<<<<<<<<<<<<<<<<<<<<" % msg, frame_index=2, checked=False, enabled=enabled)
    else:
        _debug("PASSED %s : OK" % msg, frame_index=2, checked=True, enabled=enabled)

