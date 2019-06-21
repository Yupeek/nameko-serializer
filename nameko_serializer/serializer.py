# -*- coding: utf-8 -*-
"""
this contains the serializer that will accept a datetime to transmit througth rabbitmq
"""
import collections
import datetime
import json
import logging
from time import mktime

import pytz
import sys
from tzlocal import get_localzone

if sys.version_info < (3, 7):
    def datetime_fromisoformat(time_str):
        return pytz.utc.localize(datetime.datetime.strptime(time_str[:19], '%Y-%m-%dT%H:%M:%S'))

    def date_fromisoformat(time_str):
        return datetime.datetime.strptime(time_str[:11], '%Y-%m-%d').date()

else:
    datetime_fromisoformat, date_fromisoformat = datetime.datetime.fromisoformat, datetime.date.fromisoformat

logger = logging.getLogger(__name__)


class RemoteNamedTuple(object):
    """
    base class for custom made named tuple. can be used to check via isinstance
    allow to use a nameko result either with attrs or items:

    a['attr'] or a.attr
    """
    def __getitem__(self, item):
        if isinstance(item, str):
            return getattr(self, item)
        else:
            return super(RemoteNamedTuple, self).__getitem__(item)


class NamedTupleFactory(object):
    catalog = {}

    def __call__(self, obj):
        attrs = {k: v for k, v in obj.items() if k not in {'__name__', '__type__', '__module__'}}

        s = frozenset(attrs.keys())
        nt = self.catalog.get(s)
        if nt is None:
            # not in catalog, we create it
            name = obj.get('__name__', 'UnknStruct')
            nt = type(str(name), (RemoteNamedTuple, collections.namedtuple(name, attrs.keys()), ), {})
            if '__module__' in obj:
                nt.__module__ = obj['__module__']
            self.catalog[s] = nt

        return nt(**attrs)


namedtuple_factory = NamedTupleFactory()


class DateCompatibleJSONEncode(json.JSONEncoder):
    namedtuple_type = '__namedtuple__'
    datetime_type = '__datetime__'
    date_type = '__date__'

    def replace_namedtuple(self, o):
        """
        function to  replace recursively all instance of a namedtuple
        with a dict containing the values, along with a special key __type__ = __namedtuple__
        this will not mutate o
        :param o: const: the object to recursively treat with namedtuple
        :return: o
        """
        if isinstance(o, tuple) and hasattr(o, '_asdict'):
            return dict(
                __type__=self.namedtuple_type,
                __module__=o.__class__.__module__,
                __name__=o.__class__.__name__,
                **{k: self.replace_namedtuple(v) for k, v in o._asdict().items()}
            )
        elif isinstance(o, (list, tuple)):

            return tuple(self.replace_namedtuple(i) for i in o)
        elif isinstance(o, dict):
            return {k: self.replace_namedtuple(v) for k, v in o.items()}
        else:
            return o

    def iterencode(self, o, *args, **kwargs):
        return super(DateCompatibleJSONEncode, self).iterencode(self.replace_namedtuple(o), *args, **kwargs)

    def default(self, obj):
        if isinstance(obj, datetime.datetime):

            if obj.tzinfo is None:
                # timezone naive date: we localize it ot corrent timezone and writeit as UTC date
                awaredate = get_localzone().localize(obj).astimezone(pytz.utc)
            else:
                awaredate = obj.astimezone(pytz.utc)
            return {
                '__type__': self.datetime_type,
                'utcisodate': awaredate.isoformat(),
                'epoch': int(mktime(awaredate.timetuple()))  # retrocompatible
            }
        elif isinstance(obj, datetime.date):
            return {
                '__type__': self.date_type,
                'utcisodate': obj.isoformat(),
                'epoch': int(mktime(obj.timetuple())),  # retrocompatible
            }
        else:
            return json.JSONEncoder.default(self, obj)


def datecompatible_decoder(obj):
    __type__ = obj.get('__type__', None)
    if __type__:

        if __type__ == DateCompatibleJSONEncode.datetime_type:
            if 'utcisodate' in obj:
                return datetime_fromisoformat(obj['utcisodate'])
            else:  # pragma: nocover
                return datetime.datetime.fromtimestamp(obj['epoch'])  # retrocompatible
        elif __type__ == DateCompatibleJSONEncode.date_type:
            if 'utcisodate' in obj:
                return date_fromisoformat(obj['utcisodate'])
            else:  # pragma: nocover
                return datetime.date.fromtimestamp(obj['epoch'])  # retrocompatible
        elif __type__ == DateCompatibleJSONEncode.namedtuple_type:
            return namedtuple_factory(obj)
    return obj


# Encoder function
def datecompatible_dumps(obj):
    return json.dumps(obj, cls=DateCompatibleJSONEncode)


# Decoder function
def datecompatible_loads(obj):
    return json.loads(obj, object_hook=datecompatible_decoder)


register_args = (
    datecompatible_dumps,
    datecompatible_loads,
    'application/x-myjson',
    'utf-8'
)


def register_datecompatible_serializer():  # pragma: nocover
    from kombu.serialization import register
    register('json_datecompatible', *register_args)
