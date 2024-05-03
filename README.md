# BathyReq

[![DOI](https://zenodo.org/badge/679471492.svg)](https://zenodo.org/badge/latestdoi/679471492)

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

req = bathyreq.BathyRequest()
data, lonvec, latvec = req.get_area(
    longitude=[-117.43, -117.23], latitude=[32.55, 32.75]
)
```

Download bathymetric data for a single longitude/latitude pair:
```python
import bathyreq

req = bathyreq.BathyRequest()
data = req.get_point(
    longitude=-117.43, latitude=32.75
)
```

## Methods not yet implemented

Download bathymetric data for a given set of longitude/latitude pairs:
```python
import bathyreq

req = bathyreq.BathyRequest()
data = req.get_points(
    longitude=[-117.43, -117.23], latitude=[32.55, 32.75]
)
```

Download bathymetric data for a given profile between two longitude/latitude pairs:
```python
import bathyreq

req = bathyreq.BathyRequest()
data = req.get_profile(
    longitude=[-117.43, -117.23], latitude=[32.55, 32.75]
)
```