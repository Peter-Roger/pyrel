*****
pyrel
*****

Pyrel is an efficient python library for working with and manipulating `binary relations`_. Pyrel exposes the C library `Kure`_ which provides a very fast implementation of binary relations based on `Binary Decision Diagrams`_.

| The following relation operations are provided:

* empty
* universal
* identity
* meet (intersection)
* join (union)
* transpose (converse)
* complement
* composition
* equal
* isSuperset
* isSubset
* isStrictSuperset
* isStrictSubset

Installation
============

.. code-block:: bash

    pip install pyrel


Requirements
------------

Pyrel works on Ubuntu and Macos. It has not been tested on other systems,
but it is possible it could work with some modification.

C Library Dependencies:

* glib-2.0
* gmp
* m

If you are missing these libraries just install them with your package manager.

Pyrel includes Kure (and it's dependency Cudd-2.5.1) as source. As long as the
aforementioned dependencies are installed in default locations on your system,
Kure will be built automatically during installation.


Quick Start
===========

The following provides some examples as a tutorial on how to use pyrel.
For a complete description you should consult the well-documented module `source code`_.

Creating relations
------------------
.. code-block:: python

    import pyrel

    # create a pyrel context
    context = pyrel.PyrelContext()

    # create a new 1x1 empty relation
    r1 = context.new()

    # create a new 3x3 empty relation
    r2 = context.new(3,3)


Setting bits
------------
.. code-block:: python

    rel = context.new(3,3)
    print(rel)

    ...
    ...
    ...

    bits = [(0,0),(0,1),(0,2)]
    rel.set_bits(bits)
    print(rel)

    XXX
    ...
    ...

    # set bits at random
    rel = context.new(3,3)
    rel.random()

    # set bits at creation
    rel = context.new(3,3, bits)

    # set single bit
    rel.set_bit(2,2)
    print(rel)

    XXX
    ...
    ..X

    # unset bit
    rel.set_bit(2,2,yesno=False)

    # unset bits
    rel.set_bits(bits,yesno=False)

Operations
----------
.. code-block:: python

    rel = context.new(3,3).identity()
    print(rel)

    X..
    .X.
    ..X

    r = context.new(3,3, [(0,0),(0,1),(0,2)])
    print(r)

    XXX
    ...
    ...

    s = r.transpose()
    print(s)

    X..
    X..
    X..

    m = r1.meet(r2)
    print(m)

    X..
    ...
    ...

    m = r1.join(r2)
    print(m)

    XXX
    X..
    X..

    r = context.new(3,3, [(0,1),(0,2),(2,1)])
    print(r)

    .XX
    ...
    .X.

    s = context.new(3,3, [(1,1),(2,2)])
    print(s)

    ...
    .X.
    ..X

    g = r.composition(s)
    print(g)

    .XX
    ...
    .X.

    # True
    g.isSubset(g.universal())


.. _binary relations: https://en.wikipedia.org/wiki/Binary_relation
.. _Kure: https://www.informatik.uni-kiel.de/~progsys/kure2/
.. _Binary Decision Diagrams: https://en.wikipedia.org/wiki/Binary_decision_diagram
.. _source code: https://github.com/Peter-Roger/pyrel/pyrel/pyrel.py