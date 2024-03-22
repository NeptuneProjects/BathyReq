#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import unittest
from urllib.parse import urlencode

from bathyreq.sources import ncei


class TestNCEIBase(unittest.TestCase):
    def test_build_base_url(self):
        base = ncei.NCEIBase()
        base.build_base_url()

        expected_url = "https://gis.ngdc.noaa.gov/arcgis/rest/services/DEM_mosaics/DEM_global_mosaic/ImageServer/exportImage"
        self.assertEqual(base.url, expected_url)


class TestNCEIRequest(unittest.TestCase):
    def test_build_request(self):
        request = ncei.NCEIRequest(
            bbox=[-117.43000, 32.55000, -117.43000, 32.55000],
            size=[400, 400],
            format="png",
            pixelType="U8",
        )
        request.build_request()

        expected_params = {
            "bbox": "-117.43000,32.55000,-117.43000,32.55000",
            "size": "400,400",
            "format": "png",
            "pixelType": "U8",
            "nodata": 0.0,
            "interpolation": "RSP_NearestNeighbor",
            "compression": "LZ77",
            "f": "image",
        }
        expected_request = urlencode(expected_params)

        self.assertEqual(request.request, expected_request)

    def test_format_attributes(self):
        request = ncei.NCEIRequest(
            bbox=[-117.43000, 32.55000, -117.43000, 32.55000],
            size=[400, 400],
            format="png",
            pixelType="U8",
        )
        request.format_attributes()

        expected_bbox = "-117.43000,32.55000,-117.43000,32.55000"
        expected_size = "400,400"

        self.assertEqual(request.bbox, expected_bbox)
        self.assertEqual(request.size, expected_size)


class TestNCEISource(unittest.TestCase):
    def test_build_url(self):
        base = ncei.NCEIBase()
        request = ncei.NCEIRequest(
            bbox=[-117.43000, 32.55000, -117.43000, 32.55000],
            size=[400, 400],
            format="png",
            pixelType="U8",
        )

        source = ncei.NCEISource(base=base, request=request)
        source.build_url()

        expected_base_url = "https://gis.ngdc.noaa.gov/arcgis/rest/services/DEM_mosaics/DEM_global_mosaic/ImageServer/exportImage"
        expected_request_params = {
            "bbox": "-117.43000,32.55000,-117.43000,32.55000",
            "size": "400,400",
            "format": "png",
            "pixelType": "U8",
            "nodata": 0.0,
            "interpolation": "RSP_NearestNeighbor",
            "compression": "LZ77",
            "f": "image",
        }
        expected_request = urlencode(expected_request_params)

        expected_url = f"{expected_base_url}?{expected_request}"

        self.assertEqual(source.url, expected_url)


if __name__ == "__main__":
    unittest.main()
