from __future__ import absolute_import
from ...scan import Dispatcher
from ...utils import normalize_jr
from ...spec.v2_0.objects import (
    Schema,
    Parameter,
    Response,
    PathItem,
    )


class NormalizeRef(object):
    """ normalized all $ref """

    class Disp(Dispatcher): pass

    def __init__(self, base_url):
        self.base_url = base_url

    @Disp.register([Schema, Parameter, Response, PathItem])
    def _resolve(self, path, obj, _):
        ref = getattr(obj, '$ref', None)
        if ref:
            obj.update_field('original_ref', ref)

        obj.update_field('$ref', normalize_jr(getattr(obj, '$ref'), self.base_url))
