#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Setup script."""

# Copyright (c) 2021 SUSE LLC
#
# This file is part of scc-hypervisor-collector an api and
# command line utilities for collecting hypervisor and
# virtual instance information and upload to SCC.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pathlib
from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()


# Get the version from the toplevel package __init__.py
def get_version(pkg_path, version_file="__init__.py",
                version_attr="__version__"):
    init_py = (pkg_path / version_file)
    for line in init_py.read_text(encoding="utf-8").splitlines():
        if line.startswith(version_attr):
            quote = "'" if "'" in line else '"'
            return line.split(quote)[1]


pkg_name = "scc-hypervisor-collector"
pkg_imp_name = pkg_name.replace('-', '_')
pkg_version = get_version(here / "src" / pkg_imp_name)

# Get the long description from the README.md file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Basic requirements that need to be satisfied to do a pip install
requirements = [
    # scc-hypervisor-collector direct dependencies
    "pyyaml",

    # virtual-host-gatherer dependencies
    "libvirt-python",
    "pycurl",
    "pyvmomi",
    "six",
    "virtual_host_gatherer>=1.0.23",
]

# Recommended testing tools
test_requirements = [
    # pep8 testing
    "flake8",

    # datatypes testing
    "mypy",
    "types-requests",
    "types-PyYaml",

    # pylint testing
    "pylint",

    # pytest testing
    "pytest",
    "pytest[psutils]",
    "pytest-cov",
    "testfixtures",
]

# Recommened developer tools
dev_requirements = [
    "bumpversion",
    "tox",
]

# Tox requirements
tox_requirements = [
    'tox',
    'tox-pyenv'
]


setup(
    name=pkg_name,
    version=pkg_version,
    description=("Collect hypervisor details for upload to "
                 "SUSE Customer Center."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/SUSE/scc-hypervisor-collector',
    author="Fergal Mc Carthy",
    author_email='fmccarthy@suse.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: System :: Systems Administration',
    ],
    package_dir={
        '': 'src'
    },
    packages=find_packages(where='src'),
    entry_points={
        'console_scripts': [
            pkg_name + ' = ' + pkg_imp_name + '.cli:main'
        ]
    },
    python_requires='>=3.6',
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'test': test_requirements,
        'tox': tox_requirements
    },
    keywords='SUSE, SCC, ' + pkg_name + ', ' + pkg_imp_name,
    license='Apache-2.0',
    zip_safe=False,
    include_package_data=True,
    project_urls={
        "Bug Tracker":
            "https://github.com/SUSE/scc-hypervisor-collector/issues",
    },
)
