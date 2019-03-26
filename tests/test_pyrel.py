# Copyright Peter Roger. All rights reserved.
#
# This file is part of pyrel. Use of this source code is governed by
# the GPL license that can be found in the LICENSE.txt file.

import unittest
from ctypes import c_int, c_char_p
from pyrel import kure, PyrelContext, PyrelException, Relation


class TestPyrelBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.context = PyrelContext()

    @classmethod
    def tearDownClass(cls):
        del cls.context

    def setUp(self):
        self.raw_rels = [] # track unwrapped kure relations for eventual destruction

    def tearDown(self):
        for rel in self.raw_rels:
            kure._rel_destroy(rel)
        self.raw_rels.clear()

    def raw_rel(self, rows, cols):
        _rel = kure._rel_new_with_size_si(self.context._context, c_int(rows), c_int(cols))
        self.raw_rels.append(_rel)
        return _rel

    def kure_error(self):
        msg = self.context._context.contents.error.contents.message.decode('utf-8')
        code = self.context._context.contents.error.contents.code
        raise pyrel.PyrelException(msg, code)

    def assertRelationsEqual(self, relation1, relation2):
        rel1, rel2 = relation1.rel, relation2.rel
        psuccess = c_char_p(b'')
        result = bool(ord(kure._equals(rel1, rel2, psuccess)))
        psuccess = psuccess.value
        if psuccess:
            self.assertTrue(result)
        else:
            self.kure_error()


class TestPyrelContext(TestPyrelBase):

    def testNew(self):
        _rel = self.raw_rel(1, 1)
        expected = Relation(self.context, 0, _rel)
        result = self.context.new()
        self.assertRelationsEqual(expected, result)

    def testNew_0x0(self):
        rows, cols = 0, 0
        expected = Relation(self.context, 0, self.raw_rel(rows, cols))
        result = self.context.new(rows, cols)
        self.assertRelationsEqual(expected, result)

    def testNew_0x1(self):
        rows, cols = 0, 1
        with self.assertRaises(PyrelException):
            result = self.context.new(rows, cols)

    def testNew_n1xn1(self):
        rows, cols = -1, -1
        with self.assertRaises(PyrelException):
            result = self.context.new(rows, cols)

    def testNew_1x1(self):
        rows, cols = 1, 1
        expected = Relation(self.context, 0, self.raw_rel(rows, cols))
        result = self.context.new(rows, cols)
        self.assertRelationsEqual(expected, result)

    def testNew_3x5(self):
        rows, cols = 3, 5
        expected = Relation(self.context, 0, self.raw_rel(rows, cols))
        result = self.context.new(rows, cols)
        self.assertRelationsEqual(expected, result)

    def testNew_5x3(self):
        rows, cols = 5, 3
        expected = Relation(self.context, 0, self.raw_rel(rows, cols))
        result = self.context.new(rows, cols)
        self.assertRelationsEqual(expected, result)

    def testNew_1000x1000(self):
        rows, cols = 1000, 1000
        expected = Relation(self.context, 0, self.raw_rel(rows, cols))
        result = self.context.new(rows, cols)
        self.assertRelationsEqual(expected, result)

    def testNew_1000x1000(self):
        rows, cols = 1, 1000
        expected = Relation(self.context, 0, self.raw_rel(rows, cols))
        result = self.context.new(rows, cols)
        self.assertRelationsEqual(expected, result)

    def testDelete(self):
        r1 = self.context.new()
        r2 = self.context.new()
        self.assertEqual(2, len(self.context.relations))
        self.context.delete(r1)
        self.assertEqual(1, len(self.context.relations))
        self.context.delete(r2.ref)
        self.assertEqual(0, len(self.context.relations))

    def testclean(self):
        r1 = self.context.new()
        r2 = self.context.new()
        self.assertEqual(2, len(self.context.relations))
        self.context.clean()
        self.assertEqual(0, len(self.context.relations))


