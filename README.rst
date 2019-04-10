*****
pyrel
*****

Pyrel is an efficient python library for working with and manipulating `binary relations`_. Pyrel exposes the C library `KURE`_ which provides a very fast implementation of binary relations based on `Binary Decision Diagrams`_. Pyrel originally began as a backend component to the relation programming language `Relathon`_. It was seperated into its own library because it is useful in its own right.

The following operations of relation algebra are provided:

* empty
* universal
* identity
* meet (intersection)
* join (union)
* transposition (converse)
* complement (negation)
* compose (multiplication)
* equals
* isSuperset
* isSubset
* isStrictSuperset
* isStrictSubset

Pyrel also provides functions for creating vectors (row constant relations).

Installation
============
using pip:

.. code-block:: bash

    pip3 install pyrel

or downloading with git:

.. code-block:: bash

    git clone https://github.com/Peter-Roger/pyrel.git
    cd pyrel/
    python3 setup.py build install

Requirements
------------

Pyrel works on Ubuntu and macOS. It has not been tested on other systems
but it is possible it could work, perhaps with some modification.

C Library Dependencies:

* glib-2.0
* gmp

If you are missing these libraries just install them with your package manager.

Pyrel includes a modified version of KURE (Kiel University Relation Package) and its dependency Cudd-2.5.1 (Colorado University Decision Diagram) as source. As long as *glib-2.0* and *gmp* are installed in standard locations on your system, KURE and Cudd will be built automatically during installation.


Quick Start
===========

The following provides some examples as a tutorial on how to use pyrel.
For a complete description you should consult the documented module `source code`_.

Relations are represented as boolean matrices and can be visualised by printing them. An 'X' at *col x* and *row y* denotes that *x* is related to *y* in the relation. Contrariwise a '.' denotes that *x* is not related to *y*.


Creating relations
------------------
.. code-block:: python

    import pyrel

    # create a pyrel context
    context = pyrel.PyrelContext()

    # create a new 3x3 empty relation
    rel = context.new(3,3)
    print(rel)

.. code-block:: bash

    ...
    ...
    ...

Setting bits
------------
.. code-block:: python

    # a list of ordered pairs
    bits = [(0,0),(0,1),(0,2)]
    rel = context.new(3,3)
    rel.set_bits(bits)
    print(rel)

    # set bits at random
    rel.random()
    print(rel)

    # unsets all bits
    rel.clear()
    print(rel)

.. code-block:: bash

    XXX
    ...
    ...

    .X.
    ..X
    X.X

    ...
    ...
    ...

.. code-block:: python

    # set bits at creation
    bits = [(0,0),(0,1),(0,2)]
    rel = context.new(3,3,bits)
    print(rel)

    # set single bit
    rel.set_bit(2,2)
    print(rel)

    # unset bit
    rel.set_bit(0,1,yesno=False)
    print(rel)

    # unset bits
    rel.set_bits([(0,0),(2,2)],yesno=False)
    print(rel)

.. code-block:: bash

    XXX
    ...
    ...

    XXX
    ...
    ..X

    X.X
    ...
    ..X

    ..X
    ...
    ...

Operations
----------
.. code-block:: python

    rel = context.new(3,3).identity()
    print(rel)

    r = context.new(3,3, [(0,0),(0,1),(0,2)])
    print(r)

    s = r.transpose()
    print(s)

    m = r1.meet(r2)
    print(m)

    j = r1.join(r2)
    print(j)

.. code-block:: bash

    X..
    .X.
    ..X

    XXX
    ...
    ...

    X..
    X..
    X..

    X..
    ...
    ...

    XXX
    X..
    X..

.. code-block:: python

    r = context.new(3,3, [(0,1),(0,2),(2,1)])
    print(r)

    s = context.new(3,3, [(1,1),(2,2)])
    print(s)

    g = r.composition(s)
    print(g)

    g.isSubset(g.universal())

.. code-block:: bash

    .XX
    ...
    .X.

    ...
    .X.
    ..X

    .XX
    ...
    .X.

    >>> True

Vectors
-------

A vector is a row constant relation. All columns are identical. It represents a subset.

.. code-block:: python

    rel = new(5,5)
    rel.vector(2) # row 2 (0-indexed)
    print(rel)
    rel.vector_next()
    print(rel)

.. code-block:: bash

    .....
    .....
    XXXXX
    .....
    .....

    .....
    .....
    .....
    XXXXX
    .....


Possible Future Work
--------------------

* import relations from a file
* export relations to a file
* extend support for more relation operations


.. _binary relations: https://en.wikipedia.org/wiki/Binary_relation
.. _Relathon: https://github.com/Peter-Roger/relathon
.. _Kure: https://www.informatik.uni-kiel.de/~progsys/kure2/
.. _Binary Decision Diagrams: https://en.wikipedia.org/wiki/Binary_decision_diagram
.. _source code: https://github.com/Peter-Roger/pyrel/blob/master/pyrel/pyrel.py