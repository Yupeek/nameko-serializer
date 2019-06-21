# -*- coding: utf-8 -*-
import datetime

import pytest
import pytz
import sys

from nameko_serializer.serializer import datecompatible_dumps, datecompatible_loads
import logging
import collections

logger = logging.getLogger(__name__)

Sample = collections.namedtuple('sample', ['native', 'encoded'])

MyStruct = collections.namedtuple('MyStruct', ['param', 'args'])
MyRootStruct = collections.namedtuple('MyRootStruct', ['struct1', 'struct2', 'name', 'age'])

SAMPLES = [
    Sample(
        {'status_code': 404, 'status_text': 'darius not found', 'success': False, 'progress': False, 'fail': True},
        '{"status_code": 404, "status_text": "darius not found", "success": false, "progress": false, "fail": true}'
    ),
    Sample(
        MyStruct(1, 'dada'),
        '{"__type__": "__namedtuple__", "__module__": "test_serializers", "__name__": "MyStruct", '
        '"param": 1, "args": "dada"}'
    ),
    Sample(
        {'a': [], 'b': {'bb': 42, 'bc': 'bc'}, 'c': 24},
        '{"a": [], "b": {"bb": 42, "bc": "bc"}, "c": 24}'
    ),
    Sample(
        [pytz.timezone('Europe/Paris').localize(datetime.datetime(1988, 3, 7, 12, 5)), datetime.date(2013, 5, 24)],
        '[{"__type__": "__datetime__", "utcisodate": "1988-03-07T11:05:00+00:00", "epoch": 573732300}, '
        '{"__type__": "__date__", "utcisodate": "2013-05-24", "epoch": 1369346400}]'
    ),
    Sample(
        MyStruct(MyStruct('ber', 'nard'), 'dada'),
        '{"__type__": "__namedtuple__", "__module__": "test_serializers", "__name__": "MyStruct", '
        '"param": {"__type__": "__namedtuple__", "__module__": "test_serializers", "__name__": "MyStruct", '
        '"param": "ber", "args": "nard"}, "args": "dada"}'
    ),
    Sample(
        MyRootStruct(MyStruct('ber', 'nard'), MyStruct('dar', 'ius'), 'darius', 31),
        '{"__type__": "__namedtuple__", "__module__": "test_serializers", "__name__": "MyRootStruct", '
        '"struct1": {"__type__": "__namedtuple__", "__module__": "test_serializers", "__name__": "MyStruct", '
        '"param": "ber", "args": "nard"}, "struct2": {'
        '"__type__": "__namedtuple__", "__module__": "test_serializers", "__name__": "MyStruct", '
        '"param": "dar", "args": "ius"}, "name": "darius", "age": 31}'
    ),
    Sample(
        {'a': [], 'b': MyStruct('bb', {'bb': 42, 'bc': 'bc'}), 'c': 24},
        '{"a": [], "b": {"__type__": "__namedtuple__", "__module__": "test_serializers", "__name__": "MyStruct", '
        '"param": "bb", "args": {"bb": 42, "bc": "bc"}}, "c": 24}'
    )
]


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
@pytest.mark.parametrize("fixture", SAMPLES)
def test_encode_leaf(fixture):
    enc = datecompatible_dumps(fixture.native)
    assert enc == fixture.encoded


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
@pytest.mark.parametrize("fixture", SAMPLES)
def test_decode_leaf(fixture):
    native = datecompatible_loads(fixture.encoded)
    print(fixture)
    assert native == fixture.native


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
@pytest.mark.parametrize("fixture", SAMPLES)
def test_full_chained_decode(fixture):
    encoded = datecompatible_dumps(fixture.native)
    native = datecompatible_loads(encoded)
    assert native == fixture.native


def test_encode_default_raise():
    with pytest.raises(TypeError):
        datecompatible_dumps(datetime.timedelta(1))


def test_factory_nametuple():
    json_d = '{"__type__": "__namedtuple__", "__module__": "test_serializers", "__name__": "MyStruct", ' \
             '"param": "bb", "args": null}'
    native = datecompatible_loads(json_d)  # type: MyStruct
    assert native['param'] == 'bb'
    assert native.param == 'bb'
    assert len(native) == 2


def test_broken_nametuple():
    json_d = ' {"__type__": "__namedtuple__", "__module__": "test_serializers", "__name__": 1, "param": "bb"}'
    with pytest.raises(ValueError):
        native_fallback = datecompatible_loads(json_d)  # type: dict


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_datenaiv_to_timestamp():
    dt = datetime.datetime(1988, 3, 7, 12, 5)
    assert datecompatible_dumps(dt) == '{"__type__": "__datetime__", ' \
                                       '"utcisodate": "1988-03-07T11:05:00+00:00", "epoch": 573732300}'


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
@pytest.mark.parametrize("dt", [
    datetime.datetime(1988, 3, 7, 12, 5),
    datetime.datetime(1988, 3, 7, 11, 5, tzinfo=pytz.utc),
    pytz.timezone('Europe/Paris').localize(datetime.datetime(1988, 3, 7, 12, 5)),
    pytz.timezone('Europe/Moscow').localize(datetime.datetime(1988, 3, 7, 14, 5)),
])
def test_date_to_isoformat(dt):
    assert datecompatible_dumps(dt) == '{"__type__": "__datetime__", ' \
                                       '"utcisodate": "1988-03-07T11:05:00+00:00", "epoch": 573732300}'


def test_isoformat_to_date():
    d = '{"__type__": "__datetime__", "utcisodate": "1988-03-07T11:05:00+00:00"}'
    loaded = datecompatible_loads(d)
    assert loaded == datetime.datetime(1988, 3, 7, 11, 5, tzinfo=pytz.utc)
    assert loaded.tzinfo is not None
