#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from pathlib import Path
import secrets
import shutil
from typing import Iterable, Optional, Union

import numpy as np
import rasterio
import requests
from scipy.interpolate import interpn

import bathyreq.sources.sources as sources

SMOKE_TEST = True
CACHE_DIR = Path(__file__).parents[0] / "cache"


class BathyRequest:

    """Request bathymetry data from a data source.

    Parameters
    ----------
    source : Optional[str], optional
        Bathymetric data source, by default "ncei".
    cache_dir : Path, optional
        Path to cache directory, by default CACHE_DIR.
    clear_cache : bool, optional
        Clear cache after use, by default True.

    Attributes
    ----------
    source : Optional[str]
        Bathymetric data source.
    cache_dir : Path
        Path to cache directory.
    clear_cache : bool
        Clear cache after use.

    Methods
    -------
    download_data(url: str, filepath: Path)
        Download data from URL to filepath.
    form_bbox(
        longitude: Union[float, Iterable[float]],
        latitude: Union[float, Iterable[float]]
    )
    generate_filename()
        Generate a filename for the cache.
    get_area(
        longitude: Union[float, Iterable[float]],
        latitude: Union[float, Iterable[float]], **source_kwargs
    )
        Get bathymetric data for an area.
    get_point(
        longitude: Union[float, Iterable[float]],
        latitude: Union[float, Iterable[float]],
        interp_method: Optional[str]
    )
        Get bathymetric data for a point.
        Form bounding box from longitude and latitude.
    load_data(filepath: Path)
        Load data from filepath.

    Examples
    --------
    >>> import bathyreq
    >>> req = bathyreq.BathyRequest()
    >>> data, lonvec, latvec = req.get_area(
    ...     longitude=[-117.43000, -117.23000], latitude=[32.55000, 32.75000]
    ... )
    >>> print(data.shape)
    (400, 400)
    >>> data = req.get_point(longitude=-117.43000, latitude=32.55000)
    """

    def __init__(
        self,
        source: Optional[str] = "ncei",
        cache_dir: Path = CACHE_DIR,
        clear_cache: bool = True,
    ) -> None:
        self.source = source
        self.cache_dir = cache_dir
        self.clear_cache = clear_cache

    @staticmethod
    def download_data(url: str, filepath: Path):
        """Download data from URL to filepath.

        Parameters
        ----------
        url : str
            URL to download data from.
        filepath : Path
            Path to save data to.

        Raises
        ------
        requests.HTTPError
            If the request to the URL fails.
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
        longitude: Union[float, Iterable[float]],
        latitude: Union[float, Iterable[float]],
    ) -> list[float, float, float, float]:
        """Form bounding box from longitude and latitude.

        Parameters
        ----------
        longitude : Union[float, Iterable[float]]
            Longitude in the form [lon_min, lon_max].
        latitude : Union[float, Iterable[float]]
            Latitude in the form [lat_min, lat_max].

        Returns
        -------
        list[float, float, float, float]
            Bounding box in the form [lon_min, lat_min, lon_max, lat_max].
        """
        return [
            np.min(longitude),
            np.min(latitude),
            np.max(longitude),
            np.max(latitude),
        ]

    @staticmethod
    def generate_filename() -> str:
        """Generate a filename for the cache.

        Returns
        -------
        str
            Filename.
        """
        return (
            f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            f"{secrets.token_urlsafe(4)}"
        )

    def get_area(
        self,
        longitude: Union[float, Iterable[float]],
        latitude: Union[float, Iterable[float]],
        **source_kwargs,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Get bathymetric data for an area.

        Parameters
        ----------
        longitude : Union[float, Iterable[float]]
            Longitude in the form [lon_min, lon_max].
        latitude : Union[float, Iterable[float]]
            Latitude in the form [lat_min, lat_max].
        **source_kwargs
            Keyword arguments to pass to the data source.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray]
            Bathymetric data, longitude grid, and latitude grid.

        Raises
        ------
        requests.HTTPError
            If the request to the URL fails.

        Notes
        -----
        The area is defined by the min/max of the longitude and latitude
        vectors. The data source is instantiated and request URL built. Data are
        downloaded to the cache and loaded into memory. The cache is cleared if
        requested. Latitude and longitude grids (vectors) are generated from the
        bounding box and according to the bathymetric data dimensions.
        """
        # Initialize cache
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Form boundary box
        bbox = self.form_bbox(longitude, latitude)
        # Instantiate data source and get request URL
        data_source = sources.factory(bbox=bbox, source=self.source, **source_kwargs)
        data_source.build_url()
        # Download data to cache
        filepath = (self.cache_dir / self.generate_filename()).with_suffix(
            "." + data_source.request.format
        )
        self.download_data(data_source.url, filepath)
        # Load data from cache
        data, bounds = self.load_data(filepath)
        # Clear cache if requested
        if self.clear_cache:
            filepath.unlink()
        # Get lat/lon grids
        lonvec, latvec = self._get_latlon_grids(bounds, data)

        return data, lonvec, latvec

    @staticmethod
    def _get_latlon_grids(bounds: rasterio.coords.BoundingBox, data: np.ndarray):
        """Get lat/lon grids from bounding box and data.

        Parameters
        ----------
        bounds : rasterio.coords.BoundingBox
            Bounding box.
        data : np.ndarray
            Bathymetric data.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Longitude and latitude grids.
        """
        return np.linspace(bounds.left, bounds.right, data.shape[1]), np.linspace(
            bounds.bottom, bounds.top, data.shape[0]
        )

    def get_point(
        self,
        longitude: Union[float, Iterable[float]],
        latitude: Union[float, Iterable[float]],
        interp_method: Optional[str] = "linear",
    ) -> np.ndarray:
        """Get bathymetric data for a point.

        Parameters
        ----------
        longitude : Union[float, Iterable[float]]
            Longitude.
        latitude : Union[float, Iterable[float]]
            Latitude.
        interp_method : Optional[str], optional
            Interpolation method, by default "linear". See SciPy documentation for
            details (https://docs.scipy.org/doc/scipy/reference/interpolate.html).

        Returns
        -------
        np.ndarray
            Bathymetric data interpolated at the query points `longitude` and
            `latitude`.

        Notes
        -----
        An area of bathymetry is downloaded according to the min/max of the
        supplied longitude and latitude vectors. The data source is instantiated
        and request URL built. Data are downloaded to the cache and loaded into
        memory. The cache is cleared if requested. Bathymetric data are
        interpolated at the query points `longitude` and `latitude`.

        """
        data, lonvec, latvec = self.get_area(longitude, latitude)
        return interpn(
            (lonvec, latvec),
            data.T,
            np.vstack((longitude, latitude)).T,
            method=interp_method,
        )

    @staticmethod
    def load_data(filepath: Path) -> tuple[np.ndarray, rasterio.coords.BoundingBox]:
        """Load data from filepath.

        Parameters
        ----------
        filepath : Path
            Path to load data from.

        Returns
        -------
        tuple[np.ndarray, rasterio.coords.BoundingBox]
            Bathymetric data and bounding box.
        """
        with rasterio.open(filepath, "r") as dataset:
            return np.flipud(dataset.read(1)), dataset.bounds


def clear_cache(cache_dir: Path = CACHE_DIR):
    """Clears cache.

    Parameters
    ----------
    cache_dir : Path, optional
        Path to cache directory, by default CACHE_DIR.

    Returns
    -------
    None

    Notes
    -----
    Since bathymetric data can be large, it is cached to disk. This function
    clears the cache, which may be good to do periodically if you are not doing
    so upon each request.
    """
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
