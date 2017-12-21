from dbg import debug, check, TraceCalls

@TraceCalls()
def foo():
    debug('foo: Hi World')
    debug("foo: well")
    for i in range(3):
        debug("foo: Now we're cookin")
        check(f"invariant: {i} < 2", lambda: i < 2)
        for i in range(1):
            debug("foo: 2 tabs in")
    return "42"


@TraceCalls()
def bar(i):
    debug("bar " + str(i))
    debug([i for i in range(3)], pp=True)
    if i > 1:
        bar(i - 1)
        return "99", i
    else:
        return foo(), i


# if __name__ == '__main__':
bar(3)
