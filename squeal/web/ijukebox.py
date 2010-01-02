
from zope.interface import Interface, Attribute

class ISearchStartedEvent(Interface):
    """ We have triggered a search on spotify. """
    