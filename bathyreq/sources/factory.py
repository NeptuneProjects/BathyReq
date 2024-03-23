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

"""Module provides factory function to build `Source` instances."""

from enum import Enum
from typing import Protocol

from bathyreq.sources import blue_topo, gebco, ncei


class DataSourceNotImplemented(Exception):
    """Raised when a data source is not implemented."""
    pass


class DataSource(Enum):
    """Data sources for bathymetry data.
    
    Attributes:
        BLUE_TOPO: Blue Topo data source.
        GEBCO: GEBCO data source.
        NCEI: NCEI data source.    
    """
    BLUE_TOPO = "blue_topo"
    GEBCO = "gebco"
    NCEI = "ncei"


class Source(Protocol):
    """Interface used within `BathyRequest` to construct URL request."""

    def build_url() -> None:
        """Build the URL request."""
        ...


def factory(
    bbox: list[float, float, float, float], source: str = "ncei", **kwargs
) -> Source:
    """Factory function to return a source object.

    Examples:
        >>> from bathyreq.sources import factory
        >>> inst = factory(bbox=[-117, 32, -116, 33], source="ncei")
        >>> inst.build_url()
        >>> url = inst.url
    
    Args:
        bbox: Bounding box in the form [lon_min, lat_min, lon_max, lat_max].
        source: Source of the data, by default "ncei".

    Returns:
        Source object.

    Raises:
        DataSourceNotImplemented: Raised if the data source is not implemented.
    """
    if DataSource(source) == DataSource.BLUE_TOPO:
        raise DataSourceNotImplemented("BLUE_TOPO not implemented yet.")
    elif DataSource(source) == DataSource.GEBCO:
        size = kwargs.get("size", [400, 400])
        return gebco.GEBCOSource(
            base=gebco.GEBCOBase(),
            request=gebco.GEBCORequest(
                request="getmap",
                service="wms",
                BBOX=bbox,
                crs=kwargs.get("crs", "EPSG:4326"),
                # format=kwargs.get("format", "image/jpeg"),
                format=kwargs.get("format", "image/tiff"),
                layers=kwargs.get("layers", "gebco_latest_sub_ice_topo"),
                width=size[0],
                height=size[1],
                version=kwargs.get("version", "1.3.0"),
            ),
        )
    if DataSource(source) == DataSource.NCEI:
        return ncei.NCEISource(
            base=ncei.NCEIBase(),
            request=ncei.NCEIRequest(
                bbox=bbox,
                size=kwargs.get("size", [400, 400]),
                format=kwargs.get("format", "tiff"),
                nodata=kwargs.get("nodata", 0),
                pixelType=kwargs.get("pixelType", "F32"),
                interpolation=kwargs.get("interpolation", "RSP_NearestNeighbor"),
                compression=kwargs.get("compression", "LZ77"),
                f=kwargs.get("f", "image"),
            ),
        )
