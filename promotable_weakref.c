#include <Python.h>

// xincref - take the weakref.proxy, increment the refcount
// xdecref - take the weakref.proxy, decrement the refcount

static PyObject*
promotable_xincref(PyObject* self, PyObject* ref)
{
    // if (0 == PyWeakref_Check(ref))  // no need to check 'cause Get{Ref,Object}
    //     return NULL;                // already do this check
    #if PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION >= 13
        PyObject* obj;
        int err = PyWeakref_GetRef(ref, &obj);  // does the INCREF
        if (err == -1)
            return NULL;
        else if (err == 0) {
            PyErr_SetString(PyExc_ReferenceError, "Object already dead upon attempting xincref");
            return NULL;
        }
    #else
        Py_XINCREF(PyWeakref_GetObject(ref));
    #endif
    return Py_None;
}

static PyObject*
promotable_xdecref(PyObject* self, PyObject* ref)
{
    #if PY_MAJOR_VERSION == 3 && PY_MINOR_VERSION >= 13
        PyObject* obj;
        int err = PyWeakref_GetRef(ref, &obj);  // does one INCREF
        if (err == 1) {
            Py_XDECREF(obj);
            Py_XDECREF(obj);
        } else if (err == -1) {
            return NULL;
        } else {
            // no error trying to decref on dead objects?
        }
    #else
        Py_XDECREF(PyWeakref_GetObject(ref));
    #endif
    return Py_None;
}

// Method definition structure
static PyMethodDef PromotableWeakrefMethods[] = {
    {
        "xincref",
        promotable_xincref,
        METH_O,
        "Try increment the refcount of the actual object.\n"
        "No guarantee/warn on already dead objects...\n"
        "On py>=3.13 xincref may raise a MemoryError on dead objects\n"
        "This has to do with better multi-threaded support.\n"
        "So I guess you do better not use this module from multiple threads when your py<3.13"
    },
    {
        "xdecref",
        promotable_xdecref,
        METH_O,
        "Decrement the refcount of the actual object...\n"
    },
    {NULL, NULL, 0, NULL}     // Sentinel
};

// Module definition structure
static struct PyModuleDef promotable_weakref = {
    PyModuleDef_HEAD_INIT,
    "promotable_weakref",           // module name
    "Let your python programmer do the refcount",  // module docstring
    -1,                       // size of per-interpreter state
    PromotableWeakrefMethods
};

// Module initialization function
PyMODINIT_FUNC PyInit_promotable_weakref(void) {
    return PyModule_Create(&promotable_weakref);
}
