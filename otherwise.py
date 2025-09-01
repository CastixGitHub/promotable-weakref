# Basically test.py (dropping useless example_1)
# Changed the import and AnnotatedNode defintion
# Also changes at the end of the file,
# Trying to explain a difference that shouldn't be harmful
import weakref
import gc
try:
    import promotable_weakref
except ImportError:
    promotable_weakref = None


class AnnotatedNode:
    def __init__(self, node, **metadata):
        try:
            if promotable_weakref is not None:
                self._node = weakref.proxy(node)
            else:
                self._ref = weakref.ref(node)
                self._node = weakref.proxy(node)
        except TypeError:
            self._ref = None
            self._node = node
        self.metadata = metadata
        self.accessed = False  # could be a counter?

    def __del__(self):
        if promotable_weakref is not None:
            if (
                self.accessed
                and isinstance(self._node, weakref.ProxyType)
            ):
                promotable_weakref.xdecref(self._node)
        else:
            self._ref = None

    @property
    def node(self):
        if promotable_weakref is not None:
            assert not self.accessed, 'think about it'
            self.accessed = True
            if isinstance(self._node, weakref.ProxyType):
                promotable_weakref.xincref(self._node)
            return self._node
        else:
            return self._node.__weakref__()


def example_2():
    class Node:
        def __init__(self, lhs, rhs):
            self.lhs = lhs
            self.rhs = rhs

        def __repr__(self):
            return f'({self.lhs!r} . {self.rhs!r})'

    data = Node(
        Node(
            'a',
            Node('b', Node('c', 'd')),
        ),
        Node(
            'e',
            Node('f', Node('g', 'h')),
        )
    )

    def traverse(node):
        yield node
        if isinstance(node, str):
            return
        for sub in traverse(node.lhs):
            yield sub
        for sub in traverse(node.rhs):
            yield sub

    # Still assume you can get interesting metadata on the first traversal
    proxies = [AnnotatedNode(node) for node in list(traverse(data))]
    # And then modify the actual data, based on what you already collected
    # I know it might look weird, but such a list is effective for bottom-up
    # (that i'm not showing here)
    interesting_branch = proxies[3].node
    proxies[1].node.rhs = 'A'
    print(interesting_branch)  # would otherwise have been an already dead proxy
    print(data)
    del data
    gc.collect()  # just to confirm
    print(interesting_branch)  # would otherwise be a dead proxy
    del proxies
    if promotable_weakref is not None:
        try:
            print(interesting_branch)
            assert False, 'should raise, otherwise means xdecref was never called'
        except ReferenceError: ...
    else:
        ...
        # This time, it is a strong reference, you own it fully
        # we can check it's refcount is 1...
        test_proxy = weakref.proxy(interesting_branch)
        del interesting_branch
        try:
            test_proxy.lhs
            assert False, 'should raise, or refcount is somehow > 0'
        except ReferenceError: ...

example_2()
