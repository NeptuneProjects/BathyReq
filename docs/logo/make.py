#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script to produce package logo."""

import argparse
from pathlib import Path

import bathyreq
import cmocean
from matplotlib.colors import TwoSlopeNorm
import matplotlib.pyplot as plt

PATH = Path("../docs/assets")


def make_image(lon, lat, size, figsize, dpi=300) -> plt.Figure:
    req = bathyreq.BathyRequest()
    data, _, _ = req.get_area(longitude=lon, latitude=lat, size=size)

    fig = plt.figure(frameon=False, figsize=figsize)
    ax = plt.Axes(fig, [0, 0, 1, 1])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(data, cmap="cmo.topo", origin="lower", norm=TwoSlopeNorm(0))
    return fig


def make_logo() -> None:
    LON = [-117.30, -117.25]
    LAT = [32.84, 32.89]

    make_image(LON, LAT, [1000, 1000], (3, 3)).savefig(PATH / "logo.png")
    plt.close()


def make_banner() -> None:
    LON = [-117.36, -117.24]
    LAT = [32.845, 32.915]

    make_image(LON, LAT, [2000, 1000], (6, 3)).savefig(PATH / "banner.png")
    plt.close()


def main(args: argparse.Namespace):
    if args.banner:
        make_banner()
    if args.logo:
        make_logo()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make logo and banner")
    parser.add_argument(
        "-l",
        "--logo",
        action="store_true",
        help="Make logo",
    )
    parser.add_argument(
        "-b",
        "--banner",
        action="store_true",
        help="Make banner",
    )
    args = parser.parse_args()
    main(args)
