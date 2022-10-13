# Copyright Peter Roger. All rights reserved.
#
# This file is part of pyrel. Use of this source code is governed by
# the GPL license that can be found in the LICENSE file.

"""Build Kure shared library."""

import argparse
import ctypes.util
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from setuptools import distutils
from distutils.errors import CompileError, LinkError


FILE_PATH = os.path.dirname(os.path.realpath(__file__))
PREFIX = os.path.join(FILE_PATH, 'pyrel')
DIR = os.path.join(PREFIX, 'kure')
# CUDD
CUDD_VERSION = '2.5.1'
CUDD_DIRS = ['cudd', 'dddmp', 'epd', 'mtr', 'st', 'util']
CUDD_PATH = os.path.join(DIR, 'cudd-{v}'.format(v=CUDD_VERSION))
CUDD_TARBALL = "{}.tar.gz".format(CUDD_PATH)

# KURE
KURE_LIBS = []
KURE_DEP = ['glib-2.0', 'gmp', 'm']
for lib in KURE_DEP: # check for C dependencies
    path = ctypes.util.find_library('{}'.format(lib))
    if path is None:
        raise OSError("Could not find dependency {}.".format(lib))
    KURE_LIBS.append(lib)
KURE_TARBALL = 'kure2-2.2.tar.gz'
KURE_PATH = os.path.join(DIR, 'kure2-2.2')
KURE_CFLAGS = ['-O3', '-g', '-w']
KURE_INC = [os.path.join(KURE_PATH, 'include'),\
               os.path.join(CUDD_PATH, 'include')]
KURE_LDFLAGS = [os.path.join(KURE_PATH, 'lib'),\
                os.path.join(CUDD_PATH, 'lib')]

cfg_vars = distutils.sysconfig.get_config_vars()

# macOS
if sys.platform == 'darwin':
    KURE_LIBS.extend(['kure', *CUDD_DIRS])
    cfg_vars['LDSHARED'] = cfg_vars['LDSHARED'].replace('-bundle', '-dynamiclib')
    cfg_vars['SHLIB_SUFFIX'] = '.dylib'
    cfg_vars['LDSHARED'] += ' -all_load'

# Ubuntu
else:
    CUDD_LIBS = ' '.join(['-l'+dir_ for dir_ in CUDD_DIRS])
    cfg_vars['LDSHARED'] = 'cc -shared -L/{}/lib -L/{}/lib -Wl,--whole-archive -Bstatic -lkure {} -Wl,--no-whole-archive'.format(KURE_PATH, CUDD_PATH, CUDD_LIBS)

def untar(fname):
    """Extract contents of tar file `fname`."""
    print("++ unpack: {f}".format(f=fname))
    with tarfile.open(fname) as tar:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar)
    print("-- done unpacking.")

def make_cudd():
    """Compile CUDD."""
    print("++ compiling CUDD")
    os.chdir(DIR)
    untar(CUDD_TARBALL)
    subprocess.call(['make'], cwd=CUDD_PATH)
    os.chdir(FILE_PATH)
    print("-- compiled CUDD")

def make_kure():
    """Compile KURE"""
    print("++ compiling KURE")
    os.chdir(DIR)
    untar(KURE_TARBALL)
    subprocess.Popen(['make', "PREFIX=\'{}\'".format(DIR)], cwd=KURE_PATH).wait()
    os.chdir(FILE_PATH)
    print("-- compiled KURE")

def make_kure_shlib():
    """Compile and link Kure shared library."""
    print("++ building shared library")
    compiler = distutils.ccompiler.new_compiler()
    assert isinstance(compiler, distutils.ccompiler.CCompiler)
    distutils.sysconfig.customize_compiler(compiler)

    # write temporary .c file to compile to shared library
    tmp_dir = tempfile.mkdtemp(prefix='tmp_dir_', dir='.')
    os.chdir(tmp_dir)
    file_name = "kure.c"
    with open(file_name, 'w') as fp:
        c_code = """#include <Kure.h>"""
        fp.write(c_code)
    try:
        obj = compiler.compile([file_name],
            extra_preargs= KURE_CFLAGS,
            include_dirs = KURE_INC,
            debug = True)
        compiler.link_shared_lib(obj, "kure",
            output_dir = DIR,
            libraries = KURE_LIBS,
            runtime_library_dirs = KURE_LDFLAGS,
            debug = True)
    except CompileError:
        print('-- Compile error: library not built')
    except LinkError:
        print('-- Link error: library not built')
    else:
        print("-- shared library built")
    finally:
        os.chdir(FILE_PATH)
        shutil.rmtree(tmp_dir)

def make_all():
    """Compile and link CUDD and KURE."""
    make_cudd()
    make_kure()
    make_kure_shlib()

def clean():
    cfg_vars = distutils.sysconfig.get_config_vars()
    suffix = cfg_vars['SHLIB_SUFFIX']
    files = [(os.path.join(DIR,'libkure{}'.format(suffix)), os.remove),
            (CUDD_PATH, shutil.rmtree),
            (KURE_PATH, shutil.rmtree)]
    for f, rm in files:
        try:
            rm(f)
        except OSError:
            continue

if __name__ == '__main__':
    make_all()