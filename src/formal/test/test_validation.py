import re
from twisted.trial import unittest
from formal import types, validation


class TestRequired(unittest.TestCase):
    
    def test_required(self):
        v = validation.RequiredValidator()
        v.validate(types.String(), 'bar')
        self.assertRaises(validation.FieldRequiredError, v.validate, types.String(), None)
        
        
class TestRange(unittest.TestCase):
    
    def test_range(self):
        self.assertRaises(AssertionError, validation.RangeValidator)
        v = validation.RangeValidator(min=5, max=10)
        v.validate(types.Integer(), None)
        v.validate(types.Integer(), 5)
        v.validate(types.Integer(), 7.5)
        v.validate(types.Integer(), 10)
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), 0)
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), 4)
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), -5)
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), 11)
        
    def test_rangeMin(self):
        v = validation.RangeValidator(min=5)
        v.validate(types.Integer(), None)
        v.validate(types.Integer(), 5)
        v.validate(types.Integer(), 10)
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), 0)
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), 4)
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), -5)
        
    def test_rangeMax(self):
        v = validation.RangeValidator(max=5)
        v.validate(types.Integer(), None)
        v.validate(types.Integer(), -5)
        v.validate(types.Integer(), 0)
        v.validate(types.Integer(), 5)
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), 6)
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), 10)
        
        
class TestLength(unittest.TestCase):
    
    def test_length(self):
        self.assertRaises(AssertionError, validation.LengthValidator)
        v = validation.LengthValidator(min=5, max=10)
        v.validate(types.String(), None)
        v.validate(types.String(), '12345')
        v.validate(types.String(), '1234567')
        v.validate(types.String(), '1234567890')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), '')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), '1234')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), '12345678901')
        
    def test_lengthMin(self):
        v = validation.LengthValidator(min=5)
        v.validate(types.String(), None)
        v.validate(types.String(), '12345')
        v.validate(types.String(), '1234567890')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), '')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), '1234')
        
    def test_lengthMax(self):
        v = validation.LengthValidator(max=5)
        v.validate(types.String(), None)
        v.validate(types.String(), '1')
        v.validate(types.String(), '12345')
        v.validate(types.String(), '123')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), '123456')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), '1234567890')
        
        
class TestPattern(unittest.TestCase):
    
    def test_pattern(self):
        v = validation.PatternValidator('^[0-9]{3,5}$')
        v.validate(types.String(), None)
        v.validate(types.String(), '123')
        v.validate(types.String(), '12345')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), ' 123')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), '1')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), 'foo')
        
    def test_regex(self):
        v = validation.PatternValidator(re.compile('^[0-9]{3,5}$'))
        v.validate(types.String(), None)
        v.validate(types.String(), '123')
        v.validate(types.String(), '12345')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), ' 123')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), '1')
        self.assertRaises(validation.FieldValidationError, v.validate, types.String(), 'foo')
        
