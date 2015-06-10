from pyopenapi import SwaggerApp, errs
from ..utils import get_test_data_folder
import unittest
import os
import six


folder = get_test_data_folder(
    version='1.2',
    which='wordnik'
)

def _pf(s):
    return six.moves.urllib.parse.urlunparse((
        'file',
        '',
        folder,
        '',
        '',
        s))


class Swagger_Upgrade_TestCase(unittest.TestCase):
    """ test for upgrade from converting 1.2 to 2.0 """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(folder)

    def test_resource_list(self):
        """ ResourceList -> Swagger
        """
        s = self.app.root

        self.assertEqual(s.swagger, '2.0')
        self.assertEqual(s.host, 'petstore.swagger.wordnik.com')
        self.assertEqual(s.basePath, '')
        self.assertEqual(s.info.version, '1.0.0')
        self.assertEqual(s.schemes, ['http', 'https'])
        self.assertEqual(s.consumes, [])
        self.assertEqual(s.produces, [])

    def test_resource(self):
        """  Resource -> Tag, Operation
        make sure the way we rearrange resources
        to tags is correct.
        """
        s = self.app.root
        self.assertEqual(sorted([t.name for t in s.tags]), sorted(['store', 'user', 'pet']))

        p = self.app.root.paths
        self.assertEqual(sorted(p.keys()), sorted([
            '/api/user/createWithArray',
            '/api/store/order',
            '/api/user/login',
            '/api/user',
            '/api/pet',
            '/api/pet/findByTags',
            '/api/pet/findByStatus',
            '/api/store/order/{orderId}',
            '/api/user/logout',
            '/api/pet/uploadImage',
            '/api/user/createWithList',
            '/api/user/{username}',
            '/api/pet/{petId}'
        ]))

    def test_operation(self):
        """ Operation -> Operation
        """
        p = self.app.root.paths['/api/pet/{petId}']

        # getPetById
        o = p.get
        self.assertEqual(o.tags, ['pet'])
        self.assertEqual(o.operationId, 'getPetById')
        self.assertEqual(o.produces, ['application/json', 'application/xml', 'text/plain', 'text/html'])
        self.assertEqual(o.consumes, [])
        self.assertEqual(o.deprecated, False)

        # partialUpdate
        o = p.patch
        self.assertEqual(o.produces, ['application/json', 'application/xml'])
        self.assertEqual(o.consumes, ['application/json', 'application/xml'])
        self.assertEqual(o.security, [{'oauth2': ['write:pets']}])
        self.assertTrue('default' in o.responses)

        r = o.responses['default']
        self.assertEqual(r.headers, {})
        self.assertEqual(r.schema.type, 'array')
        self.assertEqual(getattr(r.schema.items, 'norm_ref'), _pf('/definitions/pet!##!Pet'))

        # createUser
        o = self.app.root.paths['/api/user'].post
        self.assertEqual(o.tags, ['user'])
        self.assertEqual(o.operationId, 'createUser')

    def test_authorization(self):
        """ Authorization -> Security Scheme
        """
        s = self.app.root.securityDefinitions
        self.assertEqual(list(s.keys()), ['oauth2'])

        ss = s['oauth2']
        self.assertEqual(ss.type, 'oauth2')
        self.assertEqual(ss.name, None)
        self.assertEqual(getattr(ss, 'in'), None)
        self.assertEqual(ss.flow, 'accessCode')
        self.assertEqual(ss.authorizationUrl, 'http://petstore.swagger.wordnik.com/api/oauth/dialog')
        self.assertEqual(ss.tokenUrl, 'http://petstore.swagger.wordnik.com/api/oauth/token')
        self.assertEqual(ss.scopes, {'write:pets': '', 'read:pets': ''})

    def test_parameter(self):
        """ Parameter -> Parameter
        """
        # body
        o = self.app.root.paths['/api/pet/{petId}'].patch
        p = [p for p in o.parameters if getattr(p, 'in') == 'body'][0]
        self.assertEqual(getattr(p, 'in'), 'body')
        self.assertEqual(p.required, True)
        self.assertEqual(getattr(p.schema, 'norm_ref'), _pf('/definitions/pet!##!Pet'))

        # form
        o = self.app.root.paths['/api/pet/uploadImage'].post
        p = [p for p in o.parameters if getattr(p, 'in') == 'formData' and p.type == 'string'][0]
        self.assertEqual(p.name, 'additionalMetadata')
        self.assertEqual(p.required, False)
 
        # file
        o = self.app.root.paths['/api/pet/uploadImage'].post
        p = [p for p in o.parameters if getattr(p, 'in') == 'formData' and p.type == 'file'][0]
        self.assertEqual(p.name, 'file')
        self.assertEqual(p.required, False)

        # non-body can't have $ref
        try:
            SwaggerApp._create_(get_test_data_folder(
                version='1.2',
                which='upgrade_parameter'
            ))
        except errs.SchemaError as e:
            self.failUnlessEqual(e.args, ("Can't have $ref in non-body Parameters",))
        else:
            self.fail('SchemaError not raised')

    def test_model(self):
        """ Model -> Definition
        """
        d = self.app.root.definitions['pet!##!Pet']
        self.assertEqual(d.required, ['id', 'name'])

        ps = d.properties.keys()
        self.assertEqual(sorted(ps), ['category', 'id', 'name', 'photoUrls', 'status', 'tags'])

        p = d.properties['id']
        self.assertEqual(p.type, 'integer')
        self.assertEqual(p.format, 'int64')
        self.assertEqual(p.minimum, 0)
        self.assertEqual(p.maximum, 100)

        p = d.properties['category']
        self.assertEqual(getattr(p, 'norm_ref'), _pf('/definitions/pet!##!Category'))

        p = d.properties['photoUrls']
        self.assertEqual(p.type, 'array')
        self.assertEqual(p.items.type, 'string')

        p = d.properties['tags']
        self.assertEqual(p.type, 'array')
        self.assertEqual(getattr(p.items, 'norm_ref'), _pf('/definitions/pet!##!Tag'))

        p = d.properties['status']
        self.assertEqual(p.type, 'string')
        self.assertEqual(p.enum, ['available', 'pending', 'sold'])

    def test_item(self):
        """ make sure to raise exception for invalid item
        """
        try:
            SwaggerApp._create_(get_test_data_folder(
                version='1.2',
                which=os.path.join('upgrade_items', 'with_ref')
            ))
        except errs.SchemaError as e:
            self.failUnlessEqual(e.args, ('Can\'t have $ref for Items',))
        else:
            self.fail('SchemaError not raised')

        try:
            SwaggerApp._create_(get_test_data_folder(
                version='1.2',
                which=os.path.join('upgrade_items', 'invalid_primitive')
            ))
        except errs.SchemaError as e:
            self.failUnlessEqual(e.args, ('Non primitive type is not allowed for Items',))
        else:
            self.fail('SchemaError not raised')

    def test_authorizations(self):
        """ Authorizations -> [Security Requirement]
        """
        


class ModelSubtypesTestCase(unittest.TestCase):
    """ test for upgrade /data/v1_2/model_subtypes """

    @classmethod
    def setUpClass(kls):
        kls.app = SwaggerApp._create_(get_test_data_folder(version='1.2', which='model_subtypes'))

    def test_path_item(self):
        paths = self.app.resolve('#/paths')
        self.assertEqual(sorted(list(paths.keys())), sorted(['/api/user', '/api/user/{username}']))

