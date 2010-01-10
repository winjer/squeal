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

class SpotifyStreamer(rend.Page):

    def __init__(self, original, playlist, track):
        self.original = original
        self.playlist = playlist
        self.track = track

    def renderHTTP(self, ctx):
        for service in self.original.store.powerupsFor(ISpotify):
            request = inevow.IRequest(ctx)
            SpotifyTransfer(self.playlist, self.track, service, request)
            return request.deferred
