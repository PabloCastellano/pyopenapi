from __future__ import absolute_import
from pyopenapi import SwaggerApp
from pyopenapi.primitives import Renderer
from .utils import get_test_data_folder
from os import path
from validate_email import validate_email
import unittest
import six
import uuid
import string
import datetime


class StringTestCase(unittest.TestCase):
    """ render 'string' types """
    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'string')
        ))
        kls.rnd = Renderer()

    def test_string(self):
        opt = self.rnd.default()
        for _ in xrange(50):
            s = self.rnd.render(
                self.app.resolve('#/definitions/string.1'),
                opt=opt
            )
            self.assertTrue(isinstance(s, six.string_types), 'should be string, not {0}'.format(s))
            self.assertTrue(len(s) <= opt['max_str_length'])

    def test_password(self):
        opt = self.rnd.default()
        for _ in xrange(50):
            s = self.rnd.render(
                self.app.resolve('#/definitions/password.1'),
                opt=opt
            )
            self.assertTrue(isinstance(s, six.string_types), 'should be string, not {0}'.format(s))
            self.assertTrue(len(s) <= opt['max_str_length'])

    def test_uuid(self):
        u = self.rnd.render(
            self.app.resolve('#/definitions/uuid.1'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(u, uuid.UUID), 'should be UUID, not {0}'.format(u))

    def test_byte(self):
        b64s = list(string.digits) + list(string.letters) + ['/', '+']
        bt = self.rnd.render(
            self.app.resolve('#/definitions/byte.1'),
            opt=self.rnd.default()
        )
        # verify it's base64
        self.assertTrue(len(bt) % 4 == 0, 'not a base64 string, {0}'.format(bt))
        idx = bt.find('=')
        for v in bt[:idx if idx != -1 else len(bt)]:
            self.assertTrue(v in b64s, 'should be an allowed char, not {0}'.format(v))

    def test_date(self):
        d = self.rnd.render(
            self.app.resolve('#/definitions/date.1'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(d, datetime.date), 'should be a datetime.date, not {0}'.format(d))

    def test_datetime(self):
        d = self.rnd.render(
            self.app.resolve('#/definitions/datetime.1'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(d, datetime.datetime), 'should be a datetime.date, not {0}'.format(d))

    def test_email(self):
        for _ in xrange(50):
            e = self.rnd.render(
                self.app.resolve('#/definitions/email.1'),
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, six.string_types), 'should be string, not {0}'.format(e))
            self.assertTrue(validate_email(e), 'should be a email, not {0}'.format(e))

       
class OtherTestCase(unittest.TestCase):
    """ render 'integer/float/bool' types """
    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'other')
        ))
        kls.rnd = Renderer()

    def test_integer(self):
        for _ in xrange(50):
            i = self.rnd.render(
                self.app.resolve('#/definitions/integer.1'),
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(i, six.integer_types), 'should be integer, not {0}'.format(i))
            self.assertTrue(i <= 50, 'should be less than 50, not {0}'.format(i))
            self.assertTrue(i >= 10, 'should be greater than 10, not {0}'.format(i))
            self.assertTrue((i % 5) == 0, 'should be moduleable by 5, not {0}'.format(i))

    def test_float(self):
        for _ in xrange(50):
            f = self.rnd.render(
                self.app.resolve('#/definitions/float.1'),
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(f, float), 'should be float, not {0}'.format(f))
            self.assertTrue(f <= 100, 'should be less than 100, not {0}'.format(f))
            self.assertTrue(f >= 50, 'should be greater than 50, not {0}'.format(f))
            self.assertTrue((f % 5) == 0, 'should be moduleable by 5, not {0}'.format(f))


    def test_bool(self):
        b = self.rnd.render(
            self.app.resolve('#/definitions/bool.1'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(b, bool), 'should be bool, not {0}'.format(b))

    def test_enum_string(self):
        obj = self.app.resolve('#/definitions/enum.string')
        for _ in xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, six.string_types), 'should be a string, not {0}'.format(e))
            self.assertTrue(e in obj.enum, 'should be one of {0}, not {1}'.format(obj.enum, e))
 
    def test_enum_integer(self):
        obj = self.app.resolve('#/definitions/enum.integer')
        for _ in xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, six.integer_types), 'should be a integer, not {0}'.format(e))
            self.assertTrue(e in obj.enum, 'should be one of {0}, not {1}'.format(obj.enum, e))
 
    def test_enum_boolean(self):
        obj = self.app.resolve('#/definitions/enum.boolean')
        for _ in xrange(50):
            e = self.rnd.render(
                obj,
                opt=self.rnd.default()
            )
            self.assertTrue(isinstance(e, bool), 'should be a boolean, not {0}'.format(e))
            self.assertTrue(e in obj.enum, 'should be one of {0}, not {1}'.format(obj.enum, e))

    def test_enum_uuid(self):
        pass
        # TODO: add test case when pyopenapi support uuid

