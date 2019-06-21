# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import
import collections
import datetime
import logging
from collections import namedtuple

import sys
from tzlocal import get_localzone

import pytest
from nameko.standalone.rpc import ClusterRpcProxy

from service.service import MyService1, MyService2

MyNamedTuple = namedtuple('MyNamedTuple', ('arg1', 'arg2', 'date', 'datetime'))

logger = logging.getLogger(__name__)

Sample = collections.namedtuple('sample', ['native', 'encoded'])

MyStruct = collections.namedtuple('MyStruct', ['param', 'args'])
MyRootStruct = collections.namedtuple('MyRootStruct', ['struct1', 'struct2', 'name', 'age'])

config = {
    'AMQP_URI': 'amqp://guest:guest@localhost',
    'serializer': 'nameko-serializer'
}

TZ_INFO_STR = '<UTC>' if sys.version_info < (3, 7) else 'datetime.timezone.utc'


@pytest.fixture
def cluster_rpc(runner_factory):
    # run services in the normal manner
    runner = runner_factory(config, MyService1, MyService2)
    runner.start()

    with ClusterRpcProxy(config, timeout=2) as cluster_rpc:
        yield cluster_rpc
        cluster_rpc.myservice2.clear_BAD()
    runner.stop()


def test_encode_str(cluster_rpc):
    assert cluster_rpc.myservice1.method("hellø") == 'hellø'
    assert len(cluster_rpc.myservice2.get_BAD()) == 0


def test_encode_date(cluster_rpc):
    assert cluster_rpc.myservice1.method(datetime.date(2019, 6, 27)) == datetime.date(2019, 6, 28)
    assert sys.version_info < (3, 6) or \
           cluster_rpc.myservice2.get_BAD() == ['datetime.date(2019, 6, 27)']


def test_encode_datetime(cluster_rpc):
    ld = get_localzone().localize(datetime.datetime(2019, 6, 27, 13, 42))
    offset = ld.utcoffset().seconds // 3600
    assert cluster_rpc.myservice1.method(datetime.datetime(2019, 6, 27, 13, 42)) == 13 - offset
    assert sys.version_info < (3, 6) or \
           cluster_rpc.myservice2.get_BAD() == ['datetime.datetime(2019, 6, 27, 11, 42, tzinfo=%s)' % TZ_INFO_STR]


def test_encode_namedtuple(cluster_rpc):

    nt = MyNamedTuple(20, 22, datetime.date(2019, 6, 27), datetime.datetime(2019, 6, 27, 13, 42))
    assert cluster_rpc.myservice1.method(nt) == 42
    assert sys.version_info < (3, 6) or \
           cluster_rpc.myservice2.get_BAD() == [
        'MyNamedTuple(arg1=20, arg2=22, date=datetime.date(2019, 6, 27), '
        'datetime=datetime.datetime(2019, 6, 27, 11, 42, tzinfo=%s))' % TZ_INFO_STR,
    ] * 2


