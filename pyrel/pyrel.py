# Copyright Peter Roger. All rights reserved.
#
# This file is part of pyrel. Use of this source code is governed by
# the GPL license that can be found in the LICENSE file.

"""This module provides a python interface to Kure (Kiel University
Relation Package), a C library providing a fast implementation of
Binary Relations based on Binary Decision Diagrams. A number of methods
for working with and manipulating binary relations are provided
including meet (intersection), join (union), composition
(multiplication), complement (negation), transpose, and others.

To use this library first create a PyrelContext object. Use the methods
new() and delete() to create and destroy relations. Then use the
Relation object methods to manipulate and perform operations on
the relations.

NOTE: Do not try to perform operations on relations that belong to
different PyrelContexts.

Classes:
    PyrelContext: Creates and destroys relations
    Relation: Binary Relation object providing a number of
              relational operations

Exceptions:
    PyrelException: Exceptions produced by pyrel
"""

from . import kure
from ctypes import c_char, c_char_p, c_float, c_int, c_void_p


class PyrelException(Exception):
    """Exceptions produced from pyrel and a wrapper for exceptions
    produced by Kure.
    """

    def __init__(self, msg, code=None):
        """Args:
            msg (str): Human readable string describing the exception.
            code (int, optional): KureError code.

        Attributes:
            msg (str): Human readable string describing the exception.
            code (int): Exception KureError code.
            """
        self.msg = msg
        self.code = code

    def __str__(self):
        return "{}: {}.".format(self.__class__.__name__, self.msg)[:-1]

class PyrelContext:
    """A PyrelContext is used to create and destroy relations. All
    relations belong to exactly one context. Operations on Relations
    from different contexts is not possible. Destroying a context
    destroys all relations it contains.
    """
    def __init__(self):
        """Inititialize PyrelContext.

        Attributes:
            _context (KureContext): Wrapped KureContext C Object.
            ref (int): Incrementing reference number confered to
                       each newly created relation to uniquely
                       identify them
            relations (dict): Tracks relations; maps reference number
                              to relation
        """
        self._context = kure._context_new(None)
        self.ref = 0
        self.relations = {}

    def __del__(self):
        self.clean()
        kure._context_destroy(self._context)
        self._context = None

    def new(self, rows=1, cols=1, bits=None):
        """Create a new relation.

        Args:
            rows (int; default 1): Number of rows
            cols (int; defualt 1): Number of columns
            bits (list of row,col pairs): row,col pairs to set

        Raises:
            PyrelException: If the dimension specified by rows/cols is
                            invalid
        """
        isValidDimension = False
        if type(rows) == int and type(cols) == int:
            isValidDimension = (rows == 0 and cols == 0) or (rows > 0 and cols > 0)
        if not isValidDimension:
            raise PyrelException("Invalid dimension.")
        rel = kure._rel_new_with_size_si(self._context, c_int(rows), c_int(cols))
        self.ref += 1
        self.relations[self.ref] = rel
        relation = Relation(self, self.ref, rel)
        if bits:
            relation.set_bits(bits)
        return relation

    def _add(self, rel):
        """Tracks newly created relations.

        Note: Private function. Never call this.

        Args:
            rel (Relation): New relation to track
        """
        self.ref += 1
        self.relations[self.ref] = rel
        return self.ref

    def delete(self, toDelete):
        """Delete a relation.

        Args:
            toDelete (Relation or Relation reference number)
        """
        if isinstance(toDelete, Relation):
            toDelete = toDelete.ref
        rel = self.relations.get(toDelete, None)
        if rel:
            kure._rel_destroy(rel)
            del self.relations[toDelete]

    def clean(self):
        """Destroy all relations in context."""
        while self.relations:
            _, rel = self.relations.popitem()
            kure._rel_destroy(rel)

