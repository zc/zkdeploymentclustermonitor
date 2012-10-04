##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope.testing import setupstack
import datetime
import manuel.capture
import manuel.doctest
import manuel.testing
import mock
import unittest
import zc.zk.testing
import zim.zkdeploymentclustermonitor.basemonitor.testing

class TZ(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta()

    def dst(*a):
        return datetime.timedelta()

tz = TZ()
def ctime(t):
    return datetime.datetime.fromtimestamp(t, tz).ctime()

def setUp(test):
    setupstack.context_manager(
        test, mock.patch('time.time', return_value=1349378051.73))
    setupstack.context_manager(
        test, mock.patch('time.ctime', side_effect=ctime))
    zc.zk.testing.setUp(test, '', 'zookeeper:2181')
    zim.zkdeploymentclustermonitor.basemonitor.testing.setUp(test)

def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'README.rst',
            setUp=setUp, tearDown=setupstack.tearDown,
            ),
        ))