class TestRelation(TestPyrelBase):

    def setUp(self):
        rows, cols = 4, 4
        self.rel = self.context.new(rows, cols)
        self.expected = self.context.new(rows, cols)

    def tearDown(self):
        self.context.clean()

    def test_set_bits_null(self):
        bits = []
        self.rel.set_bits(bits)
        self.assertRelationsEqual(self.expected, self.rel)

    def test_set_bits_ident(self):
        bits = [(0,0),(1,1),(2,2),(3,3)]
        self.rel.set_bits(bits)
        self.assertRelationsEqual(self.expected.identity(), self.rel)

    def test_unset_bits_(self):
        expected = self.expected.identity().complement()
        bits = [(0,0),(1,1),(2,2),(3,3)]
        self.rel = self.rel.universal()
        self.rel.set_bits(bits, False)
        self.assertRelationsEqual(expected, self.rel)

    def test_set_bits_out_of_range(self):
        bits = [(3,5)]
        with self.assertRaises(PyrelException):
            self.rel.set_bits(bits)

    def test_set_bits_neg_bit(self):
        bits = [(-1,5)]
        with self.assertRaises(PyrelException):
            self.rel.set_bits(bits)

    def test_set_bits_invalid_pair(self):
        bits = [(1,2),(2,)]
        with self.assertRaises(PyrelException):
            self.rel.set_bits(bits)

    def test_set_bits_invalid(self):
        bits = (1,2)
        with self.assertRaises(PyrelException):
            self.rel.set_bits(bits)

    def test_copy(self):
        self.rel.set_bit(3,3)
        self.other = self.rel.copy()
        self.assertRelationsEqual(self.rel, self.other)

    def test_empty(self):
        self.rel.random()
        result = self.rel.empty()
        self.assertRelationsEqual(self.expected, result)

    def test_universal(self):
        self.expected.set_bits([(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)])
        self.rel.random()
        result = self.rel.universal()
        self.assertRelationsEqual(self.expected, result)

    def test_identity(self):
        self.expected.set_bits([(0, 0), (1, 1), (2, 2), (3, 3)])
        self.rel.random()
        result = self.rel.identity()
        self.assertRelationsEqual(self.expected, result)

    def test_meet(self):
        self.expected.set_bits([(1,1),(2,2)])
        self.rel.set_bits([(1,1),(2,2),(3,3)])
        other_rel = self.context.new(4,4, [(0,0),(1,1),(2,2)])
        result = self.rel.meet(other_rel)
        self.assertRelationsEqual(self.expected, result)

    def test_join(self):
        self.expected.set_bits([(0,0),(1,1),(2,2),(3,3)])
        self.rel.set_bits([(1,1),(2,2),(3,3)])
        other_rel = self.context.new(4,4, [(0,0),(1,1),(2,2)])
        result = self.rel.join(other_rel)
        self.assertRelationsEqual(self.expected, result)

    def test_transpose(self):
        self.expected.set_bits([(2,1),(3,2)])
        self.rel.set_bits([(1,2),(2,3)])
        result = self.rel.transpose()
        self.assertRelationsEqual(self.expected, result)

    def test_complement(self):
        self.expected = self.expected.universal()
        result = self.rel.complement()
        self.assertRelationsEqual(self.expected, result)

    def test_composition(self):
        self.expected.set_bits([(0,3),(2,3)])
        self.rel.set_bits([(0,1),(2,3)])
        other_rel = self.context.new(4,4,[(1,3),(3,3)])
        result = self.rel.composition(other_rel)
        self.assertRelationsEqual(self.expected, result)

    def test_equal(self):
        self.rel.set_bits([(0,1),(2,3)])
        self.expected.set_bits([(0,1),(2,3)])
        result = self.rel.equal(self.expected)
        self.assertTrue(result)

    def test_isSuperset(self):
        self.rel.set_bits([(1,1),(2,2)])
        self.expected.set_bits([(1,1)])
        result = self.rel.isSuperset(self.expected)
        self.assertTrue(result)

    def test_isSuperset_not_strict(self):
        self.rel.set_bits([(1,1),(2,2)])
        self.expected.set_bits([(1,1),(2,2)])
        result = self.rel.isSuperset(self.expected)
        self.assertTrue(result)

    def test_isSubset(self):
        self.rel.set_bits([(1,1)])
        self.expected.set_bits([(1,1),(2,2)])
        result = self.rel.isSubset(self.expected)
        self.assertTrue(result)

    def test_isSubset_not_strict(self):
        self.rel.set_bits([(1,1),(2,2)])
        self.expected.set_bits([(1,1),(2,2)])
        result = self.rel.isSubset(self.expected)
        self.assertTrue(result)

    def test_isStrictSuperset(self):
        self.rel.set_bits([(1,1),(2,2)])
        self.expected.set_bits([(1,1)])
        result = self.rel.isStrictSuperset(self.expected)
        self.assertTrue(result)

    def test_isStrictSuperset_not_strict(self):
        self.rel.set_bits([(1,1),(2,2)])
        self.expected.set_bits([(1,1),(2,2)])
        result = self.rel.isStrictSuperset(self.expected)
        self.assertFalse(result)

    def test_isStrictSubset(self):
        self.rel.set_bits([(1,1)])
        self.expected.set_bits([(1,1),(2,2)])
        result = self.rel.isStrictSubset(self.expected)
        self.assertTrue(result)

    def test_isStrictSubset_not_strict(self):
        self.rel.set_bits([(1,1),(2,2)])
        self.expected.set_bits([(1,1),(2,2)])
        result = self.rel.isStrictSubset(self.expected)
        self.assertFalse(result)

    def test_clear(self):
        self.expected = self.expected.empty()
        self.rel.set_bits([(1,1),(2,2)])
        self.rel.clear()
        self.assertRelationsEqual(self.expected, self.rel)


if __name__ == '__main__':
    unittest.main()
