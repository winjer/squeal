
from zope.interface import implements

from axiom.item import Item
from axiom.attributes import text

from squeal import isqueal

class UserDetails(Item):

    implements(isqueal.ISquealAccount)
    powerupInterfaces = (isqueal.ISquealAccount,)

    username = text()
    name = text()