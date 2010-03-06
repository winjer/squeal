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

""" Web interface for on-disk music library """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

from twisted.python.util import sibpath

from squeal.web import base

template_dir = sibpath(__file__, 'templates')

def xmltemplate(s):
    return base.xmltemplate(s, template_dir)

class Document(base.BaseElement):
    jsClass = u"Library.Document"
    docFactory = xmltemplate("document.html")

class Main(base.BaseElementContainer):
    docFactory = xmltemplate("main.html")

    contained = {
        'document': Document
    }

