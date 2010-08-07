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

""" Streaming from spotify to squeezeboxes.  Here be dragons. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from zope.interface import implements
from twisted.python import log
from nevow import rend
from nevow import inevow
from squeal.isqueal import *
import ispotify

import os

import Image
from StringIO import StringIO

class SpotifyStreamingPage(rend.Page):

    def __init__(self, original, pid):
        self.original = original
        self.pid = pid

    def renderHTTP(self, ctx):
        for service in self.original.store.powerupsFor(ispotify.ISpotifyService):
            request = inevow.IRequest(ctx)
            service.squeezebox_request(request, self.pid)
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

