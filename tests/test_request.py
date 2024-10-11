import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import numpy as np
import rasterio
from bathyreq.request import BathyRequest, clear_cache, CACHE_DIR


class TestBathyRequest(unittest.TestCase):
    def setUp(self):
        self.bathy_req = BathyRequest()

    @patch('requests.get')
    def test_download_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        test_url = "http://test.com"
        test_filepath = Path("testfile")
        self.bathy_req.download_data(test_url, test_filepath)

        mock_get.assert_called_once_with(test_url, stream=True)
        mock_response.raise_for_status.assert_called_once()

    def test_form_bbox(self):
        # Test with a bounding box
        longitude = [-117.43000, -117.23000]
        latitude = [32.55000, 32.75000]
        expected_bbox = [-117.43000, 32.55000, -117.23000, 32.75000]
        bbox = self.bathy_req.form_bbox(longitude, latitude)
        [self.assertAlmostEqual(bbox[i], expected_bbox[i]) for i in range(4)]

        # Test with a single point
        longitude = -117.33000
        latitude = 32.65000
        expected_bbox = [-117.33100, 32.64900, -117.32900, 32.65100]
        bbox = self.bathy_req.form_bbox(longitude, latitude, single_point=True)
        [self.assertAlmostEqual(bbox[i], expected_bbox[i]) for i in range(4)]

    def test_generate_filename(self):
        filename = self.bathy_req.generate_filename()
        self.assertIsInstance(filename, str)
        self.assertEqual(len(filename), 20)

    @patch.object(BathyRequest, 'download_data')
    @patch.object(BathyRequest, 'load_data')
    @patch('bathyreq.sources.factory.factory')
    def test_get_area(self, mock_factory, mock_load_data, mock_download_data):
        mock_source = MagicMock()
        mock_source.url = "http://test.com"
        mock_source.request.format = "image/jpeg"
        mock_factory.return_value = mock_source

        mock_load_data.return_value = (np.array([[1, 2], [3, 4]]), rasterio.coords.BoundingBox(1, 2, 3, 4))

        longitude = [-117.43000, -117.23000]
        latitude = [32.55000, 32.75000]
        data, lonvec, latvec = self.bathy_req.get_area(longitude, latitude)

        self.assertEqual(data.tolist(), [[1, 2], [3, 4]])
        self.assertEqual(lonvec.tolist(), [1.0, 3.0])
        self.assertEqual(latvec.tolist(), [2.0, 4.0])

    def test_get_latlon_grids(self):
        bounds = rasterio.coords.BoundingBox(1, 2, 3, 4)
        data = np.array([[1, 2], [3, 4]])
        lonvec, latvec = self.bathy_req.get_latlon_grids(bounds, data)

        self.assertEqual(lonvec.tolist(), [1.0, 3.0])
        self.assertEqual(latvec.tolist(), [2.0, 4.0])

    @patch.object(BathyRequest, 'get_area')
    def test_get_point(self, mock_get_area):
        mock_get_area.return_value = (np.array([[1, 2], [3, 4]]), np.array([1.0, 3.0]), np.array([2.0, 4.0]))

        longitude = -117.43000
        latitude = 32.55000
        data = self.bathy_req.get_point(longitude, latitude)

        self.assertEqual(data.tolist(), [1.0])

    @patch('rasterio.open')
    def test_load_data(self, mock_open):
        mock_dataset = MagicMock()
        mock_dataset.read.return_value = np.array([[1, 2], [3, 4]])
        mock_dataset.bounds = rasterio.coords.BoundingBox(1, 2, 3, 4)
        mock_open.return_value.__enter__.return_value = mock_dataset

        filepath = Path("testfile")
        data, bounds = self.bathy_req.load_data(filepath)

        self.assertEqual(data.tolist(), [[1, 2], [3, 4]])
        self.assertEqual(bounds, rasterio.coords.BoundingBox(1, 2, 3, 4))

class TestClearCache(unittest.TestCase):
    @patch('shutil.rmtree')
    @patch('pathlib.Path.exists')
    def test_clear_cache(self, mock_exists, mock_rmtree):
        mock_exists.return_value = True
        clear_cache(CACHE_DIR)
        mock_rmtree.assert_called_once_with(CACHE_DIR)

