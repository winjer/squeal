# $Id$
#
# Copyright 2010 Doug Winter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Controllers specific to spotify. Will probably be pulled out into a
spotify plugin in some form. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from zope.interface import implements
from twisted.internet.interfaces import IConsumer, IProducer, IPushProducer
from twisted.python import log
from nevow import rend
from nevow import inevow
from squeal.isqueal import *

class SpotifyTransfer(object):

    """ Implements the streaming interface between spotify and a web request. """

    implements(IConsumer, IProducer, IPushProducer)

    request = None

    def __init__(self, tid, service, request):
        log.msg("Initiating transfer", system="squeal.spot.sfy.SpotifyTransfer")
        self.tid = tid
        self.request = request
        self.service = service
        self.data = []
        self.paused = False
        self.finished = False
        request.registerProducer(self, 1)
        self.service.registerConsumer(self, tid)

    def resumeProducing(self):
        if not self.request:
            return
        if self.data:
            for x in self.data:
                self.request.write(x)
            self.data = []
        if self.finished:
            self.request.unregisterProducer()
            self.request.finish()
            self.request = None
        self.paused = False

    def pauseProducing(self):
        self.paused = True
        pass

    def stopProducing(self):
        self.producer.stopProducing()
        self.request = None

    def write(self, data):
        """ Called by spotify to queue data to send to the squeezebox  """

        if not self.request:
            log.warning("overrun: writing to a closed request", system="squeal.spot.sfy.SpotifyTransfer")
            return
        if self.paused:
            self.data.append(data)
        else:
            self.request.write(data)

    def registerProducer(self, producer, streaming):
        self.producer = producer

    def unregisterProducer(self):
        self.request.unregisterProducer()
        self.request.finish()
        self.producer = None
        self.request = None

class SpotifyStreamer(rend.Page):

    def __init__(self, original, tid):
        self.original = original
        self.tid = tid

    def renderHTTP(self, ctx):
        for service in self.original.store.powerupsFor(ISpotify):
            request = inevow.IRequest(ctx)
            SpotifyTransfer(self.tid, service, request)
            return request.deferred
