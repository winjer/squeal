
"""
Tests for L{epsilon.view}.
"""

from operator import getitem

from twisted.trial.unittest import TestCase

from epsilon.view import SlicedView


class SlicedViewTests(TestCase):
    """
    Tests for L{SlicedView}
    """
    def test_outOfBoundsPositiveStart(self):
        """
        Verify that the C{__getitem__} of a L{SlicedView} constructed with a
        slice with a positive start value greater than the maximum allowed
        index clips that start value to the end of the underlying sequence.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(3, None))
        self.assertRaises(IndexError, getitem, view, 0)


    def test_outOfBoundsNegativeStart(self):
        """
        Verify that the C{__getitem__} of a L{SlicedView} constructed with a
        slice with a negative start value greater than the maximum allowed
        index clips that start value to the beginning of the underlying
        sequence.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-4, None))
        self.assertEqual(view[0], 'a')
        self.assertEqual(view[1], 'b')
        self.assertEqual(view[2], 'c')
        self.assertRaises(IndexError, getitem, view, 3)


    def test_outOfBoundsPositiveStop(self):
        """
        Verify that the C{__getitem__} of a L{SlicedView} constructed with a
        slice with a positve stop value greater than the maximum allowed index
        clips that stop value to the end of the underlying sequence.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None, 4))
        self.assertEqual(view[0], 'a')
        self.assertEqual(view[1], 'b')
        self.assertEqual(view[2], 'c')
        self.assertRaises(IndexError, getitem, view, 3)


    def test_outOfBoundsNegativeStop(self):
        """
        Verify that the C{__getitem__} of a L{SlicedView} constructed with a
        slice with a negative stop value greater than the maximum allowed index
        clips that stop value to the beginning of the underlying sequence.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None, -4))
        self.assertRaises(IndexError, getitem, view, 0)


    def test_positiveIndices(self):
        """
        Verify that the C{__getitem__} of a L{SlicedView} constructed with a
        slice with no start or stop value behaves in the same way as the
        underlying sequence with respect to indexing with positive values.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None))
        self.assertEqual(view[0], 'a')
        self.assertEqual(view[1], 'b')
        self.assertEqual(view[2], 'c')
        self.assertRaises(IndexError, getitem, view, 3)


    def test_negativeIndices(self):
        """
        Similar to L{test_positiveIndices}, but for negative indices.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None))
        self.assertEqual(view[-1], 'c')
        self.assertEqual(view[-2], 'b')
        self.assertEqual(view[-3], 'a')
        self.assertRaises(IndexError, getitem, view, -4)


    def test_length(self):
        """
        Verify that L{SlicedView.__len__} returns the length of the underlying
        sequence when the SlicedView is constructed with no start or stop
        values.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None))
        self.assertEqual(len(view), 3)


    def test_lengthEmptySequence(self):
        """
        Verify that L{SlicedView.__len__} works with empty sequences.
        """
        sequence = []
        view = SlicedView([], slice(None))
        self.assertEqual(len(view), 0)


    def test_positiveStartLength(self):
        """
        Similar to L{test_length}, but for a L{SlicedView} constructed with a
        slice with a positive start value.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(1, None))
        self.assertEqual(len(view), 2)


    def test_negativeStartLength(self):
        """
        Similar to L{test_length}, but for a L{SlicedView} constructed with a
        slice with a negative start value.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-2, None))
        self.assertEqual(len(view), 2)


    def test_positiveStopLength(self):
        """
        Similar to L{test_length}, but for a L{SlicedView} constructed with a
        slice with a positive stop value.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None, 2))
        self.assertEqual(len(view), 2)


    def test_negativeStopLength(self):
        """
        Similar to L{test_length}, but for a L{SlicedView} constructed with a
        slice with a negative stop value.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None, -1))
        self.assertEqual(len(view), 2)


    def test_positiveStartPositiveStopLength(self):
        """
        Similar to L{test_length}, but for a L{SlicedView} constructed with a
        slice with positive start and stop values.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(1, 2))
        self.assertEqual(len(view), 1)


    def test_positiveStartNegativeStopLength(self):
        """
        Similar to L{test_length}, but for a L{SlicedView} constructed with a
        slice with a positive start value and a negative stop value.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(1, -1))
        self.assertEqual(len(view), 1)


    def test_negativeStartPositiveStopLength(self):
        """
        Similar to L{test_length}, but for a L{SlicedView} constructed with a
        slice with a negative start value and a positive stop value.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-2, 2))
        self.assertEqual(len(view), 1)


    def test_negativeStartNegativeStopLength(self):
        """
        Similar to L{test_length}, but for a L{SlicedView} constructed with a
        slice with negative start and stop values.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-2, -1))
        self.assertEqual(len(view), 1)


    def test_extendedSliceLength(self):
        """
        Verify that L{SlicedView.__len__} reports the correct length when a
        step is present.
        """
        sequence = ['a', 'b', 'c', 'd', 'e']
        view = SlicedView(sequence, slice(1, -1, 2))
        self.assertEqual(len(view), 2)


    def test_positiveStartOnlyPositiveIndices(self):
        """
        Verify that the C{__getitem__} of a L{SlicedView} constructed with a
        slice with only a positive start value returns elements at the
        requested index plus the slice's start value for positive requested
        indices.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(1, None))
        self.assertEqual(view[0], 'b')
        self.assertEqual(view[1], 'c')
        self.assertRaises(IndexError, getitem, view, 2)


    def test_positiveStartOnlyNegativeIndices(self):
        """
        Similar to L{test_positiveStartOnlyPositiveIndices}, but cover
        negative requested indices instead of positive ones.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(1, None))
        self.assertEqual(view[-1], 'c')
        self.assertEqual(view[-2], 'b')
        self.assertRaises(IndexError, getitem, view, -3)


    def test_negativeStartOnlyPositiveIndices(self):
        """
        Similar to L{test_positiveStartOnlyPositiveIndices}, but for the case
        of a negative slice start value.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-2, None))
        self.assertEqual(view[0], 'b')
        self.assertEqual(view[1], 'c')
        self.assertRaises(IndexError, getitem, view, 2)


    def test_negativeStartOnlyNegativeIndices(self):
        """
        Similar to L{test_negativeStartOnlyPositiveIndices}, but cover negative
        requested indices instead of positive ones.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-2, None))
        self.assertEqual(view[-1], 'c')
        self.assertEqual(view[-2], 'b')
        self.assertRaises(IndexError, getitem, view, -3)


    def test_positiveStopOnlyPositiveIndices(self):
        """
        Verify that L{__getitem__} of L{SlicedView} constructed with a slice
        with a positive stop value returns elements at the requested index for
        indices less than the stop value and raises IndexError for positive
        requested indices greater than or equal to the stop value.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None, 2))
        self.assertEqual(view[0], 'a')
        self.assertEqual(view[1], 'b')
        self.assertRaises(IndexError, getitem, view, 2)


    def test_positveStopOnlyNegativeIndices(self):
        """
        Similar to L{test_positiveStopOnlyPositiveIndices}, but cover negative
        requested indices instead of positive ones.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None, 2))
        self.assertEqual(view[-1], 'b')
        self.assertEqual(view[-2], 'a')
        self.assertRaises(IndexError, getitem, view, -3)


    def test_negativeStopOnlyPositiveIndices(self):
        """
        Similar to L{test_positiveStopOnlyPositiveIndices}, but test a
        L{SlicedView} created with a slice with a negative stop value.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None, -1))
        self.assertEqual(view[0], 'a')
        self.assertEqual(view[1], 'b')
        self.assertRaises(IndexError, getitem, view, 2)


    def test_negativeStopOnlyNegativeIndices(self):
        """
        Similar to L{test_negativeStopOnlyPositiveIndices}, but cover negative
        requested indices instead of positive ones.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(None, -1))
        self.assertEqual(view[-1], 'b')
        self.assertEqual(view[-2], 'a')
        self.assertRaises(IndexError, getitem, view, -3)


    def test_positiveStartPositiveStopPositiveIndices(self):
        """
        Verify that L{__getitem__} of L{SlicedView} constructed with a slice
        with positive start and stop values returns elements at the requested
        index plus the slice's start value for positive requested indices less
        than the difference between the stop and start values and raises
        IndexError for positive requested indices greater than or equal to that
        difference.
        """
        sequence = ['a', 'b', 'c', 'd']
        view = SlicedView(sequence, slice(1, 3))
        self.assertEqual(view[0], 'b')
        self.assertEqual(view[1], 'c')
        self.assertRaises(IndexError, getitem, view, 2)


    def test_positiveStartPositiveStopNegativeIndices(self):
        """
        Similar to L{test_positiveStartPositiveStopPositiveIndices}, but cover
        negative requested indices instead of positive ones.
        """
        sequence = ['a', 'b', 'c', 'd']
        view = SlicedView(sequence, slice(1, 3))
        self.assertEqual(view[-1], 'c')
        self.assertEqual(view[-2], 'b')
        self.assertRaises(IndexError, getitem, view, -3)


    def test_positiveStartNegativeStopPositiveIndices(self):
        """
        Verify that L{__getitem__} of a L{SlicedView} constructed with a slice
        with a positive start and a negative stop value returns elements at the
        requested index plus the slice's start value for positive requested
        indices within the bounds defined by the stop value and raises an
        IndexError for positive requested indices outside those bounds.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(1, -1))
        self.assertEqual(view[0], 'b')
        self.assertRaises(IndexError, getitem, view, 1)


    def test_positiveStartNegativeStopNegativeIndices(self):
        """
        Similar to L{test_positiveStartNegativeStopPositiveIndices}, but cover
        negative requested indices instead of positive ones.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(1, -1))
        self.assertEqual(view[-1], 'b')
        self.assertRaises(IndexError, getitem, view, -2)


    def test_negativeStartPositiveStopPositiveIndices(self):
        """
        Similar to L{test_positiveStartNegativeStopPositiveIndices}, but for a
        negative slice start and positive slice stop.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-2, 2))
        self.assertEqual(view[0], 'b')
        self.assertRaises(IndexError, getitem, view, 1)


    def test_negativeStartPositiveStopNegativeIndices(self):
        """
        Similar to L{test_negativeStartPositiveStopPositiveIndices}, but cover
        negative requested indices instead of positive ones.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-2, 2))
        self.assertEqual(view[-1], 'b')
        self.assertRaises(IndexError, getitem, view, -2)


    def test_negativeStartNegativeStopPositiveIndices(self):
        """
        Similar to L{test_negativeStartPositiveStopPositiveIndices}, but for a
        negative slice stop.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-2, -1))
        self.assertEqual(view[0], 'b')
        self.assertRaises(IndexError, getitem, view, 1)


    def test_negativeStartNegativeStopNegativeIndices(self):
        """
        Similar to L{test_negativeStartPositiveStopPositiveIndices}, but cover
        negative requested indices instead of positive ones.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(-2, -1))
        self.assertEqual(view[-1], 'b')
        self.assertRaises(IndexError, getitem, view, -2)


    def test_positiveStepPositiveIndices(self):
        """
        Verify that a positive step produces the correct results, skipping over
        the appropriate elements.
        """
        sequence = ['a', 'b', 'c', 'd', 'e']
        view = SlicedView(sequence, slice(1, -1, 2))
        self.assertEqual(view[0], 'b')
        self.assertEqual(view[1], 'd')
        self.assertRaises(IndexError, getitem, view, 2)


    def test_positiveStepNegativeIndices(self):
        """
        Verify that a negative step produces the correct results, skipping over
        the appropriate elements.
        """
        sequence = ['a', 'b', 'c', 'd', 'e']
        view = SlicedView(sequence, slice(1, -1, 2))
        self.assertEqual(view[-1], 'd')
        self.assertEqual(view[-2], 'b')
        self.assertRaises(IndexError, getitem, view, -3)


    def test_negativeStepPositiveIndices(self):
        """
        Verify that a negative step produces the correct results, skipping over
        the appropriate elements.
        """
        sequence = ['a', 'b', 'c', 'd', 'e']
        view = SlicedView(sequence, slice(-1, 1, -2))
        self.assertEqual(view[0], 'e')
        self.assertEqual(view[1], 'c')
        self.assertRaises(IndexError, getitem, view, 2)


    def test_negativeStepNegativeIndices(self):
        """
        Verify that a negative step produces the correct results, skipping over
        the appropriate elements.
        """
        sequence = ['a', 'b', 'c', 'd', 'e']
        view = SlicedView(sequence, slice(-1, 1, -2))
        self.assertEqual(view[-1], 'c')
        self.assertEqual(view[-2], 'e')
        self.assertRaises(IndexError, getitem, view, -3)


    def test_slice(self):
        """
        Verify a L{SlicedView} itself can be sliced.
        """
        sequence = ['a', 'b', 'c']
        view = SlicedView(sequence, slice(1, None))
        viewView = view[1:]
        self.assertIdentical(viewView.sequence, view)
        self.assertEqual(viewView.bounds, slice(1, None, None))
