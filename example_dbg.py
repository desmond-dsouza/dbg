# An example of using dbg: recursive calls, trace, debug, check

from dbg import debug, check, TraceCalls

# set_debugging(...) to choose All, None, or Selective debugging
from dbg import set_debugging, Dbg_all, Dbg_none, Dbg_enabled_only
set_debugging(Dbg_all)


@TraceCalls()
def foo():
    debug('foo: Hi World', label="LABEL")
    debug([1, 2, 3])
    for i in range(3):
        debug("Now we're cookin")
        check("invariant: %d < 2" % i, lambda: i < 2)
        for j in range(debug(1, label="ONE")):
            debug("nested loop", enabled=True)
    return "42"


pp_stuff = ['spam', 'eggs', 'lumberjack', 'knights', 'ni']
pp_stuff.insert(0, pp_stuff[:])


@TraceCalls(enabled=True)
def bar(i, j=None):
    debug("bar " + str(i))
    debug(pp_stuff)
    if i > 1:
        bar(i - 1)
        return "99", i
    else:
        debug(pp_stuff, pretty=True)
        return foo(), i


if __name__ == '__main__':
    bar(3)

