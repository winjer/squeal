#! /usr/bin/env python
import sys
from axiom.store import Store
from squeal.library.record import Collection, StandardNamingPolicy
from squeal.isqueal import *

s = Store("db")
c = Collection(store=s, pathname=unicode(sys.argv[1]))
p = StandardNamingPolicy(store=s)
c.powerUp(p, INamingPolicy)
