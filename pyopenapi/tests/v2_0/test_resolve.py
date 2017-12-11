from pyopenapi import App, utils
from pyopenapi.spec.v3_0_0 import objects
from pyopenapi.spec.v2_0.objects import Swagger, License, Schema
from ..utils import get_test_data_folder, gen_test_folder_hook
from ...utils import final, deref
import unittest
import os
import weakref



class ResolvePathItemTestCase(unittest.TestCase):
    """ test for PathItem $ref """

    @classmethod
    def setUpClass(kls):
        kls.app = App._create_(get_test_data_folder(
            version='2.0',
            which=os.path.join('resolve', 'path_item')
        ))

    def test_path_item(self):
        """ make sure PathItem is correctly merged """
        a = self.app.resolve(utils.jp_compose('/a', '#/paths'))

        self.assertTrue(isinstance(a, objects.PathItem))
        self.assertTrue(a.get.operationId, 'a.get')
        self.assertTrue(a.put.description, 'c.put')
        self.assertTrue(a.post.description, 'd.post')

        b = self.app.resolve(utils.jp_compose('/b', '#/paths'))
        self.assertTrue(b.get.operationId, 'b.get')
        self.assertTrue(b.put.description, 'c.put')
        self.assertTrue(b.post.description, 'd.post')

        c = self.app.resolve(utils.jp_compose('/c', '#/paths'))
        self.assertTrue(b.put.description, 'c.put')
        self.assertTrue(b.post.description, 'd.post')


class ResolveTestCase(unittest.TestCase):
    """ test for $ref other than PathItem """

    @classmethod
    def setUpClass(kls):
        kls.app = App._create_(get_test_data_folder(
            version='2.0',
            which=os.path.join('resolve', 'other')
        ))

    def test_schema(self):
        """ make sure $ref to Schema works """
        p = final(self.app.s('/a').get)

        self.assertEqual(
            id(p.request_body.content['application/json'].schema.ref_obj),
            id(self.app.resolve('#/components/schemas/d1'))
        )

    def test_parameter(self):
        """ make sure $ref to Parameter works """
        p = final(self.app.s('/a').get)

        self.assertEqual(len(p.parameters), 4)
        self.assertEqual(deref(p.parameters[0]).name, 'p1_d')
        self.assertEqual(deref(p.parameters[1]).name, 'p2_d')
        self.assertEqual(deref(p.parameters[2]).name, 'p3_d')
        self.assertEqual(deref(p.parameters[3]).name, 'p4_d')

        body = deref(p.request_body)
        self.assertEqual(deref(body.content['application/json'].schema).type_, 'string')

    def test_response(self):
        """ make sure $ref to Response works """
        p = final(self.app.s('/a').get)

        self.assertEqual(deref(p.responses['default']).description, 'void, r1')

    def test_raises(self):
        """ make sure to raise for invalid input """
        self.assertRaises(ValueError, self.app.resolve, None)
        self.assertRaises(ValueError, self.app.resolve, '')


class DerefTestCase(unittest.TestCase):
    """ test for pyopenapi.utils.deref """

    @classmethod
    def setUpClass(kls):
        kls.app = App._create_(get_test_data_folder(
            version='2.0',
            which=os.path.join('resolve', 'deref')
        ))

    def test_deref(self):
        od = utils.deref(self.app.resolve('#/components/schemas/s1'))

        self.assertEqual(id(od), id(self.app.resolve('#/components/schemas/s4')))

    def test_external_ref_loading_order(self):
        """ make sure pyopenapi.spec_obj_cache would remove
        dummy objects when resolving.

        dummy objects: an spec object co-exist with its parent in
        pyopenapi.spec_obj_cache
        """

        # prepare a dummy app
        app = App.load(
            url='file:///ex/root/swagger.json',
            url_load_hook=gen_test_folder_hook(get_test_data_folder(version='2.0'))
        )

        # fill its cache with several dummy objects
        license = app.resolve('file:///wordnik/swagger.json#/info/license',
            parser=License,
            spec_version='2.0',
            before_return=None,
            remove_dummy=True,
        )
        order = app.resolve('file:///wordnik/swagger.json#/definitions/Order',
            parser=Schema,
            spec_version='2.0',
            before_return=None,
            remove_dummy=True,
        )
        pet = app.resolve('file:///wordnik/swagger.json#/definitions/Pet',
            parser=Schema,
            spec_version='2.0',
            before_return=None,
            remove_dummy=True,
        )

        # resolve their root object with latest version
        swg = app.resolve('file:///wordnik/swagger.json',
            parser=Schema,
            spec_version='2.0',
            before_return=None,
            remove_dummy=True,
        )

        # make sure root objec use those dummy objects during loading
        self.assertEqual(weakref.proxy(swg.resolve(['info','license'])), license)
        self.assertEqual(weakref.proxy(swg.resolve(['definitions','Order'])), order)
        self.assertEqual(weakref.proxy(swg.resolve(['definitions','Pet'])), pet)

        # make sure this relation is maintained after migrating up
        license = app.resolve('file:///wordnik/swagger.json#/info/license',
            parser=License,
            before_return=None,
            remove_dummy=True,
        )

        # #/definitios/Order is changed to #/components/schemas/Order
        # this case is not taken care here.

        # resolve their root object with latest version
        oai = app.resolve('file:///wordnik/swagger.json',
            before_return=None,
            remove_dummy=True,
        )

        # make sure root objec use those dummy objects during loading
        self.assertEqual(weakref.proxy(oai.resolve(['info','license'])), license)

