# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2023-2024 William Jenkins

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module provides the `BathyRequest` class for requesting bathymetric data
from a public data source.

Examples:
    >>> import bathyreq
    >>> req = bathyreq.BathyRequest()
    >>> data, lonvec, latvec = req.get_area(
    ...     longitude=[-117.43000, -117.23000],
    ...     latitude=[32.55000, 32.75000],
    ...     size=[400, 400],
    ... )
    >>> print(data.shape)
    (400, 400)
    >>> data = req.get_point(longitude=-117.43000, latitude=32.55000)
    [-1017.61428833]
"""

from concurrent.futures import ThreadPoolExecutor
import datetime
from functools import partial
from pathlib import Path
import secrets
import shutil
from typing import Sequence
import warnings

from geopy import distance
import numpy as np
import rasterio
import requests
from scipy.interpolate import interpn

import bathyreq.sources.factory as factory

CACHE_DIR: Path = Path(__file__).parents[0] / "cache"


class ExcessivePointsWarning(UserWarning):
    """Excessive points warning."""

    pass


class BathyRequest:
    """Request bathymetry data from a data source.

    Attributes:
        source: Bathymetric data source.
        cache_dir: Path to cache directory.
        clear_cache: Clear cache after use.
    """

    def __init__(
        self,
        source: str = "ncei",
        cache_dir: Path = CACHE_DIR,
        clear_cache: bool = True,
    ) -> None:
        """Initialize the `BathyRequest` class.

        Args:
            source: Data source.
            cache_dir: Directory to cache downloaded data.
            clear_cache: Whether or not to delete files downloaded by this
                instance immediately after use.
        """
        self.source = source
        self.cache_dir = cache_dir
        self.clear_cache = clear_cache

    @staticmethod
    def download_data(url: str, filepath: Path):
        """Download data from URL to filepath.

        Args:
            url: URL to download data from.
            filepath: Path to save data to.

        Raises:
            requests.HTTPError: If the request to the URL fails.
        """

        r = requests.get(url, stream=True)
        r.raise_for_status()
        if r.status_code == 200:
            with open(filepath, "wb") as fd:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, fd)
        del r

    @staticmethod
    def form_bbox(
        longitude: float | Sequence[float],
        latitude: float | Sequence[float],
        single_point: bool = False,
    ) -> list[float, float, float, float]:
        """Form bounding box from longitude and latitude.

        Args:
            longitude: Longitude in the form `[lon_min, lon_max]`.
            latitude: Latitude in the form `[lat_min, lat_max]`.
            single_point: If `True`, add a small buffer to the bounding box.

        Returns:
            Bounding box in the form `[lon_min, lat_min, lon_max, lat_max]`.
        """
        if single_point:
            return [
                longitude - 0.001,
                latitude - 0.001,
                longitude + 0.001,
                latitude + 0.001,
            ]
        return [
            min(longitude),
            min(latitude),
            max(longitude),
            max(latitude),
        ]

    @staticmethod
    def generate_filename() -> str:
        """Generate a filename for the cache.

        Returns:
            Filename.
        """
        return (
            f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            f"{secrets.token_urlsafe(4)}"
        )

    def get_area(
        self,
        longitude: float | Sequence[float],
        latitude: float | Sequence[float],
        single_point: bool = False,
        **source_kwargs: dict,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get bathymetric data for an area.

        The area is defined by the min/max of the longitude and latitude
        vectors. The data source is instantiated and request URL built. Data are
        downloaded to the cache and loaded into memory. The cache is cleared if
        requested. Latitude and longitude grids (vectors) are generated from the
        bounding box and according to the bathymetric data dimensions.

        Examples:
            >>> import bathyreq
            >>> req = bathyreq.BathyRequest()
            >>> data, lonvec, latvec = req.get_area(
            ...     longitude=[-117.43000, -117.23000],
            ...     latitude=[32.55000, 32.75000],
            ...     size=[100, 400],
            ... )
            >>> print(data.shape)
            (400, 100)

        Args:
            longitude: Longitude in the form `[lon_min, lon_max]`.
            latitude: Latitude in the form `[lat_min, lat_max]`.
            single_point: If `True`, add a small buffer to the bounding box.
            **source_kwargs: Keyword arguments to pass to `Source`. For example,
                `size=[100, 400]` ([n_longitude, n_latitude]).

        Returns:
            Bathymetric data (n_latitude, n_longitude)
            Longitude grid
            Latitude grid.

        Raises:
            requests.HTTPError: If the request to the URL fails.
        """
        # Initialize cache
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Form boundary box
        bbox = self.form_bbox(longitude, latitude, single_point=single_point)

        # Instantiate data source and get request URL
        if single_point:
            source_kwargs["size"] = [2, 2]
        data_source = factory.factory(bbox=bbox, source=self.source, **source_kwargs)
        data_source.build_url()

        # Download data to cache
        fmt = data_source.request.format
        if fmt == "image/jpeg":
            fmt = "jpeg"
        if fmt == "image/tiff":
            fmt = "tiff"
        filepath = (self.cache_dir / self.generate_filename()).with_suffix("." + fmt)
        self.download_data(data_source.url, filepath)

        # Load data from cache
        data, bounds = self.load_data(filepath)

        # Clear cache if requested
        if self.clear_cache:
            filepath.unlink()

        # Get lat/lon grids
        lonvec, latvec = self.get_latlon_grids(bounds, data)

        return data, lonvec, latvec

    @staticmethod
    def get_latlon_grids(
        bounds: rasterio.coords.BoundingBox, data: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Get lat/lon grids from bounding box and data.

        Args:
            bounds: Bounding box.
            data: Bathymetric data (n_latitude x n_longitude).

        Returns:
            Longitude and latitude grids.
        """
        return np.linspace(bounds.left, bounds.right, data.shape[1]), np.linspace(
            bounds.bottom, bounds.top, data.shape[0]
        )

    def get_point(
        self,
        longitude: float | Sequence[float],
        latitude: float | Sequence[float],
        interp_method: str = "linear",
        **source_kwargs: dict,
    ) -> np.ndarray:
        """Get bathymetric data for a single point.

        A small area of bathymetry surrounding the query point is downloaded
        and interpolated at the query points `longitude` and `latitude`.

        Args:
            longitude: Longitude.
            latitude: Latitude.
            interp_method:
                Interpolation method, by default "linear".
            **source_kwargs: Keyword arguments to pass to the data source.

        Returns:
            Bathymetric data interpolated at the query points `longitude` and `latitude`.
        """
        DECIMALS = 5

        data, lonvec, latvec = self.get_area(
            longitude, latitude, single_point=True, **source_kwargs
        )
        return interpn(
            (np.round(latvec, DECIMALS), np.round(lonvec, DECIMALS)),
            data,
            np.round(np.vstack((latitude, longitude)).T, DECIMALS),
            method=interp_method,
        )

    def get_points(
        self,
        points: Sequence[tuple[float, float]],
        interp_method: str = "linear",
        **source_kwargs: dict,
    ) -> list[float]:
        """Get bathymetry for a list of longitude/latitude points.

        Args:
            points: List of longitude/latitude points specified as tuples.
            interp_method: Interpolation method, by default "linear".
            **source_kwargs: Keyword arguments to pass to the data source.

        Returns:
            List of bathymetric data for each point.
        """
        with ThreadPoolExecutor(max_workers=32) as executor:
            return list(
                executor.map(
                    partial(
                        self.get_point, interp_method=interp_method, **source_kwargs
                    ),
                    [point[0] for point in points],
                    [point[1] for point in points],
                )
            )

    def get_transect(
        self,
        point1: Sequence[float],
        point2: Sequence[float],
        num_points: int = 100,
        interp_method: str = "linear",
        **source_kwargs: dict,
    ) -> tuple[list[tuple[float, float]], list[float], list[float]]:
        """Get bathymetry along a great circle transect.

        Args:
            point1: First point (longitude, latitude).
            point2: Second point (longitude, latitude).
            num_points: Number of points along the transect, by default 100.
            interp_method: Interpolation method, by default "linear".
            **source_kwargs: Keyword arguments to pass to the data source.

        Returns:
            Points along the transect.
            Bathymetry at each point.
            Distances along the transect.
        """

        if num_points > 800:
            warnings.warn(
                ">800 points requested. The server may be unable to handle "
                "this request; `num_points` set to 800. For larger requests, "
                "consider retrieving an area using `get_area` and interpolating.",
                ExcessivePointsWarning,
            )
            num_points = 800

        # Generate points along great circle transect (lon/lat pairs)
        points = self.create_great_circle_transect(
            point1[0], point1[1], point2[0], point2[1], num_points=num_points
        )
        # Get bathymetry at points
        bathy = self.get_points(points, interp_method, **source_kwargs)
        # Compute distances along track
        distances = [
            distance.geodesic(reversed(points[0]), reversed(point)).km
            for point in points
        ]
        return points, bathy, distances

    @staticmethod
    def create_great_circle_transect(
        lon1: float, lat1: float, lon2: float, lat2: float, num_points: int = 100
    ) -> list[tuple[float, float]]:
        """Generate a great circle transect between two geographic points."""
        lons = np.linspace(lon1, lon2, num_points)
        lats = np.linspace(lat1, lat2, num_points)
        return list(zip(lons, lats))

    @staticmethod
    def load_data(filepath: Path) -> tuple[np.ndarray, rasterio.coords.BoundingBox]:
        """Load data from filepath.

        Args:
            filepath: Path to load data from.

        Returns:
            Bathymetric data (n_latitude x n_longitude).
            Bounding box.
        """
        with rasterio.open(filepath, "r") as dataset:
            return dataset.read(1), dataset.bounds


def clear_cache(cache_dir: Path = CACHE_DIR) -> None:
    """Clears cache.

    Since bathymetric data can be large, it is cached to disk. This function
    clears the cache, which may be good to do periodically if you are not doing
    so upon each request.

    Examples:
        >>> import bathyreq
        >>> bathyreq.clear_cache()

    Args:
        cache_dir: Path to cache directory, by default CACHE_DIR.
    """
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
