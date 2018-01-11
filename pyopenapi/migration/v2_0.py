from ..utils import jr_split
from ..scan import Scanner
from ..scanner.v1_2 import Upgrade
from ..scanner.v2_0 import Resolve, YamlFixer, NormalizeRef
from ..spec.v2_0.objects import Operation


def up(obj, app, jref):
    ret = obj
    scanner = Scanner(app)

    if ret.__swagger_version__ == '1.2':
        converter = Upgrade(app.sep)

        scanner.scan(root=ret, route=[converter])
        # scan through each resource
        for name in ret.cached_apis:
            scanner.scan(root=ret.cached_apis[name], route=[converter])

        ret = converter.get_swagger()
        if not ret:
            raise Exception('unable to upgrade from 1.2: {}'.format(jref))

    if ret.__swagger_version__ == '2.0':
        url, jp = jr_split(jref)
        app.spec_obj_store.set(ret, url, jp, spec_version='2.0')

        # normalize $ref
        scanner.scan(root=ret, route=[NormalizeRef(url)])
        # fix for yaml that treat response code as number
        scanner.scan(root=ret, route=[YamlFixer()], leaves=[Operation])

        # cache this object before resolving external(possible) object
        app.spec_obj_store.set(ret, url, jp, spec_version='2.0')

        # pre resolve Schema Object
        # note: make sure this object is cached before using 'Resolve' scanner
        scanner.scan(root=ret, route=[Resolve()])
    else:
        raise Exception('unsupported migration: {} to 2.0'.format(ret.__swagger_version__))

    return ret, {}
