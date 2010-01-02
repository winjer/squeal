#! /usr/bin/env python

""" This eliminates the moaning about updating the plugin cache """

from twisted.plugin import getPlugins
from zope.interface import Interface

for i in getPlugins(Interface):
    print i
