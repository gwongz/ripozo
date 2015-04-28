from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import ValidationException, TranslationException
from ripozo.viewsets.fields.common import StringField, BooleanField, FloatField,\
    DateTimeField, IntegerField, ListField
from ripozo.tests.bases.field import FieldTestBase

import datetime
import re
import six
import unittest


# TODO test validating, translating, etc on multiple fields.
# TODO test field values that evaluate to None

class FieldTestBase2(FieldTestBase):
    validation_exception = ValidationException
    translation_exception = TranslationException





class StringFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = StringField
    instance_type = six.text_type
    translation_success = ['', 'another', 1, True]
    translation_failures = []  # everything should be convertable to a string

    def test_size(self):
        self.size_test_helper('a', '123456', 'woooooooooooooooo')

    def test_validate_regex(self):
        f = StringField('field', regex=re.compile(r'^something$'))
        self.assertRaises(ValidationException, f._validate, 'notsomething')
        original = 'something'
        new = f._validate(original)
        self.assertEqual(original, new)


class IntegerFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = IntegerField
    instance_type = int
    translation_success = [1, '123', 1.5]
    translation_failures = ['abc', '']  # everything should be convertable to a string

    def test_size(self):
        self.size_test_helper(1, 7, 12)


class FloatFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = FloatField
    instance_type = float
    translation_success = [1, '1', 1.5]
    translation_failures = ['abc', '']  # everything should be convertable to a string

    def test_size(self):
        self.size_test_helper(1.0, 7.0, 12.0)


class BoolFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = BooleanField
    instance_type = bool
    translation_success = [True, False, 'True', 'False', 'true', 'false', 'TRUE', 'FALSE']
    translation_failures = ['somethingelse', 0]  # everything should be convertable to a string


class DatetimeFieldTest(FieldTestBase2, unittest.TestCase):
    field_type = DateTimeField
    instance_type = datetime.datetime
    translation_success = [datetime.datetime.now(), '2015-02-10T18:15:15.123456Z']
    translation_failures = ['something', '2/15/2012']  # everything should be convertable to a string

    def test_size(self):
        minimum = datetime.datetime.now()
        maximum = minimum + datetime.timedelta(days=5)
        too_small = minimum - datetime.timedelta(days=5)
        too_large = maximum + datetime.timedelta(days=5)
        just_right = minimum + datetime.timedelta(days=2)
        self.size_test_helper(too_small, just_right, too_large, minimum=minimum, maximum=maximum)

    def test_valid_formats(self):
        d = '12/15/2015'
        valid_formats = ['%Y-%m-%dT%H:%M:%S.%fZ', '%m/%d/%Y']
        f = DateTimeField('field', valid_formats=valid_formats)
        inst = f._translate(d)
        self.assertIsInstance(inst, datetime.datetime)
        d = '2015-02-10T18:15:15.123456Z'
        inst = f._translate(d)
        self.assertIsInstance(inst, datetime.datetime)

        self.assertRaises(TranslationException, f._translate, '15/12/2015')


class TestListField(FieldTestBase2, unittest.TestCase):
    field_type = ListField
    instance_type = list
    translation_success = [(1, 2,), [1, 2]]
    translation_failures = [12]

    def test_not_required(self):
        """
        Tests that a validation error
        is raised only when appropriate.
        """
        l = ListField('field', required=False)
        obj = l.translate(None, validate=True)
        self.assertListEqual(obj, [])

    def test_required(self):
        """
        Tests that the validation error
        is raised when required is True
        """
        l = ListField('field', required=True)
        self.assertRaises(ValidationException, l.translate, None, validate=True)

    def test_translate_items(self):
        """
        Tests validating the items.
        """
        items = [datetime.datetime.now(), 'gonna break']
        l = ListField('field', indv_field=DateTimeField('datetime'))
        self.assertRaises(TranslationException, l.translate, items)
        items = [datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')]
        resp_items = l.translate(items)
        self.assertEqual(len(resp_items), 1)
        self.assertIsInstance(resp_items[0], datetime.datetime)

    def test_validate_items(self):
        """
        Tests validating the items in the list
        """
        items = [10, 15]
        l = ListField('field', indv_field=IntegerField('int', minimum=5))
        resp_items = l.translate(items, validate=True)
        self.assertEqual(items, resp_items)
        items = [15, 0]
        self.assertRaises(ValidationException, l.translate, items, validate=True)
