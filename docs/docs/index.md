# BathyReq
A Python package for querying public bathymetric data sources.
Currently only digital elevation model (DEM) data from the [NOAA National Centers for Environmental Information (NCEI)](https://www.ncei.noaa.gov/) database is supported.

> [!WARNING]
> This package is still in development.

## Installation
```bash
pip install git+https://github.com/NeptuneProjects/BathyReq.git
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
