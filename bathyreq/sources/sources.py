#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from typing import Protocol

from bathyreq.sources import blue_topo, gebco, ncei


class DataSourceNotImplemented(Exception):
    pass


class DataSource(Enum):
    BLUE_TOPO = "blue_topo"
    GEBCO = "gebco"
    NCEI = "ncei"


class Source(Protocol):
    """Interface for data sources to the bathymetry requester."""

    def __init__(self) -> None:
        ...

    def build_url() -> None:
        ...


def factory(
    bbox: list[float, float, float, float], source: str = "ncei", **kwargs
) -> Source:
    """Factory function to return a source object.

    Parameters
    ----------
    bbox : list[float, float, float, float]
        Bounding box in the form [lon_min, lat_min, lon_max, lat_max].
    source : str, optional
        Source of the data, by default "ncei".

    Returns
    -------
    Source
        Source object.

    Raises
    ------
    DataSourceNotImplemented
        Raised if the data source is not implemented.

    Examples
    --------
    >>> from bathyreq.sources import factory
    >>> inst = factory(bbox=[-117, 32, -116, 33], source="ncei")
    >>> inst.build_url()
    >>> url = inst.url
    """
    if DataSource(source) == DataSource.BLUE_TOPO:
        raise DataSourceNotImplemented("BLUE_TOPO not implemented yet.")
    elif DataSource(source) == DataSource.GEBCO:
        raise DataSourceNotImplemented("GEBCO not implemented yet.")
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
