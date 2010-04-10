from twisted.trial import unittest
from nevow import testutil
from nevow import context

import formal
from formal.validation import FieldRequiredError

class TestForm(unittest.TestCase):

    def test_fieldName(self):
        form = formal.Form()
        form.addField('foo', formal.String())
        self.assertRaises(ValueError, form.addField, 'spaceAtTheEnd ', formal.String())
        self.assertRaises(ValueError, form.addField, 'got a space in it', formal.String())

    def test_process(self):
        form = formal.Form()
        request = testutil.FakeRequest(args={'foo': ['bar', ]})
        ctx = context.RequestContext(tag=request)
        form.addField('foo', formal.String())
        form.addAction(lambda *a, **kw: None)
        d = form.process(ctx)
        d.addCallback(self.failUnlessEqual, None)

        def done(_):
            self.failUnlessEqual(form.data['foo'], 'bar')

        d.addCallback(done)
        return d

    def test_processError(self):
        form = formal.Form()
        request = testutil.FakeRequest()
        ctx = context.RequestContext(tag=request)
        form.addField('foo', formal.String(required=True))
        form.addAction(lambda *a, **kw: None)
        d = form.process(ctx)

        def done(errors):
            self.failIfEqual(errors, None)
            self.failUnless(isinstance(errors.getFieldError('foo'), FieldRequiredError))

        d.addCallbacks(done)
        return d

