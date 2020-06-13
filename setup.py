# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


import sys
if sys.version_info < (3, 6):
    sys.exit('theverse requires Python 3.6+')
import pathlib
from setuptools import setup




# Extract the version from version.py, using functions in fmtversion.py
fmtversion_path = pathlib.Path(__file__).parent / 'theverse' / 'fmtversion.py'
exec(compile(fmtversion_path.read_text(encoding='utf8'), 'theverse/fmtversion.py', 'exec'))
version_path = pathlib.Path(__file__).parent / 'theverse' / 'version.py'
version = get_version_from_version_py_str(version_path.read_text(encoding='utf8'))

readme_path = pathlib.Path(__file__).parent / 'README.md'
long_description = readme_path.read_text(encoding='utf8')


setup(name='theverse',
      version=version,
      py_modules=[],
      packages=[
          'theverse'
      ],
      package_data = {},
      description='Find properties of objects in our universe (and others) without leaving Python',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Geoffrey M. Poore',
      author_email='gpoore@gmail.com',
      url='http://github.com/gpoore/theverse',
      license='BSD',
      keywords=['reference', 'physics', 'astronomy', 'chemistry', 'planetary system', 'star', 'planet'],
      python_requires='>=3.6',
      install_requires=[
      ],
      # https://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Education',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Education :: Testing',
      ],
      entry_points = {
      },
)
