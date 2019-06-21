=================
nameko-serializer
=================

enhenced json serializer for nameko micro-services.

1. it allow to pass ``datetime.date`` and ``datetime.datetime`` to rpc calls and event arguments.
   get ride of ``datetime.datetime not JSON serializable`` errors messages in nameko.

2. add support for namedtuple in service transmissions. you return a namedtuple instance,
   you get the same namedtuple in the other side, which is retro-comatible and support either ``res.attr`` or ``res['attr']``

Stable branch

.. image:: https://img.shields.io/travis/Yupeek/nameko-serializer/master.svg
    :target: https://travis-ci.org/Yupeek/nameko-serializer

.. image:: https://readthedocs.org/projects/nameko-serializer/badge/?version=latest
    :target: http://nameko-serializer.readthedocs.org/en/latest/

.. image:: https://coveralls.io/repos/github/Yupeek/nameko-serializer/badge.svg?branch=master
    :target: https://coveralls.io/github/Yupeek/nameko-serializer?branch=master

.. image:: https://img.shields.io/pypi/v/nameko-serializer.svg
    :target: https://pypi.python.org/pypi/nameko-serializer
    :alt: Latest PyPI version

.. image:: https://requires.io/github/Yupeek/nameko-serializer/requirements.svg?branch=master
     :target: https://requires.io/github/Yupeek/nameko-serializer/requirements/?branch=master
     :alt: Requirements Status

Development status

.. image:: https://img.shields.io/travis/Yupeek/nameko-serializer/develop.svg
    :target: https://travis-ci.org/Yupeek/nameko-serializer

.. image:: https://coveralls.io/repos/github/Yupeek/nameko-serializer/badge.svg?branch=develop
    :target: https://coveralls.io/github/Yupeek/nameko-serializer?branch=develop

.. image:: https://requires.io/github/Yupeek/nameko-serializer/requirements.svg?branch=develop
     :target: https://requires.io/github/Yupeek/nameko-serializer/requirements/?branch=develop
     :alt: Requirements Status


Installation
------------

1. Install using pip:

   ``pip install nameko-serializers``

2. Alternatively, you can download or clone this repo and install with :

    ``pip install -e .``.

Requirements
------------

work with nameko up to 1.12.*


Examples
--------

1. install: ``pip install nameko-serializers``
2. configure: add in your config.yaml the folowing line: ``serializer: nameko-serializer``
3. enjoy

datetime support (with timezone)

.. code-block::python

  class MyService2:

    name = "myservice2"

    def compute_date(self, date):
      return date + datetime.timedelta(days=1)


.. code-block::python

  MyNamedTuple = namedtuple('MyNamedTuple', ('arg1', 'arg2', 'date', 'datetime'))

  class MyService2:

    name = "myservice2"

    @rpc
    def compute_date(self, data: MyNamedTuple):
      return data.arg1 + data['arg2']


Documentation
-------------

this Readme is currently the full documentation. it's not a library this big...

features
--------

date and datetime serializing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

this serializer will handle datetime and date serializing. if a datetime is timezone naive, it will be made aware using
the detected current timezone (via ``tzlocal.get_localzone()``)

all received dates will be timezone aware, but the timezone will be fixed to UTC.

NamedTulpe support
^^^^^^^^^^^^^^^^^^

this serializer allow to transmit namedtuple as dict, and will deserialize it as special namedtuple, supporting dict index

.. code-block::python

	# python < 3.6: use collections.namedtuple
	from collections import namedtuple

	MyStruct = namedtuple('MyStruct', ('arg1', 'arg2', 'date', 'datetime'))

	# python >= 3.6: use NamedTulpe from typing, for a better type hinting
	from typing import NamedTuple, Optional

	class MyStruct(NamedTuple):
		arg1: int
		arg2: int
		date: datetime.date
		datetime: Optional[datetime.datetime] = None


	# service with rich type hinting
	class A:
		name = 'a'

		@rpc
		def method(self, struct: MyStruct) -> MyStruct:
			arg1, arg2, date, dt = struct
			assert arg1 + arg2 == struct.arg1 + struct['arg2']
			assert arg1 == struct[0]  # safe only with python3.7+
			return MyStruct(arg1=date.year)





Requirements
------------

- Python 2.7, 3.6, 3.7

.. note::

  this serializer use the builtin ordered dict feature to unserialize namedtuple with correct attributes order.
  if you use python2.7 or 3.6 without cPython, you must exclusively use argument's names and not indice.


.. code-block::python

  MyNamedTuple = namedtuple('SpecialStruct', ('arg1', 'arg2'))

  @rpc
  def myfunc(self, special_struct):
    use_special_struct(*special_struct)  # wrong in python < 3.7, since order is not garanteed
    use_special_struct(special_struct.arg1, special_struct.arg2)  # good in any version


Contributions and pull requests are welcome.


Bugs and requests
-----------------

If you found a bug or if you have a request for additional feature, please use the issue tracker on GitHub.

https://github.com/Yupeek/nameko-serializer/issues


known limitations
-----------------

- if you pass some objects with keys ``__type__``, it will be converted.
- all unserialized dates will be tz aware, and tzinfo will be set to UTC. (this is a good practice to change tz at display time)
- for python < 3.7, the order in the namedtuple is not garanteed, use exclusively kwargs and attrs by names

License
-------

You can use this under GPLv3.

Author
------

Original author: `Darius BERNARD <https://github.com/ornoone>`_.


Thanks
------

Thanks to Nameko for this amazing framework.
