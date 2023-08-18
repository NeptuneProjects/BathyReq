# BathyReq

<div align="center"> <img src="docs/docs/assets/banner.png"> </div>

A Python package for querying public bathymetric data sources.
Currently only digital elevation model (DEM) data from the [NOAA National Centers for Environmental Information (NCEI)](https://www.ncei.noaa.gov/) database is supported.
Future development will focus on implementing other sources, such as the [General Bathymetric Chart of the Oceans (GEBCO)](https://www.gebco.net) and NOAA's new [Blue Topo](https://nauticalcharts.noaa.gov/data/bluetopo.html) project.

## Installation
```bash
pip install bathyreq
```

## Usage

Download bathymetric data for a given area:
```python
import bathyreq

req = bathyreq.BathyReq()
data, lonvec, latvec = req.get_area(
    longitude=[-117.43, -117.23], latitude=[32.55, 32.75]
)
```

Download bathymetric data for a given set of longitude/latitude pairs:
```python
import bathyreq

req = bathyreq.BathyReq()
data = req.get_points(
    longitude=[-117.43, -117.23], latitude=[32.55, 32.75]
)
```
