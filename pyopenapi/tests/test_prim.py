from pyopenapi import SwaggerApp, primitives
from .utils import get_test_data_folder
from pyopenapi.spec.v2_0 import objects
from pyopenapi.utils import jp_compose
import unittest


class SchemaTestCase(unittest.TestCase):
    """ test for Schema object """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which='schema'))

    def test_model_tag(self):
        """ test basic model """
        t = self.app.resolve('#/definitions/Tag')
        self.assertTrue(isinstance(t, objects.Schema))

        v = t._prim_(dict(id=1, name='Hairy'))
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.id, 1)
        self.assertEqual(v.name, 'Hairy')

    def test_model_pet(self):
        """ test complex model, including
        model inheritance
        """
        p = self.app.resolve('#/definitions/Pet')
        self.assertTrue(isinstance(p, objects.Schema))

        v = p._prim_(dict(
            name='Buf',
            photoUrls=['http://flickr.com', 'http://www.google.com'],
            id=10,
            category=dict(
                id=1,
                name='dog'
            ),
            tags=[
                dict(id=1, name='Hairy'),
                dict(id=2, name='south'),
            ]
        ))
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.name, 'Buf')
        self.assertEqual(v.photoUrls[0], 'http://flickr.com')
        self.assertEqual(v.photoUrls[1], 'http://www.google.com')
        self.assertEqual(v.id, 10)
        self.assertTrue(isinstance(v.tags[0], primitives.Model))
        self.assertTrue(v.tags[0].id, 1)
        self.assertTrue(v.tags[0].name, 'Hairy')
        self.assertTrue(isinstance(v.category, primitives.Model))
        self.assertTrue(v.category.id, 1)
        self.assertTrue(v.category.name, 'dog')

    def test_model_employee(self):
        """ test model with allOf only
        """
        e = self.app.resolve("#/definitions/Employee")
        self.assertTrue(isinstance(e, objects.Schema))

        v = e._prim_(dict(
            id=1,
            skill_id=2,
            location="home",
            skill_name="coding"
        ))
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.id, 1)
        self.assertEqual(v.skill_id, 2)
        self.assertEqual(v.location, "home")
        self.assertEqual(v.skill_name, "coding")

    def test_model_boss(self):
        """ test model with allOf and properties
        """
        b = self.app.resolve("#/definitions/Boss")
        self.assertTrue(isinstance(b, objects.Schema))

        v = b._prim_(dict(
            id=1,
            location="office",
            boss_name="not you"
        ))
        self.assertTrue(isinstance(v, primitives.Model))
        self.assertEqual(v.id, 1)
        self.assertEqual(v.location, "office")
        self.assertEqual(v.boss_name, "not you")

    def test_int(self):
        """ test integer,
        schema is separated into parts
        """
        i = self.app.resolve("#/definitions/int")

        self.assertRaises(ValueError, i._prim_, 200)
        self.assertRaises(ValueError, i._prim_, 99)

    def test_num_multiple_of(self):
        """ test multipleOf """
        i = self.app.resolve("#/definitions/num_multipleOf")

        self.assertRaises(ValueError, i._prim_, 4)
        i._prim_(5)


class HeaderTestCase(unittest.TestCase):
    """ test for Header object """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='2.0', which='schema'))

    def test_simple_array(self):
        """ header in array """
        p1 = self.app.resolve(jp_compose(['#', 'paths', '/t', 'get', 'parameters', '0']))
        self.assertTrue(isinstance(p1, objects.Parameter))

        v = p1._prim_([1, 2, 3, 4, 5])
        self.assertTrue(isinstance(v, primitives.Array))
        self.assertEqual(str(v), '1,2,3,4,5')

    def test_integer_limit(self):
        """ header in integer """
        p2 = self.app.resolve(jp_compose(['#', 'paths', '/t', 'get', 'parameters', '1']))
        self.assertTrue(isinstance(p2, objects.Parameter))

        self.assertRaises(ValueError, p2._prim_, 101)
        self.assertRaises(ValueError, p2._prim_, -1)

    def test_multi_level_array(self):
        """ header in array of array """
        p3 = self.app.resolve(jp_compose(['#', 'paths', '/t', 'get', 'parameters', '2']))
        self.assertTrue(isinstance(p3, objects.Parameter))

        self.assertEqual(str(p3._prim_(
            [
                [
                    [1,2],
                    [3,4],
                    [5,6]
                ],
                [
                    [7,8],
                    [9,10]
                ],
                [
                    [11,12],
                    [13,14]
                ]
            ]
        )), '1|2,3|4,5|6 7|8,9|10 11|12,13|14')