class ArrayTestCase(unittest.TestCase):
    """ render 'array' types """
    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'array')
        ))
        kls.rnd = Renderer()

    def test_array_of_email(self):
        """ basic case with email """
        a = self.rnd.render(
            self.app.resolve('#/definitions/array.email'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(a, list), 'should be a list, not {0}'.format(a))
        self.assertTrue(len(a) <= 50, 'should be less than 50, not {0}'.format(len(a)))
        for v in a:
            self.assertTrue(validate_email(v), 'should be an email, not {0}'.format(v))

    def test_array_allOf(self):
        """ lots of allOf """
        a = self.rnd.render(
            self.app.resolve('#/definitions/array.allOf'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(a, list), 'should be a list, not {0}'.format(a))
        self.assertTrue(len(a) <= 50 and len(a) >= 10, 'should be less than 50 and more than 10, not {0}'.format(len(a)))
        for v in a:
            self.assertTrue(isinstance(v, six.integer_types), 'should be integer, not {0}'.format(v))
            self.assertTrue(v >= 22 and v <= 33, 'should be more than 22 and less than 33, not {0}'.format(v))

    def test_array_with_object(self):
        """ array with object """
        a = self.rnd.render(
            self.app.resolve('#/definitions/array.object'),
            opt=self.rnd.default()
        )
        self.assertTrue(isinstance(a, list), 'should be a list, not {0}'.format(a))
        self.assertTrue(len(a) >=10 and len(a) <=40, 'length should be more than 10 and less than 40')
        for v in a:
            self.assertTrue(isinstance(v, dict), 'should be a dict, not {0}'.format(v))
            if 'id' in v:
                self.assertTrue(v['id'] >=50 and v['id'] <=100, 'should be between (50, 100), not {0}'.format(v['id']))
            if 'name' in v:
                self.assertTrue(isinstance(v['name'], six.string_types), 'should be string, not {0}'.format(v['name']))


class ObjectTestCase(unittest.TestCase):
    """ render 'object' (Model) types """
    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'object')
        ))
        kls.rnd = Renderer()

    def test_required(self):
        """ make sure required works """
        opt = self.rnd.default()
        opt['minimal'] = True
        for _ in xrange(50):
            o = self.rnd.render(
                self.app.resolve('#/definitions/user'),
                opt=opt
            )
            self.assertTrue(isinstance(o, dict), 'should be a dict, not {0}'.format(o))
            self.assertTrue('id' in o, 'id is in required list')
            self.assertTrue('name' in o, 'name is in required list')
            self.assertTrue('email' not in o, 'email is not in required list, and it\'s minimal')

        opt['minimal'] = False
        yes = no = 0
        for _ in xrange(50):
            o = self.rnd.render(
                self.app.resolve('#/definitions/user'),
                opt=opt
            )
            self.assertTrue(isinstance(o, dict), 'should be a dict, not {0}'.format(o))
            self.assertTrue('id' in o, 'id is in required list')
            self.assertTrue('name' in o, 'name is in required list')
            if 'email' in o:
                yes = yes + 1
            else:
                no = no + 1
        self.assertTrue(yes > 0 and no > 0, 'email should exist sometimes, Y{0}-N{1}'.format(yes, no))

    def test_additionalProperties(self):
        """ test additionalProperties """
        opt = self.rnd.default()
        opt['minimal'] = True
        for _ in xrange(50):
            o = self.rnd.render(
                self.app.resolve('#/definitions/object.addp'),
                opt=opt
            )
            self.assertTrue(isinstance(o, dict), 'should be a dict, not {0}'.format(o))
            self.assertTrue(len(o) >= 20 and len(o) <= 50, 'should be between (20, 50), not {0}'.format(len(o)))
            for k, v in six.iteritems(o):
                self.assertTrue(isinstance(v, dict), 'should be a dict, not {0}'.format(v))
                self.assertTrue('id' in v, 'id is in required list')
                self.assertTrue('name' in v, 'name is in required list')
                self.assertTrue('email' not in v, 'email is not in required list, and it\'s minimal')

class ParameterTestCase(unittest.TestCase):
    """ render all parameters """
    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp.create(get_test_data_folder(
            version='2.0',
            which=path.join('render', 'params')
        ))

