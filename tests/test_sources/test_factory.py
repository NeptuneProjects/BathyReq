#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from bathyreq.sources.factory import factory, DataSourceNotImplemented


class TestFactory(unittest.TestCase):

    def test_ncei_source(self):
        bbox = [-117, 32, -116, 33]
        source = "ncei"
        inst = factory(bbox=bbox, source=source)
        self.assertIsNotNone(inst)
        self.assertTrue(hasattr(inst, "build_url"))
        self.assertTrue(callable(inst.build_url))

    def test_gebco_source(self):
        bbox = [-117, 32, -116, 33]
        source = "gebco"
        inst = factory(bbox=bbox, source=source, size=[500, 500], format="image/jpeg")
        self.assertIsNotNone(inst)
        self.assertTrue(hasattr(inst, "build_url"))
        self.assertTrue(callable(inst.build_url))

    def test_blue_topo_not_implemented(self):
        bbox = [-117, 32, -116, 33]
        source = "blue_topo"
        with self.assertRaises(DataSourceNotImplemented):
            factory(bbox=bbox, source=source)


if __name__ == "__main__":
    unittest.main()
