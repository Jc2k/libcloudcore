#!/usr/bin/env python

import sys
from setuptools import setup, find_packages


requires = ['jmespath==0.7.1',
            'python-dateutil>=2.1,<3.0.0']


setup(
    name='libcloudcore',
    version="0.0.0",
    description='Data-driven cross-cloud library',
    scripts=[],
    include_package_data=True,
    install_requires=requires,
    license=open("LICENSE.txt").read(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
)
