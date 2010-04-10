from twisted.trial import unittest
from formal import form, validation

class TestFormErrors(unittest.TestCase):
    
    def test_nonzero(self):
        e = form.FormErrors()
        self.failIf(not not e)
        self.failUnless(not e)
        e.add(validation.FieldRequiredError('required'))
        self.failIf(not e)
        self.failUnless(not not e)

