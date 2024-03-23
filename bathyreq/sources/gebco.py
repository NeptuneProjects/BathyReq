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

"""Module for composing GEBCO `Source`."""

from dataclasses import asdict, dataclass, field
from typing import Optional
import urllib.parse


@dataclass
class GEBCOBase:
    """Base class for GEBCO requests.
    """

    url: str = "https://www.gebco.net/data_and_products/gebco_web_services/web_map_service/mapserv"
        

@dataclass
class GEBCORequest:
    BBOX: list[str]
    request: str = "getmap"
    service: str = "wms"
    crs: str = "EPSG:4326"
    format: str = "image/jpeg"
    layers: str = "gebco_latest_sub_ice_topo"
    width: int = 1200
    height: int = 600
    version: str = "1.3.0"

    def build_request(self) -> None:
        self.format_attributes()
        self.request = urllib.parse.urlencode(asdict(self))


    def format_attributes(self) -> None:
        """Format the attributes for proper parsing of the request string.

        Returns:
            The attributes are formatted in place.
        """
        self.BBOX = f"{','.join(map('{:.5f}'.format, self.BBOX))}"


@dataclass
class GEBCOSource:
    base: GEBCOBase = field(default_factory=GEBCOBase())
    request: Optional[GEBCORequest] = None

    def build_url(self) -> None:
        """Build the URL for the request.

        Returns:
            The URL is stored in the `url` attribute.
        """
        self.base
        self.request.build_request()
        self.url = "?".join([self.base.url, self.request.request])
