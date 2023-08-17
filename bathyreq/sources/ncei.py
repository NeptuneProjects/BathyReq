# -*- coding: utf-8 -*-

from dataclasses import asdict, dataclass, field
from typing import Optional
import urllib.parse


@dataclass
class NCEIBase:
    # """Base class for NCEI requests.

    # Parameters
    # ----------
    # host : str, optional
    #     Host URL, by default "https://gis.ngdc.noaa.gov".
    # context : str, optional
    #     Context, by default "arcgis".
    # endpoint : str, optional
    #     Endpoint, by default "rest/services".
    # folder : str, optional
    #     Folder, by default "DEM_mosaics".
    # serviceName : str, optional
    #     Service name, by default "DEM_global_mosaic".
    # serviceType : str, optional
    #     Service type, by default "ImageServer".
    # operation : str, optional
    #     Operation, by default "exportImage".

    # Attributes
    # ----------
    # url : str
    #     URL for the request.

    # Examples
    # --------
    # >>> from bathyreq.sources import ncei
    # >>> inst = ncei.NCEIBase()
    # >>> inst.build_base_url()
    # >>> inst.url

    # Methods
    # -------
    # build_base_url()
    #     Build the base URL for the request.
    # """

    host: str = "https://gis.ngdc.noaa.gov"
    context: str = "arcgis"
    endpoint: str = "rest/services"
    folder: str = "DEM_mosaics"
    serviceName: str = "DEM_global_mosaic"
    serviceType: str = "ImageServer"
    operation: str = "exportImage"

    def build_base_url(self) -> None:
        """Build the base URL for the request.

        Returns
        -------
        None
            The base URL is stored in the `url` attribute.

        References
        ----------
        .. [1] https://gis.ngdc.noaa.gov/arcgis/sdk/rest/
        """
        self.url = "/".join([v for k, v in asdict(self).items() if v is not None])


@dataclass
class NCEIRequest:
    # """Request class for NCEI requests.

    # Parameters
    # ----------
    # bbox : list[str]
    #     Bounding box in the form [lon_min, lat_min, lon_max, lat_max].
    # size : list[int]
    #     Size of the image in the form [width, height].
    # format : str
    #     Image format.
    # pixelType : str
    #     Pixel type.
    # bboxSR : Optional[int], optional
    #     Bounding box spatial reference, by default None.
    # imageSR : Optional[int], optional
    #     Image spatial reference, by default None.
    # nodata : float, optional
    #     No data value, by default 0.0.
    # interpolation : str, optional
    #     Interpolation method, by default "RSP_NearestNeighbor".
    # compression : str, optional
    #     Compression method, by default "LZ77".
    # renderingRule : Optional[str], optional
    #     Rendering rule, by default None.
    # f : str, optional
    #     Format, by default "image".

    # Attributes
    # ----------
    # request : str
    #     Request string.

    # Methods
    # -------
    # build_request()
    #     Build the request string.
    # format_attributes()
    #     Format the attributes for the request string.

    # Examples
    # --------
    # >>> from bathyreq.sources import ncei
    # >>> inst = ncei.NCEIRequest(
    # ...     bbox=[-117.43000, 32.55000, -117.43000, 32.55000],
    # ...     size=[400, 400],
    # ... )
    # >>> inst.build_request()
    # >>> inst.request

    # References
    # ----------
    # .. [1] https://gis.ngdc.noaa.gov/arcgis/sdk/rest/#/Image_Service/02ss00000021000000/
    # """

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
        # """Build the request string.

        # Returns
        # -------
        # None
        #     The request string is stored in the `request` attribute.
        # """
        self.format_attributes()
        self.request = urllib.parse.urlencode(
            {k: v for k, v in asdict(self).items() if v is not None}
        )

    def format_attributes(self) -> None:
        """Format the attributes for proper parsing of the request string.

        Returns
        -------
        None
            The attributes are formatted in place.
        """
        self.bbox = f"{','.join(map('{:.5f}'.format, self.bbox))}"
        self.size = f"{','.join(map('{:d}'.format, self.size))}"


@dataclass
class NCEISource:
    # """Source class for NCEI requests.

    # Parameters
    # ----------
    # base : NCEIBase, optional
    #     Base class for NCEI requests, by default NCEIBase().
    # request : Optional[NCEIRequest], optional
    #     Request class for NCEI requests, by default None.

    # Attributes
    # ----------
    # url : str
    #     URL for the request.

    # Methods
    # -------
    # build_url()
    #     Build the URL for the request.

    # Examples
    # --------
    # >>> from bathyreq.sources import ncei
    # >>> inst = ncei.NCEISource(
    # ...     base=ncei.NCEIBase(),
    # ...     request=ncei.NCEIRequest(
    # ...         bbox=[-117.43000, 32.55000, -117.43000, 32.55000],
    # ...         size=[400, 400],
    # ...     ),
    # ... )
    # >>> inst.build_url()
    # >>> inst.url

    # References
    # ----------
    # .. [1] https://gis.ngdc.noaa.gov/arcgis/sdk/rest/
    # """

    base: NCEIBase = field(default_factory=NCEIBase())
    request: Optional[NCEIRequest] = None

    def build_url(self) -> None:
        # """Build the URL for the request.

        # Returns
        # -------
        # None
        #     The URL is stored in the `url` attribute.
        # """
        self.base.build_base_url()
        self.request.build_request()
        self.url = "?".join([self.base.url, self.request.request])
