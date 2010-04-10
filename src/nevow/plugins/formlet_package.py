from nevow import athena
from twisted.python import util

import formlet

formletJS = athena.JSPackage({
    'Formlet': util.sibpath(formlet.__file__, 'formlet.js'),
})
