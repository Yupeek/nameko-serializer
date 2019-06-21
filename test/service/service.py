# -*- coding: utf-8 -*-
import datetime
import logging

from nameko.events import EventDispatcher, event_handler
from nameko.rpc import RpcProxy, rpc
from nameko_serializer.serializer import RemoteNamedTuple

logger = logging.getLogger(__name__)

BAD_GLOBAL = []


class MyService1:

    name = 'myservice1'

    myservice2 = RpcProxy('myservice2')  # type: MyService2

    dispatch = EventDispatcher()
    """
    :type: typing.Callable
    """

    @rpc
    def method(self, arg):
        if isinstance(arg, datetime.datetime):
            self.dispatch("on_datetime", arg)
            return self.myservice2.compute_datetime(arg)
        elif isinstance(arg, datetime.date):
            self.dispatch("on_date", arg)
            return self.myservice2.compute_date(arg)
        elif isinstance(arg, RemoteNamedTuple):
            self.dispatch('on_namedtulpe', arg)
            self.dispatch('on_%s' % arg.__class__.__name__, arg)
            return self.myservice2.compute_nt(arg)
        else:
            return arg


class MyService2:

    name = "myservice2"

    @rpc
    def compute_date(self, date):
        return date + datetime.timedelta(days=1)

    @rpc
    def compute_datetime(self, datetime):
        """
        pass
        :param datetime.datetime datetime:
        :return:
        """
        return datetime.hour

    @rpc
    def compute_nt(self, nt):
        """
        return attrs of namedtuple
        :param MyNamedTuple|RemoteNamedTuple nt:
        :return:
        """
        return nt.arg1 + nt['arg2']

    @event_handler('myservice1', 'on_date')
    def handle_on_date(self, date):
        BAD_GLOBAL.append(repr(date))

    @event_handler('myservice1', 'on_datetime')
    def handle_on_datetime(self, datetime):
        BAD_GLOBAL.append(repr(datetime))

    @event_handler('myservice1', 'on_namedtulpe')
    def handle_on_namedtulpe(self, nt):
        BAD_GLOBAL.append(repr(nt))

    @event_handler('myservice1', 'on_MyNamedTuple')
    def handle_on_mynamedtuple(self, mynamedtuple):
        BAD_GLOBAL.append(repr(mynamedtuple))

    @rpc
    def get_BAD(self):
        return BAD_GLOBAL

    @rpc
    def clear_BAD(self):
        del BAD_GLOBAL[:]