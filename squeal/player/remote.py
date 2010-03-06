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

""" Manage the remote control. """

__author__ = "Doug Winter <doug.winter@isotoma.com>"
__docformat__ = "restructuredtext en"
__version__ = "$Revision$"[11:-2]

class Remote:

    codes = {
        1988737095: 'sleep',
        1988706495: 'power',
        1988739135: 'rewind',
        1988698335: 'pause',
        1988730975: 'forward',
        1988714655: 'add',
        1988694255: 'play',
        1988747295: 'up',
        1988735055: 'down',
        1988726895: 'left',
        1988743215: 'right',
        1988722815: 'volumeup',
        1988690175: 'volumedown',
        1988751375: '1',
        1988692215: '2',
        1988724855: '3',
        1988708535: '4',
        1988741175: '5',
        1988700375: '6',
        1988733015: '7',
        1988716695: '8',
        1988749335: '9',
        1988696295: 'favorites',
        1988728935: '0',
        1988712615: 'search',
        1988718735: 'browse',
        1988745255: 'shuffle',
        1988704455: 'repeat',
        1988720775: 'nowplaying',
        1988753415: 'size',
        1988691195: 'brightness',
    }



