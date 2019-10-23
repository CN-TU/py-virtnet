"""virtnet - a library for simplifying network emulation"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='py-virtnet',
    version='1.0.1',

    description='A library for building testnetworks',
    long_description=long_description,
    long_description_content_type='text/markdown; charset=UTF-8',

    python_requires=">=3.5",

    url='https://github.com/CN-TU/py-virtnet',

    author='Gernot Vormayr',
    author_email='gvormayr@gmail.com',

    license='GPLv2',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',

        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        'Operating System :: POSIX :: Linux',

        'Topic :: System :: Networking',

        'Programming Language :: Python :: 3',
    ],

    packages=find_packages(exclude=['tests', 'docs']),

    install_requires=['pyroute2'],
)
