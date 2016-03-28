#! /usr/bin/env python
import os
from setuptools import setup, find_packages

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name='django-choicer',
    version='0.1',
    description='Simplify dealing with large choices',
    long_description=read('README.rst'),
    license='MIT',
    keywords='django, choices',
    author='Toni Michel',
    author_email='toni.michel@schnapptack.de',
    url="https://github.com/tonimichel/django-choicer.git",
    packages=find_packages(),
    package_dir={'choicer': 'choicer'},
    include_package_data=True,
    scripts=[],
    zip_safe=False,
    classifiers=[
        'License :: schnapptack commercial License',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ],
    install_requires=[

    ]
)
