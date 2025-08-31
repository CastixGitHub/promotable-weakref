import weakref, promotable_weakref
import gc


class AnnotatedNode:
    def __init__(self, node, **metadata):
        try:
            self._node = weakref.proxy(node)
        except TypeError:
            self._node = node
        self.metadata = metadata
        self.accessed = False  # could be a counter?

    def __del__(self):
        if self.accessed and isinstance(self._node, weakref.ProxyType):
            promotable_weakref.xdecref(self._node)

    @property
    def node(self):
        assert not self.accessed, 'think about it'
        self.accessed = True
        if isinstance(self._node, weakref.ProxyType):
            promotable_weakref.xincref(self._node)
        return self._node


def example_1():
    class Node:  # simple example, can be whatever
        def __init__(self, next_, **data):
            self.data = data
            self.next_ = next_

    head = Node(Node(Node(Node((tail := Node(None, d=4)), d=3), d=2), d=1), d=0)

    proxies = []
    node = head
    while (node := node.next_):
        proxies.append(AnnotatedNode(node, cached_d=node.data['d']))

    for an in proxies:
        if an.metadata['cached_d'] == 2:
            an.node.next_ = tail
    del an  # remember to also clean the last one if you loop

    node = head
    while (node := node.next_):
        print(node.data)
    # 3 was skipped but like... what's the point?

example_1()

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
    try:
        print(interesting_branch)
        assert False, 'should raise, otherwise means xdecref was never called'
    except ReferenceError: ...
example_2()
