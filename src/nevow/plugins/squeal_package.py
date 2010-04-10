from nevow import athena
from twisted.python import util
import functools

import squeal

sp = functools.partial(util.sibpath, squeal.__file__)

squealJS = athena.JSPackage({
    'Squeal': sp('web/js/squeal.js'),
    'Library': sp('library/js/library.js'),
    'Spot': sp('spot/js/spot.js'),
})
