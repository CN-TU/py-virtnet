"""virtnet - a library for simplifying network emulation"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='virtnet',
    version='0.0.1',

    description='A library for building testnetworks',
    long_description=long_description,

    url='',

    author='Gernot Vormayr',
    author_email='gernot.vormayr@nt.tuwien.ac.at',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3',
    ],

    packages=find_packages(exclude=['tests', 'docs']),

    install_requires=['pyroute2'],
)
