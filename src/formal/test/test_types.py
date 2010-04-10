from datetime import date, time
try:
    from decimal import Decimal
    haveDecimal = True
except ImportError:
    haveDecimal = False
from twisted.internet import defer
from twisted.trial import unittest
import formal
from formal import validation


class TestValidators(unittest.TestCase):

    def testHasValidator(self):
        t = formal.String(validators=[validation.LengthValidator(max=10)])
        self.assertEquals(t.hasValidator(validation.LengthValidator), True)

    def testRequired(self):
        t = formal.String(required=True)
        self.assertEquals(t.hasValidator(validation.RequiredValidator), True)
        self.assertEquals(t.required, True)


class TestCreation(unittest.TestCase):

    def test_immutablility(self):
        self.assertEquals(formal.String().immutable, False)
        self.assertEquals(formal.String(immutable=False).immutable, False)
        self.assertEquals(formal.String(immutable=True).immutable, True)

    def test_immutablilityOverride(self):
        class String(formal.String):
            immutable = True
        self.assertEquals(String().immutable, True)
        self.assertEquals(String(immutable=False).immutable, False)
        self.assertEquals(String(immutable=True).immutable, True)


class TestValidate(unittest.TestCase):


    @defer.deferredGenerator
    def runSuccessTests(self, type, tests):
        for test in tests:
            d = type(*test[0], **test[1]).validate(test[2])
            d = defer.waitForDeferred(d)
            yield d
            self.assertEquals(d.getResult(), test[3])


    @defer.deferredGenerator
    def runFailureTests(self, type, tests):
        for test in tests:
            d = type(*test[0], **test[1]).validate(test[2])
            d = defer.waitForDeferred(d)
            yield d
            self.assertRaises(test[3], d.getResult)


    def testStringSuccess(self):
        return self.runSuccessTests(formal.String, [
                ([], {}, None, None),
                ([], {}, '', None),
                ([], {}, ' ',  ' '),
                ([], {},  'foo', 'foo'),
                ([], {}, u'foo', u'foo'),
                ([], {'strip': True}, ' ', None),
                ([], {'strip': True}, ' foo ', 'foo'),
                ([], {'missing': 'bar'}, 'foo', 'foo'),
                ([], {'missing': 'bar'}, '', 'bar'),
                ([], {'strip': True, 'missing': ''}, ' ', ''),
                ])


    def testStringFailure(self):
        return self.runFailureTests(formal.String, [
            ([], {'required': True}, '', formal.FieldValidationError),
            ([], {'required': True}, None, formal.FieldValidationError),
            ])


    def testIntegerSuccess(self):
        return self.runSuccessTests(formal.Integer, [
                ([], {}, None, None),
                ([], {}, 0, 0),
                ([], {}, 1, 1),
                ([], {}, -1, -1),
                ([], {'missing': 1}, None, 1),
                ([], {'missing': 1}, 2, 2),
                ])


    def testIntegerFailure(self):
        return self.runFailureTests(formal.Integer, [
            ([], {'required': True}, None, formal.FieldValidationError),
            ])


    def testFloatSuccess(self):
        self.runSuccessTests(formal.Float, [
            ([], {}, None, None),
            ([], {}, 0, 0.0),
            ([], {}, 0.0, 0.0),
            ([], {}, .1, .1),
            ([], {}, 1, 1.0),
            ([], {}, -1, -1.0),
            ([], {}, -1.86, -1.86),
            ([], {'missing': 1.0}, None, 1.0),
            ([], {'missing': 1.0}, 2.0, 2.0),
            ])

    
    def testFloatFailure(self):
        self.runFailureTests(formal.Float, [
            ([], {'required': True}, None, formal.FieldValidationError),
            ])


    if haveDecimal:

        def testDecimalSuccess(self):
            return self.runSuccessTests(formal.Decimal, [
                ([], {}, None, None),
                ([], {}, Decimal('0'), Decimal('0')),
                ([], {}, Decimal('0.0'), Decimal('0.0')),
                ([], {}, Decimal('.1'), Decimal('.1')),
                ([], {}, Decimal('1'), Decimal('1')),
                ([], {}, Decimal('-1'), Decimal('-1')),
                ([], {}, Decimal('-1.86'), Decimal('-1.86')),
                ([], {'missing': Decimal('1.0')}, None, Decimal('1.0')),
                ([], {'missing': Decimal('1.0')}, Decimal('2.0'), Decimal('2.0')),
                ])


        def testDecimalFailure(self):
            return self.runFailureTests(formal.Decimal, [
                ([], {'required': True}, None, formal.FieldValidationError),
                ])


    def testBooleanSuccess(self):
        return self.runSuccessTests(formal.Boolean, [
            ([], {}, None, None),
            ([], {}, True, True),
            ([], {}, False, False),
            ([], {'missing' :True}, None, True),
            ([], {'missing': True}, False, False)
            ])


    def testDateSuccess(self):
        return self.runSuccessTests(formal.Date, [
            ([], {}, None, None),
            ([], {}, date(2005, 1, 1), date(2005, 1, 1)),
            ([], {'missing': date(2005, 1, 2)}, None, date(2005, 1, 2)),
            ([], {'missing': date(2005, 1, 2)}, date(2005, 1, 1), date(2005, 1, 1)),
            ])


    def testDateFailure(self):
        return self.runFailureTests(formal.Date, [
            ([], {'required': True}, None, formal.FieldValidationError),
            ])


    def testTimeSuccess(self):
        self.runSuccessTests(formal.Time, [
            ([], {}, None, None),
            ([], {}, time(12, 30, 30), time(12, 30, 30)),
            ([], {'missing': time(12, 30, 30)}, None, time(12, 30, 30)),
            ([], {'missing': time(12, 30, 30)}, time(12, 30, 31), time(12, 30, 31)),
            ])


    def testTimeFailure(self):
        self.runFailureTests(formal.Time, [
            ([], {'required': True}, None, formal.FieldValidationError),
            ])


    def testSequenceSuccess(self):
        self.runSuccessTests(formal.Sequence, [
            ([formal.String()], {}, None, None),
            ([formal.String()], {}, ['foo'], ['foo']),
            ([formal.String()], {'missing': ['foo']}, None, ['foo']),
            ([formal.String()], {'missing': ['foo']}, ['bar'], ['bar']),
            ])


    def testSequenceFailure(self):
        self.runFailureTests(formal.Sequence, [
            ([formal.String()], {'required': True}, None, formal.FieldValidationError),
            ([formal.String()], {'required': True}, [], formal.FieldValidationError),
            ])

    def test_file(self):
        pass
    test_file.skip = "write tests"

