#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script to produce package logo."""

import bathyreq
import cmocean
from matplotlib.colors import TwoSlopeNorm
import matplotlib.pyplot as plt

lons = [-117.30, -117.25]
lats = [32.84, 32.89]


def main():
    req = bathyreq.BathyRequest()
    data, _, _ = req.get_area(longitude=lons, latitude=lats, size=[1000, 1000])

    fig = plt.figure(figsize=(10, 10))
    plt.imshow(data, cmap="cmo.topo", origin="lower", norm=TwoSlopeNorm(0))
    plt.axis("off")
    fig.savefig("logo.png", pad_inches=0, dpi=300)
    plt.close()


if __name__ == "__main__":
    main()
