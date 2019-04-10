# Copyright Peter Roger. All rights reserved.
#
# This file is part of pyrel. Use of this source code is governed by
# the GPL license that can be found in the LICENSE file.

"""This modules provides python wrapper functions for the C library
KURE as well as a ctypes utility function. This module is not
intended to be used directly. Use the module pyrel instead.

KURE is hosted here: https://www.informatik.uni-kiel.de/~progsys/kure2/
"""

import os
import sys
import ctypes
from ctypes.util import find_library


# make function prototypes a bit easier to declare
def wrap_func(name, dll, result, *args):
    """build and apply a ctypes prototype complete with parameter flags

    NOTE: this function was borrowed from this blog
      https://www.cs.unc.edu/~gb/blog/2007/02/11/ctypes-tricks/
    """
    atypes = []
    aflags = []
    if args:
      for arg in args:
          atypes.append(arg[1])
          aflags.append((1, arg[0]))
    else:
      atypes = [None]
    return ctypes.CFUNCTYPE(result, *atypes)((name, dll), tuple(aflags))

if sys.platform == 'darwin':
    shlib_suffix = '.dylib'
else:
    shlib_suffix = '.so'

sh_lib = "libkure{}".format(shlib_suffix)
DIR = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(DIR, "kure", sh_lib)
KURE = ctypes.CDLL(LIB_PATH)

Kure_True = b'\x01'
Kure_False = b'\x00'

class KureError(ctypes.Structure):

    _fields_ = [("message", ctypes.c_char_p),
                ("code", ctypes.c_int)]

c_kure_error_p = ctypes.POINTER(KureError)


class KureContext(ctypes.Structure):

    _fields_ = [("manager", ctypes.c_void_p),
                ("error",ctypes.POINTER(KureError)),
                ("random_func", ctypes.c_void_p),
                ("random_udata", ctypes.c_void_p),
                ("refs", ctypes.c_int)]

c_context_p = ctypes.POINTER(KureContext)


class KureRel(ctypes.Structure):

    _fields_= [("context", c_context_p),
               ("bdd", ctypes.c_void_p),
               ("rows", ctypes.c_void_p),
               ("cols", ctypes.c_void_p)]

c_rel_p = ctypes.POINTER(KureRel)


# context
_context_new = wrap_func("kure_context_new", KURE, c_context_p,
                      (None, ctypes.c_void_p))

_context_destroy = wrap_func("kure_context_destroy", KURE, c_context_p,
                      (None, ctypes.c_void_p))


# relation create/destroy
_rel_new = wrap_func("kure_rel_new", KURE, c_rel_p,
                      ("context", c_context_p,))

_rel_new_copy = wrap_func("kure_rel_new_copy", KURE, c_rel_p,
                      ("R", c_rel_p,))

_rel_new_with_size_si = wrap_func("kure_rel_new_with_size_si", KURE, c_rel_p,
                      ("context", c_context_p),
                      ("rows", ctypes.c_int),
                      ("cols", ctypes.c_int))

_rel_destroy = wrap_func("kure_rel_destroy", KURE, ctypes.c_void_p,
                      ("self", c_rel_p))

_rel_to_string = wrap_func("kure_rel_to_string", KURE, ctypes.c_char_p,
                      ("rel", c_rel_p),
                      ("one_ch", ctypes.c_char),
                      ("zero_ch", ctypes.c_char))


# relation dimension
_rel_get_rows_si = wrap_func("kure_rel_get_rows_si", KURE, ctypes.c_int,
                      ("self", c_rel_p))

_rel_get_cols_si = wrap_func("kure_rel_get_cols_si", KURE, ctypes.c_int,
                      ("self", c_rel_p))

# relation bits
_set_bit_si = wrap_func("kure_set_bit_si", KURE, ctypes.c_char,
                      ("R", c_rel_p),
                      ("yesno", ctypes.c_char),
                      ("row", ctypes.c_int),
                      ("col", ctypes.c_int))

_get_bit_si = wrap_func("kure_get_bit_si", KURE, ctypes.c_char,
                      ("R", c_rel_p),
                      ("row", ctypes.c_int),
                      ("col", ctypes.c_int),
                      ("psuccess", ctypes.c_char_p, 2))


# relation random
_random_simple = wrap_func("kure_random_simple", KURE, ctypes.c_char,
                      ("R", c_rel_p),
                      ("prob", ctypes.c_float))


# relation base operations
_empty = wrap_func("kure_O", KURE,  ctypes.c_char,
                      ("R", c_rel_p))

_universal = wrap_func("kure_L", KURE, ctypes.c_char,
                      ("R", c_rel_p))

_identity = wrap_func("kure_I", KURE, ctypes.c_char,
                      ("R", c_rel_p))

_or = wrap_func("kure_or", KURE, ctypes.c_char,
                      ("rop", c_rel_p),
                      ("arg1", c_rel_p),
                      ("arg2", c_rel_p))

_and = wrap_func("kure_and", KURE, ctypes.c_char,
                      ("rop", c_rel_p),
                      ("arg1", c_rel_p),
                      ("arg2", c_rel_p))

_transpose = wrap_func("kure_transpose", KURE, ctypes.c_char,
                      ("rop", c_rel_p),
                      ("arg", c_rel_p))

_complement = wrap_func("kure_complement", KURE, ctypes.c_char,
                      ("rop", c_rel_p),
                      ("arg", c_rel_p))

_composition = wrap_func("kure_mult", KURE, ctypes.c_char,
                      ("rop", c_rel_p),
                      ("arg1", c_rel_p),
                      ("arg2", c_rel_p))


# relation comparison operations
_equals = wrap_func("kure_equals", KURE, ctypes.c_char,
                      ("R", c_rel_p),
                      ("S", c_rel_p),
                      ("psuccess", ctypes.c_char_p))

_includes = wrap_func("kure_includes", KURE, ctypes.c_char,
                      ("R", c_rel_p),
                      ("S", c_rel_p),
                      ("psuccess", ctypes.c_char_p))

_is_empty = wrap_func("kure_is_empty", KURE, ctypes.c_char,
                      ("R", c_rel_p),
                      ("psuccess", ctypes.c_char_p))


# vectors
_vec_begin_full_si = wrap_func("kure_vec_begin_full_si", KURE, ctypes.c_char,
                      ("v", c_rel_p),
                      ("rows", ctypes.c_int),
                      ("cols", ctypes.c_int))

_vec_next = wrap_func("kure_vec_next", KURE, ctypes.c_char,
                      ("v", c_rel_p),
                      ("arg", c_rel_p))
