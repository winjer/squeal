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

""" Manage the display on the player. Provides support for rendering text
using local truetype fonts. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

import os
import struct
import Image, ImageDraw, ImageFont

from twisted.python.util import sibpath

fontdir = sibpath(__file__, 'font')

class Font(object):
    
    def __init__(self, name):
        self.filename = os.path.join(fontdir, name + ".ttf")
        self.cache = {}
        
    def render(self, s, size=15):
        """ Returns a PIL image with this string rendered into it """
        self.cache.setdefault(size, ImageFont.truetype(self.filename, size))
        font = self.cache[size]
        siz = font.getsize(s)
        im = Image.new("RGB", siz)
        draw = ImageDraw.Draw(im)
        draw.text((0,0), s, font=font)
        return im

class Display(object):
    
    class Transition:
        
        clear = 'c'
        push_left = 'r'
        push_right = 'l'
        push_up = 'u'
        push_down = 'd'
        bump_left = 'L'
        bump_right = 'R'
        bump_down = 'U'
        bump_up = 'D'
        
    class AnimateState:
        
        none = 0
        client = 1
        scheduled = 2
        server_brief = 5
        clear_scroll = 6
        
    class ScrollState:
        
        none = 0
        server_normal = 1
        server_ticker = 2
    
    def __init__(self):
        self.image = Image.new("1", (320, 32))
        self.fonts = {}
        for f in self.availableFonts():
            self.fonts[f] = Font(f)
            
    def clear(self):
        self.image.paste(0, (0,0,320,32))
        
    def availableFonts(self):
        for f in os.listdir(fontdir):
            if f.endswith(".ttf"):
                yield f[:-len(".ttf")]
        
    def renderText(self, text, fontName, size, position):
        font = self.fonts[fontName]
        im = font.render(text, size)
        self.image.paste(im, position)

    def frame(self):
        """ Return the frame ready for transmission """
        pixmap = self.image.load()
        words = []
        for col in range(0,320):
            word = 0
            for bit in range(0, 32):
                set = 1 if pixmap[col, 31-bit] else 0
                word += set << bit
            words.append(word)
        return struct.pack("!320I", *words)
    