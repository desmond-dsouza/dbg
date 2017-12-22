from dbg import debug, check, TraceCalls
import dbg

dbg.DEBUG = True


@TraceCalls()
def foo():
    debug('foo: Hi World', label="LABEL")
    debug("foo: well")
    for i in range(3):
        debug("foo: Now we're cookin")
        check(f"invariant: {i} < 2", lambda: i < 2)
        for i in range(debug(1, label="ONE")):
            debug("foo: 2 tabs in")
    return "42"


pp_stuff = ['spam', 'eggs', 'lumberjack', 'knights', 'ni']
pp_stuff.insert(0, pp_stuff[:])


@TraceCalls()
def bar(i):
    debug("bar " + str(i))
    debug(pp_stuff, pretty=False)
    if i > 1:
        bar(i - 1)
        return "99", i
    else:
        return foo(), i


if __name__ == '__main__':
    bar(3)

