#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Optional
import urllib.parse


class DataSources(Enum):
    NCEI: 0


@dataclass
class NCEIBase:
    host: str = "https://gis.ngdc.noaa.gov"
    context: str = "arcgis"
    endpoint: str = "rest/services"
    folder: str = "DEM_mosaics"
    serviceName: str = "DEM_global_mosaic"
    serviceType: str = "ImageServer"
    operation: str = "exportImage"

    def __post_init__(self) -> None:
        self.url = "/".join([v for k, v in asdict(self).items() if v is not None])


@dataclass
class NCEIRequest:
    bbox: list[str]
    size: list[int]
    format: str
    pixelType: str
    bboxSR: Optional[int] = None
    imageSR: Optional[int] = None
    nodata: float = 0.0
    interpolation: str = "RSP_NearestNeighbor"
    compression: str = "LZ77"
    renderingRule: Optional[str] = None
    f: str = "image"

    def __post_init__(self) -> None:
        self.format_attributes()
        self.build_request()

    def build_request(self) -> None:
        self.request = urllib.parse.urlencode(
            {k: v for k, v in asdict(self).items() if v is not None}
        )

    def format_attributes(self) -> None:
        self.bbox = f"{','.join(map('{:.5f}'.format, self.bbox))}"
        self.size = f"{','.join(map('{:d}'.format, self.size))}"


@dataclass
class NCEISource:
    base: NCEIBase = field(default_factory=NCEIBase())
    request: Optional[NCEIRequest] = None

    def __post_init__(self) -> None:
        self.build_url()

    def build_url(self) -> None:
        self.url = "?".join([self.base.url, self.request.request])
