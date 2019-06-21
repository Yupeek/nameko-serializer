# -*- coding: utf-8 -*-
from setuptools import setup
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme_file:
    readme = readme_file.read()


setup(
    name='nameko-serializer',
    version='1.0.0',
    description="nameko serializer compatible with datetime and namedtuple",
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Darius BERNARD',
    author_email='darius@yupeek.com',
    url='https://github.com/Yupeek/nameko-serializer',
    py_modules=['nameko_serializer.serializer'],
    license="GPL3",
    zip_safe=True,
    entry_points={
        'kombu.serializers': [
            'nameko-serializer = nameko_serializer.serializer:register_args'
        ]
    },
    install_requires=[
        'tzlocal',
        'pytz',
    ],
    keywords='nameko json serializer namedtuple datetime',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],

)
