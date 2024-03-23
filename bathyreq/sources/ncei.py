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

"""Module for composing NCEI `Source`."""

from dataclasses import asdict, dataclass, field
from typing import Optional
import urllib.parse


@dataclass
class NCEIBase:
    """Base class for NCEI requests.

    Attributes:
        host: Host URL.
        context: Context.
        endpoint: Endpoint.
        folder: Folder.
        serviceName: Service name.
        serviceType: Service type.
        operation: Operation.
        url: URL for the request (set with `self.build_base_url()`).

    Examples:
        >>> from bathyreq.sources import ncei
        >>> inst = ncei.NCEIBase()
        >>> inst.build_base_url()
        >>> inst.url
    """

    host: str = "https://gis.ngdc.noaa.gov"
    context: str = "arcgis"
    endpoint: str = "rest/services"
    folder: str = "DEM_mosaics"
    serviceName: str = "DEM_global_mosaic"
    serviceType: str = "ImageServer"
    operation: str = "exportImage"

    def build_base_url(self) -> None:
        """Build the base URL for the request.

        For further documentation, see https://gis.ngdc.noaa.gov/arcgis/sdk/rest/.

        Returns:
            The base URL is stored in the `url` attribute.
        """
        self.url = "/".join([v for v in asdict(self).values() if v is not None])


@dataclass
class NCEIRequest:
    """Request class for NCEI requests.

    Additional documentation available at 
    https://gis.ngdc.noaa.gov/arcgis/sdk/rest/#/Image_Service/02ss00000021000000/

    Attributes:
        bbox: Bounding box in the form [lon_min, lat_min, lon_max, lat_max].
        size: Size of the image in the form [width, height].
        forma :Image format.
        pixelType: Pixel type.
        bboxSR: Bounding box spatial reference, by default None.
        imageSR: Image spatial reference, by default None.
        nodata: No data value, by default 0.0.
        interpolation: Interpolation method, by default "RSP_NearestNeighbor".
        compression: Compression method, by default "LZ77".
        renderingRule: Rendering rule, by default None.
        f: Format, by default "image".
        request: Request string (set with `self.build_request()`).

    Examples:
        >>> from bathyreq.sources import ncei
        >>> inst = ncei.NCEIRequest(
        ...     bbox=[-117.43000, 32.55000, -117.43000, 32.55000],
        ...     size=[400, 400],
        ... )
        >>> inst.build_request()
        >>> inst.request
    """

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

    def build_request(self) -> None:
        """Build the request string.

        Returns:
            The request string is stored in the `request` attribute.
        """
        self.format_attributes()
        self.request = urllib.parse.urlencode(
            {k: v for k, v in asdict(self).items() if v is not None}
        )

    def format_attributes(self) -> None:
        """Format the attributes for proper parsing of the request string.

        Returns:
            The attributes are formatted in place.
        """
        self.bbox = f"{','.join(map('{:.5f}'.format, self.bbox))}"
        self.size = f"{','.join(map('{:d}'.format, self.size))}"


@dataclass
class NCEISource:
    """Source class for NCEI requests.

    Additional documentation available at 
    https://gis.ngdc.noaa.gov/arcgis/sdk/rest/.
    
    Attributes:
        base: Base class for NCEI requests, by default NCEIBase().
        request: Request class for NCEI requests, by default None.
        url: URL for the request.

    Examples:
        >>> from bathyreq.sources import ncei
        >>> inst = ncei.NCEISource(
        ...     base=ncei.NCEIBase(),
        ...     request=ncei.NCEIRequest(
        ...         bbox=[-117.43000, 32.55000, -117.43000, 32.55000],
        ...         size=[400, 400],
        ...     ),
        ... )
        >>> inst.build_url()
        >>> inst.url
    """

    base: NCEIBase = field(default_factory=NCEIBase())
    request: Optional[NCEIRequest] = None

    def build_url(self) -> None:
        """Build the URL for the request.

        Returns:
            The URL is stored in the `url` attribute.
        """
        self.base.build_base_url()
        self.request.build_request()
        self.url = "?".join([self.base.url, self.request.request])
