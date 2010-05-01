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
import ispotify

import Image
from StringIO import StringIO

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
        self.written = 0
        request.registerProducer(self, 1)
        self.service.registerConsumer(self, tid)

    def resumeProducing(self):
        log.msg("resumeProducing", system="squeal.spot.sfy.SpotifyTransfer")
        if not self.request:
            return
        if self.data:
            # calling write multiple times causes a slew of pauses to come back
            self.request.write("".join(self.data))
            self.data = []
        if self.finished:
            self.request.unregisterProducer()
            self.request.finish()
            self.request = None
        self.paused = False

    def pauseProducing(self):
        log.msg("pauseProducing", system="squeal.spot.sfy.SpotifyTransfer")
        self.paused = True

    def stopProducing(self):
        log.msg("stopProducing", system="squeal.spot.sfy.SpotifyTransfer")
        #self.producer.stopProducing()
        #self.request = None

    def write(self, data):
        """ Called by spotify to queue data to send to the squeezebox  """

        if not self.request:
            self.stopProducing()
            log.msg("overrun: writing to a closed request", system="squeal.spot.sfy.SpotifyTransfer")
            return
        self.written += len(data)
        if self.written % (1024*1024) == 0:
            log.msg("%d written" % self.written,  system="squeal.spot.sfy.SpotifyTransfer")
        if self.paused:
            # you'd think just returning 0 here would work, but it causes
            # the sound to skip
            self.data.append(data)
        else:
            self.request.write(data)

    def registerProducer(self, producer, streaming):
        log.msg("registerProducer", system="squeal.spot.sfy.SpotifyTransfer")
        self.producer = producer

    def unregisterProducer(self):
        """ Called by the spotify service when the end of track is reached. We
        may stop receiving data long before we stop sending it of course, so
        the request remains active. """
        log.msg("unregisterProducer", system="squeal.spot.sfy.SpotifyTransfer")
        self.producer = None
        self.finished = True

class SpotifyStreamer(rend.Page):

    def __init__(self, original, tid):
        self.original = original
        self.tid = tid

    def renderHTTP(self, ctx):
        for service in self.original.store.powerupsFor(ispotify.ISpotifyService):
            request = inevow.IRequest(ctx)
            SpotifyTransfer(self.tid, service, request)
            return request.deferred

class SpotifyImage(rend.Page):

    def __init__(self, original, image_id, size=None):
        self.original = original
        self.image_id = image_id
        self.size = size

    def renderHTTP(self, ctx):
        request = inevow.IRequest(ctx)
        def _(image):
            request.setHeader("content-type", "image/jpeg")
            if self.size is not None:
                s = StringIO(image.data())
                i = Image.open(s)
                i.thumbnail([int(self.size), int(self.size)], Image.ANTIALIAS)
                s2 = StringIO()
                i.save(s2, "JPEG")
                return s2.getvalue()
            return str(image.data())
        for service in self.original.store.powerupsFor(ispotify.ISpotifyService):
            d = service.image(self.image_id)
            d.addCallback(_)
            return d

