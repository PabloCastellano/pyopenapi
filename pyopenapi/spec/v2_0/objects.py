from __future__ import absolute_import
from ...base import BaseObj, FieldMeta
from ...utils import deref
from pyopenapi import primitives, io
import six
import copy


class BaseSchema(BaseObj):
    """ Base type for Items, Schema, Parameter, Header
    """

    __swagger_fields__ = [
        ('type', None),
        ('format', None),
        ('items', None),
        ('default', None),
        ('maximum', None),
        ('exclusiveMaximum', None),
        ('minimum', None),
        ('exclusiveMinimum', None),
        ('maxLength', None),
        ('minLength', None),
        ('maxItems', None),
        ('minItems', None),
        ('multipleOf', None),
        ('enum', None),
        ('pattern', None),
        ('uniqueItems', None),
    ]

    def __init__(self, ctx):
        # __swagger_fields__ would be overriden by child class.
        # TODO: duplicated code in BaseObj.__init__
        for name, default in BaseSchema.__swagger_fields__:
            setattr(self, self.get_private_name(name), ctx._obj.get(name, copy.copy(default)))

        super(BaseSchema, self).__init__(ctx)

class Items(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Items Object
    """

    __swagger_fields__ = [
        ('collectionFormat', None),
    ]

    def _prim_(self, v):
        return primitives.prim_factory(self, v)


class Schema(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Schema Object
    """

    __swagger_fields__ = [
        ('$ref', None),
        ('maxProperties', None),
        ('minProperties', None),
        ('required', None),

        ('allOf', []),
        ('properties', None),

        ('discriminator', None),
        ('readOnly', None),

        # pyopenapi only
        ('ref_obj', None),
        ('name', None),
    ]

    def _prim_(self, v):
        return primitives.prim_factory(self, v)


class Swagger(six.with_metaclass(FieldMeta, BaseObj)):
    """ Swagger Object
    """

    __swagger_fields__ = [
        ('swagger', None),
        ('info', None),
        ('host', None),
        ('basePath', None),
        ('schemes', None),
        ('consumes', []),
        ('produces', []),
        ('paths', None),
        ('definitions', None),
        ('parameters', None),
        ('responses', None),
        ('securityDefinitions', None),
        ('security', None),
        ('tags', None),
    ]


class Info(six.with_metaclass(FieldMeta, BaseObj)):
    """ Info Object
    """

    __swagger_fields__ = [
        ('version', None),
    ]


class Parameter(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Parameter Object
    """

    __swagger_fields__ = [
        # Reference Object
        ('$ref', None),

        ('name', None),
        ('in', None),
        ('required', None),

        # body parameter
        ('schema', None),

        # other parameter
        ('collectionFormat', None),

        # pyopenapi only
        ('ref_obj', None),
    ]

    def _prim_(self, v):
        i = getattr(self, 'in')
        return primitives.prim_factory(self.schema, v) if i == 'body' else primitives.prim_factory(self, v)


class Header(six.with_metaclass(FieldMeta, BaseSchema)):
    """ Header Object
    """

    __swagger_fields__ = [
        ('collectionFormat', None),
    ]


class Response(six.with_metaclass(FieldMeta, BaseObj)):
    """ Response Object
    """

    __swagger_fields__ = [
        # Reference Object
        ('$ref', None),

        ('schema', None),
        ('headers', None),

        # pyopenapi only
        ('ref_obj', None),
    ]


class Operation(six.with_metaclass(FieldMeta, BaseObj)):
    """ Operation Object
    """

    __swagger_fields__ = [
        ('tags', None),
        ('operationId', None),
        ('consumes', []),
        ('produces', []),
        ('parameters', None),
        ('responses', None),
        ('deprecated', None),
        ('security', None),

        # for pyopenapi
        ('method', None),
        ('url', None),
    ]

    def __call__(self, **k):
        # prepare parameter set
        params = dict(header={}, query=[], path={}, body={}, formData=[], file={})
        def _convert_parameter(p):
            v = k.get(p.name, p.default)
            if v == None and p.required:
                raise ValueError('requires parameter: ' + p.name)

            c = p._prim_(v)
            i = getattr(p, 'in')
            if i in ('query', 'formData'):
                if isinstance(c, primitives.Array):
                    params[i].extend([tuple(p.name, v) for v in c.to_url()])
                else:
                    params[i].append((p.name, str(c),))
            else:
                if i != 'body' and p.type != 'file':
                    c = str(c)

                params[i if p.type != 'file' else 'file'][p.name] = c

        # TODO: check for unknown parameter
        for p in self.parameters:
            _convert_parameter(deref(p))

        return \
        io.SwaggerRequest(op=self, params=params), io.SwaggerResponse(self)


class PathItem(six.with_metaclass(FieldMeta, BaseObj)):
    """ Path Item Object
    """

    __swagger_fields__ = [
        # Reference Object
        ('$ref', None),

        ('get', None),
        ('put', None),
        ('post', None),
        ('delete', None),
        ('options', None),
        ('head', None),
        ('patch', None),
        ('parameters', []),

        # pyopenapi only
        ('ref_obj', None),
    ]


class SecurityScheme(six.with_metaclass(FieldMeta, BaseObj)):
    """ Security Scheme Object
    """

    __swagger_fields__ = [
        ('type', None),
        ('name', None),
        ('in', None),
        ('flow', None),
        ('authorizationUrl', None),
        ('tokenUrl', None),
        ('scopes', None),
    ]


class Tag(six.with_metaclass(FieldMeta, BaseObj)):
    """ Tag Object
    """

    __swagger_fields__ = [
        ('name', None),
    ]

