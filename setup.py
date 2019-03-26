# Copyright Peter Roger. All rights reserved.
#
# This file is part of pyrel. Use of this source code is governed by
# the GPL license that can be found in the LICENSE file.

"""Installation script."""
import argparse
import os
import sys
import build_kure
from setuptools import setup, Extension, find_packages
from distutils.command.build import build


NAME = 'pyrel'
DESCRIPTION = ('An efficient python library for working with'
    ' and manipulating binary relations.')
with open("README.rst", "r") as fh:
    LONG_DESCRIPTION = fh.read()
AUTHOR = "Peter Roger"
URL = 'https://github.com/Peter-Roger/{name}'.format(name=NAME)
MAJOR = 0
MINOR = 1
MICRO = 4
VERSION = '{major}.{minor}.{micro}'.format(
    major=MAJOR, minor=MINOR, micro=MICRO)
LICENSE = 'GPLv3'


class BuildKure(build):
    """Customized setuptools build command - builds Kure on build."""
    def run(self):
        build_kure.make_all()
        build.run(self)


def run_setup():
    """Build C Library dependencies and install pyRel."""
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/x-rst',
        author=AUTHOR,
        url=URL,
        license=LICENSE,
        platforms=['darwin', 'linux'],
        cmdclass={'build': BuildKure},
        py_modules=['build_kure'],
        packages=['pyrel'],
        package_data={'pyrel' : ['kure/libkure.*', 'kure/kure2-2.2.tar.gz', 'kure/cudd-2.5.1.tar.gz']},
        test_suite='tests/test_pyrel.py'
    )

if __name__ == '__main__':
    run_setup()
