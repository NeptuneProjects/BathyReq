#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from pathlib import Path
import secrets
import shutil
from typing import Iterable, Optional, Protocol, Union

import numpy as np
import rasterio
import requests
from scipy.interpolate import interpn

import sources

SMOKE_TEST = True
CACHE_DIR = Path("cache")


class DataSource(Protocol):
    def __init__(self) -> None:
        ...


class BathyRequest:
    def __init__(
        self,
        source: DataSource = sources.NOAASource(),
        cache_dir: Path = CACHE_DIR,
    ) -> None:
        self.source = source
        self.cache_dir = cache_dir

    def __call__(
        self,
        longitude: Union[float, Iterable[float]],
        latitude: Union[float, Iterable[float]],
    ):
        return self.get(longitude, latitude)

    def download_data(self, filepath: Path):
        r = requests.get(self.source.url, stream=True)
        if r.status_code == 200:
            with open(filepath, "wb") as fd:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, fd)
        del r

    def load_data(
        self, filepath: Path
    ) -> tuple[np.ndarray, rasterio.coords.BoundingBox]:
        with rasterio.open(filepath, "r") as dataset:
            return np.flipud(dataset.read(1)), dataset.bounds

    def format_request(self):
        self.source.format_attributes()  # TODO: Build interface here
        self.source.build_url()

    @staticmethod
    def generate_filename() -> str:
        return (
            f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_"
            f"{secrets.token_urlsafe(16)}"
        )

    def get(
        self,
        longitude: Union[float, Iterable[float]],
        latitude: Union[float, Iterable[float]],
    ) -> tuple[np.ndarray, rasterio.coords.BoundingBox, np.ndarray, np.ndarray]:
        self.format_request()  # TODO: Build interface here
        filepath = self.cache_dir / (self.generate_filename() + self.source.format)
        self.download_data(filepath)
        data, bounds = self.load_data(filepath)
        lonvec, latvec = self.get_latlon_grids(bounds, data)
        return data, bounds, lonvec, latvec

    def get_latlon_grids(self, bounds: rasterio.coords.BoundingBox, data: np.ndarray):
        return np.linspace(bounds.left, bounds.right, data.shape[1]), np.linspace(
            bounds.bottom, bounds.top, data.shape[0]
        )

    def interpolate(
        self,
        data: np.ndarray,
        lonvec: np.ndarray,
        latvec: np.ndarray,
        longitude: Union[float, Iterable[float]],
        latitude: Union[float, Iterable[float]],
        method: Optional[str] = "linear",
    ) -> np.ndarray:
        return interpn(
            (lonvec, latvec), data.T, np.vstack((longitude, latitude)).T, method=method
        )


if (__name__ == "__main__") and SMOKE_TEST:
    lonq = -117.5
    latq = 32.5
    br = BathyRequest()
    data, _, lonvec, latvec = br.get(lonq, latq)
    bathy = br.interp(data, lonvec, latvec, lonq, latq)
    print("Complete!")