if __name__ == "__main__":
    unittest.main()

# class TestBathyRequest(unittest.TestCase):
#     def setUp(self):
#         self.bathy_req = BathyRequest()

#     @patch('requests.get')
#     def test_download_data(self, mock_get):
#         mock_response = MagicMock()
#         mock_response.status_code = 200
#         mock_get.return_value = mock_response

#         test_url = "http://test.com"
#         test_filepath = Path("testfile")
#         self.bathy_req.download_data(test_url, test_filepath)

#         mock_get.assert_called_once_with(test_url, stream=True)
#         mock_response.raise_for_status.assert_called_once()

#     def test_form_bbox(self):
#         longitude = [-117.43000, -117.23000]
#         latitude = [32.55000, 32.75000]
#         expected_bbox = [-117.43000, 32.55000, -117.23000, 32.75000]
#         self.assertEqual(self.bathy_req.form_bbox(longitude, latitude), expected_bbox)

#     def test_generate_filename(self):
#         filename = self.bathy_req.generate_filename()
#         self.assertIsInstance(filename, str)
#         self.assertEqual(len(filename), 20)

#     @patch.object(BathyRequest, 'download_data')
#     @patch.object(BathyRequest, 'load_data')
#     @patch('bathyreq.sources.factory.factory')
#     def test_get_area(self, mock_factory, mock_load_data, mock_download_data):
#         mock_source = MagicMock()
#         mock_source.url = "http://test.com"
#         mock_source.request.format = "image/jpeg"
#         mock_factory.return_value = mock_source

#         mock_load_data.return_value = (np.array([[1, 2], [3, 4]]), rasterio.coords.BoundingBox(1, 2, 3, 4))

#         longitude = [-117.43000, -117.23000]
#         latitude = [32.55000, 32.75000]
#         data, lonvec, latvec = self.bathy_req.get_area(longitude, latitude)

#         self.assertEqual(data.tolist(), [[1, 2], [3, 4]])
#         self.assertEqual(lonvec.tolist(), [1.0, 3.0])
#         self.assertEqual(latvec.tolist(), [2.0, 4.0])

#     def test_get_latlon_grids(self):
#         bounds = rasterio.coords.BoundingBox(1, 2, 3, 4)
#         data = np.array([[1, 2], [3, 4]])
#         lonvec, latvec = self.bathy_req.get_latlon_grids(bounds, data)

#         self.assertEqual(lonvec.tolist(), [1.0, 3.0])
#         self.assertEqual(latvec.tolist(), [2.0, 4.0])

#     @patch.object(BathyRequest, 'get_area')
#     def test_get_point(self, mock_get_area):
#         mock_get_area.return_value = (np.array([[1, 2], [3, 4]]), np.array([1.0, 3.0]), np.array([2.0, 4.0]))

#         longitude = -117.43000
#         latitude = 32.55000
#         data = self.bathy_req.get_point(longitude, latitude)

#         self.assertEqual(data.tolist(), [1.0])

#     @patch('rasterio.open')
#     def test_load_data(self, mock_open):
#         mock_dataset = MagicMock()
#         mock_dataset.read.return_value = np.array([[1, 2], [3, 4]])
#         mock_dataset.bounds = rasterio.coords.BoundingBox(1, 2, 3, 4)
#         mock_open.return_value.__enter__.return_value = mock_dataset

#         filepath = Path("testfile")
#         data, bounds = self.bathy_req.load_data(filepath)

#         self.assertEqual(data.tolist(), [[1, 2], [3, 4]])
#         self.assertEqual(bounds, rasterio.coords.BoundingBox(1, 2, 3, 4))

# class TestClearCache(unittest.TestCase):
#     @patch('shutil.rmtree')
#     @patch('pathlib.Path.exists')
#     def test_clear_cache(self, mock_exists, mock_rmtree):
#         mock_exists.return_value = True
#         clear_cache(CACHE_DIR)
#         mock_rmtree.assert_called_once_with(CACHE_DIR)

        

# if __name__ == "__main__":
#     unittest.main()