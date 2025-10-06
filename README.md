# Project retired
Looks like there is no actual need for this project.

Just look at otherwise.py (or better at [yeastr](github.com/yeastr-org/yeastr))

There is no benefit using this extension, you can go 100% python and achieve better results.

# Briefly
Take ownership of borrowed references

So the garbage collector can do it's job

Related to [CPython's gh-138235](https://github.com/python/cpython/issues/138235) (see otherwise.py on how this module may be optional)

Allows the python programmer to tightly think about the refcount, without switching to the C-API

Python >= 3.13 is suggested. (may also work on py2.1?)

#### Usage
You are using `weakref.proxy` to avoid copying a tree (maybe also flattening the tree if feasible),
but then want to move some branch. Since you're working on proxies you do the xincref and store them as long as you need

But before they go out of scope, you have to remember to xdecref them. Otherwise gc will keep them forever

```python
import weakref, promotable_weakref

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
```
