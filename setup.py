# -*- coding: utf-8 -*-

"""

ABGLEICH
zfs sync tool
https://github.com/pleiszenburg/abgleich

	setup.py: Used for package distribution

	Copyright (C) 2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/abgleich/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from setuptools import (
	find_packages,
	setup,
	)
import os

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Package version
__version__ = '0.0.2'

# List all versions of Python which are supported
python_minor_min = 5
python_minor_max = 8
confirmed_python_versions = [
    'Programming Language :: Python :: 3.{MINOR:d}'.format(MINOR = minor)
    for minor in range(python_minor_min, python_minor_max + 1)
    ]

# Fetch readme file
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
	long_description = f.read()

# Define source directory (path)
SRC_DIR = 'src'

# Install package
setup(
	name = 'abgleich',
	packages = find_packages(SRC_DIR),
	package_dir = {'': SRC_DIR},
	version = __version__,
	description = 'zfs sync tool',
	long_description = long_description,
	long_description_content_type = 'text/markdown',
	author = 'Sebastian M. Ernst',
	author_email = 'ernst@pleiszenburg.de',
	url = 'https://github.com/pleiszenburg/abgleich',
	download_url = 'https://github.com/pleiszenburg/abgleich/archive/v%s.tar.gz' % __version__,
	license = 'LGPLv2',
	keywords = [
		'zfs',
		'ssh',
		],
	scripts = [],
	include_package_data = True,
	python_requires = '>=3.{MINOR:d}'.format(MINOR = python_minor_min),
	setup_requires = [],
	install_requires = [
		'click',
		'tabulate',
		'pyyaml',
		],
	extras_require = {'dev': [
		# 'pytest',
		'python-language-server[all]',
		'setuptools',
		# 'Sphinx',
		# 'sphinx_rtd_theme',
		'twine',
		'wheel',
		]},
	zip_safe = False,
	entry_points = {
		'console_scripts': [
			'abgleich = abgleich.cli:cli',
			],
		},
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: Education',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
		'Operating System :: MacOS',
		'Operating System :: POSIX :: BSD',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python :: 3'
		] + confirmed_python_versions + [
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: Implementation :: CPython',
		'Topic :: Scientific/Engineering',
		'Topic :: System',
		'Topic :: System :: Archiving',
		'Topic :: System :: Archiving :: Backup',
		'Topic :: System :: Archiving :: Mirroring',
		'Topic :: System :: Filesystems',
		'Topic :: System :: Systems Administration',
		'Topic :: Utilities'
		]
	)