class Relation:
    """Binary Relation object.

    Attributes:
        one_ch (str): How set bits are represented when printing
        zero_ch (zerochar): How unset bits are represented when printing
    """

    one_ch = 'X'
    zero_ch = '.'

    def __init__(self, context, ref, rel):
        """Inititialize Relation

        Args:
            context (PyrelContext): The originating PyrelContext to which the relation belongs
            ref (int): Uniquely identifying relation reference number
            rel (KureRel): Wrapped KureRelation C object

        Attributes:
            context (PyrelContext): Associated PyrelContext
            ref (int): reference
            rel (KureRel): relation
            rows (int): Number of rows in relation
            cols (int): Number of cols in relation
        """
        self.context = context
        self.ref = ref
        self.rel = rel
        self.rows = kure._rel_get_rows_si(self.rel)
        self.cols = kure._rel_get_cols_si(self.rel)

    def __del__(self):
        self.context.delete(self.ref)

    def __str__(self):
        _true = self.one_ch.encode('ASCII')
        _false = self.zero_ch.encode('ASCII')
        b = kure._rel_to_string(self.rel, _true, _false)
        return b.decode(encoding="utf-8")

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.equals(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def _is_relation(self, arg):
        """Returns True if arg is of type Relation, raises
        PyrelException otherwise.

        Args:
            arg (obj): argument to check

        Raises:
            PyrelException if arg is not type Relation
        """
        if type(arg) != Relation:
            raise PyrelException("argument type must be relation")
        return True

    def _kure_error(self):
        """Handles errors generated from Kure library.

        Raises:
            PyrelException
        """
        msg = self.context._context.contents.error.contents.message.decode('utf-8')
        code = self.context._context.contents.error.contents.code
        raise PyrelException(msg, code)

    def is_empty(self):
        psuccess = c_char_p(b'')
        result = kure._is_empty(self.rel, psuccess)
        if result == kure.Kure_True:
            return True
        elif result == kure.Kure_False:
            return False
        else:
            self._error()

    def set_bit(self, row, col, yesno=True):
        """Set a bit.

        Args:
            row (int): row number
            col (int): column number
            yesno (bool; default True): If true sets bit to one,
                                        zero otherwise

        Returns:
            None if operation was successful, raises exception otherwise
        """
        kure_yesno = kure.Kure_True if yesno else kure.Kure_False
        if not bool(ord(kure._set_bit_si(self.rel, kure_yesno, row, col))):
            self._kure_error()

    def set_bits(self, bits, yesno=True):
        """Set a sequence of bits.

        Args:
            bits (list): list of row,col pairs to be set
            yesno (bool; default True): If true sets bit to one,
                                        zero otherwise

        Returns:
            True if operation was successful, raises exception otherwise

        Raises:
            PyrelException
        """
        success = True
        try:
            for row, col in bits:
                self.set_bit(row, col, yesno)
        except (TypeError, ValueError):
            raise PyrelException("Invalid (row, col) bit pair.")

    def copy(self):
        """Create deep copy of relation.

        Returns:
            copy of relation

        Raises:
            PyrelException
        """
        rel = kure._rel_new_copy(self.rel)
        if rel:
            ref = self.context._add(rel)
            return Relation(self.context, ref, rel)
        else:
            self._kure_error()

    def clear(self):
        """Set all bits to zero.

        Raises:
            PyrelException if operation was unsuccessful
        """
        success = bool(ord(kure._empty(self.rel)))
        if not success:
            self._kure_error()

    def random(self, prob=0.5):
        """Set bits at random.

        Args:
            prob (float): probability between 0.0 and 1.0 that a bit
                          will be set

        Raises:
            PyrelException if operation was unsuccessful
        """
        self.clear()
        if isinstance(prob, float) and prob > 0.0:
            prob = min(1.0, prob)
            success = kure._random_simple(self.rel, c_float(prob))
            if not success:
                self._kure_error()
        else:
            raise PyrelException("Invalid argument. Prob must be a float \
                between 0.0 and 1.0.")

    def empty(self):
        """Creates the empty relation of the same dimension.

        Returns:
            the empty relation (O)

        Raises:
            PyrelException if operation was unsuccessful
        """
        result = self.context.new(self.rows, self.cols)
        success = bool(ord(kure._empty(result.rel)))
        if success:
            return result
        else:
            self._kure_error()

    def universal(self):
        """Creates the universal relation of the same dimension.

        Returns:
            the universal relation (L)

        Raises:
            PyrelException if operation was unsuccessful
        """
        result = self.context.new(self.rows, self.cols)
        success = bool(ord(kure._universal(result.rel)))
        if success:
            return result
        else:
            self._kure_error()

    def identity(self):
        """Creates the identity relation of the same dimension.

        Returns:
            the identity relation (I)

        Raises:
            PyrelException if operation was unsuccessful
        """
        result = self.context.new(self.rows, self.cols)
        success = bool(ord(kure._identity(result.rel)))
        if success:
            return result
        else:
            self._kure_error()

    def meet(self, other):
        """Meet (intersection) with other relation.

        Args:
            other (Relation): other relation

        Returns:
            The intersection of two relations

        Raises:
            PyrelException if operation was unsuccessful
        """
        self._is_relation(other)
        result = self.context.new(self.rows, self.cols)
        success = bool(ord(kure._and(result.rel, self.rel, other.rel)))
        if success:
            return result
        else:
            self._kure_error()

    def join(self, other):
        """Join (Union) with other relation.

        Args:
            other (Relation): other relation

        Returns:
            The union of two relations

        Raises:
            PyrelException if operation was unsuccessful
        """
        self._is_relation(other)
        result = self.context.new(self.rows, self.cols)
        success = bool(ord(kure._or(result.rel, self.rel, other.rel)))
        if success:
            return result
        else:
            self._kure_error()

    def transpose(self):
        """Transpose (converse) relation.

        Returns:
            the transposed relation

        Raises:
            PyrelException if operation was unsuccessful
        """
        result = self.context.new(self.rows, self.cols)
        success = bool(ord(kure._transpose(result.rel, self.rel)))
        if success:
            return result
        else:
            self._kure_error()

    def complement(self):
        """Complement (negatation) relation.

        Returns:
             the complemented relation

        Raises:
            PyrelException if operation was unsuccessful
        """
        result = self.context.new(self.rows, self.cols)
        success = bool(ord(kure._complement(result.rel, self.rel)))
        if success:
            return result
        else:
            self._kure_error()

    def composition(self, other):
        """Compose (mutliply) relation with another relation. Other
        relation must be compatable in dimension.

        Args:
            other (Relation): other relation

        Returns:
            the composed relation

        Raises:
            PyrelException if operation was unsuccessful
        """
        self._is_relation(other)
        result = self.context.new(self.rows, self.cols)
        success = bool(ord(kure._composition(result.rel, self.rel, other.rel)))
        if success:
            return result
        else:
            self._kure_error()

    def equals(self, other):
        """Check equality of two relations.

        Args:
            other (Relation): other relation

        Returns:
            True if relation is equal, otherwise False

        Raises:
            PyrelException if operation was unsuccessful
        """
        self._is_relation(other)
        psuccess = c_char_p(b'')
        result = bool(ord(kure._equals(self.rel, other.rel, psuccess)))
        psuccess = psuccess.value
        if psuccess:
            return result
        else:
            self._kure_error()

    def notEquals(self, other):
        """Check equality of two relations.

        Args:
            other (Relation): other relation

        Returns:
            True if relation is equal, otherwise False

        Raises:
            PyrelException if operation was unsuccessful
        """
        return not self.equals(other)

    def isSuperset(self, other):
        """Check if other relation is a superset.

        Args:
            other (Relation): other relation

        Returns:
            True if relation is superset, otherwise False

        Raises:
            PyrelException if operation was unsuccessful
        """
        self._is_relation(other)
        psuccess = c_char_p(b'')
        result = bool(ord(kure._includes(other.rel, self.rel, psuccess)))
        psuccess = psuccess.value
        if psuccess:
            return result
        else:
            self._kure_error()

    def isSubset(self, other):
        """Check if other relation is a subset.

        Args:
            other (Relation): other relation

        Returns:
            True if relation is subset, otherwise False

        Raises:
            PyrelException if operation was unsuccessful
        """
        self._is_relation(other)
        psuccess = c_char_p(b'')
        result = bool(ord(kure._includes(self.rel, other.rel, psuccess)))
        psuccess = psuccess.value
        if psuccess:
            return result
        else:
            self._kure_error()

    def isStrictSuperset(self, other):
        """Check if other relation is a strict superset.

        Args:
            other (Relation): other relation

        Returns:
            True if relation is a strict superset, otherwise False

        Raises:
            PyrelException if operation was unsuccessful
        """
        self._is_relation(other)
        return self.isSuperset(other) and not self.equals(other)

    def isStrictSubset(self, other):
        """Check if other relation is a strict superset.

        Args:
            other (Relation): other relation

        Returns:
            True if relation is a strict superset, otherwise False

        Raises:
            PyrelException if operation was unsuccessful
        """
        self._is_relation(other)
        return self.isSubset(other) and not self.equals(other)

    def vector(self, vector=0):
        """Turn the relation into a vector.

        Args:
            vector (int): the vector (row)

        Raises:
            PyrelException if operation was unsuccessful
        """
        if type(vector) != int:
            raise PyrelException("Invalid vector arg. Must be int.")
        success = bool(ord(kure._vec_begin_full_si(self.rel, c_int(self.rows), c_int(self.cols))))
        if not success:
            self._kure_error()
        self.vector_next(increment=vector)

    def vector_next(self, increment=1):
        """Increment the vector.

        Raises:
            PyrelException if operation was unsuccessful
        """
        for i in range(increment):
            success = bool(ord(kure._vec_next(self.rel, self.rel)))
            if not success:
                self._kure_error()