from pyopenapi import App, utils, primitives, errs
from ..utils import get_test_data_folder
from ...scanner import CycleDetector
from ...scan import Scanner
import unittest
import os
import six


class CircularRefTestCase(unittest.TestCase):
    """ test for circular reference guard """

    def test_path_item_prepare_with_cycle(self):
        app = App.load(get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'path_item')
        ))

        # should raise nothing
        app.prepare()

    def test_path_item(self):
        folder = get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'path_item')
        )

        def _pf(s):
            return six.moves.urllib.parse.urlunparse((
                'file',
                '',
                folder,
                '',
                '',
                s))

        app = App.create(folder)
        s = Scanner(app)
        c = CycleDetector()
        s.scan(root=app.raw, route=[c])
        self.assertEqual(sorted(c.cycles['path_item']), sorted([[
            _pf('/paths/~1p1'),
            _pf('/paths/~1p2'),
            _pf('/paths/~1p3'),
            _pf('/paths/~1p4'),
            _pf('/paths/~1p1')
        ]]))

    def test_schema(self):
        folder = get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'schema')
        )

        def _pf(s):
            return six.moves.urllib.parse.urlunparse((
                'file',
                '',
                folder,
                '',
                '',
                s))


        app = App.load(folder)
        app.prepare(strict=False)

        s = Scanner(app)
        c = CycleDetector()
        s.scan(root=app.raw, route=[c])
        self.maxDiff = None
        self.assertEqual(sorted(c.cycles['schema']), sorted([
            [_pf('/components/schemas/s10'), _pf('/components/schemas/s11'), _pf('/components/schemas/s9'), _pf('/components/schemas/s10')],
            [_pf('/components/schemas/s5'), _pf('/components/schemas/s5')],
            [_pf('/components/schemas/s1'), _pf('/components/schemas/s2'), _pf('/components/schemas/s3'), _pf('/components/schemas/s4'), _pf('/components/schemas/s1')],
            [_pf('/components/schemas/s12'), _pf('/components/schemas/s13'), _pf('/components/schemas/s12')],
            [_pf('/components/schemas/s6'), _pf('/components/schemas/s7'), _pf('/components/schemas/s6')],
            [_pf('/components/schemas/s14'), _pf('/components/schemas/s15'), _pf('/components/schemas/s14')]
        ]))

    def test_deref(self):
        app = App.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'schema'),
            ),
            strict=False
        )

        s = app.resolve('#/components/schemas/s1')
        self.assertRaises(errs.CycleDetectionError, utils.deref, s)

    def test_primfactory(self):
        app = App.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('circular', 'schema'),
            ),
            strict=False
        )

        s = app.resolve('#/components/schemas/s1')
        self.assertRaises(errs.CycleDetectionError, app.prim_factory.produce, s, {})

