# BathyReq
A Python package for querying public bathymetric data sources.
Currently only digital elevation model (DEM) data from the [NOAA National Centers for Environmental Information (NCEI)](https://www.ncei.noaa.gov/) database is supported.
Future development will focus on implementing other sources, such as the [General Bathymetric Chart of the Oceans (GEBCO)](https://www.gebco.net) and NOAA's new [Blue Topo](https://nauticalcharts.noaa.gov/data/bluetopo.html) project.

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

## Contributing

Contributions are welcome! If you have any issues using the package, please open an issue on GitHub. If you would like to contribute to the package, please fork the repository and open a pull request.


## Support

If you find this package useful and if it's saved you lots of time and effort, please consider supporting the project by buying me a coffee!

<a href="https://www.buymeacoffee.com/wjenkins" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
