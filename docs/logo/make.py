#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script to produce package logo."""

import argparse
from pathlib import Path

import bathyreq
import cmocean
from matplotlib.colors import TwoSlopeNorm
import matplotlib.pyplot as plt

DPI = 300
PATH = Path("../docs/assets")


def make_image(
    lon: list[float, float],
    lat: list[float, float],
    size: list[int, int],
    figsize: tuple[int, int],
) -> plt.Figure:
    req = bathyreq.BathyRequest()
    data, _, _ = req.get_area(longitude=lon, latitude=lat, size=size)

    fig = plt.figure(frameon=False, figsize=figsize)
    ax = plt.Axes(fig, [0, 0, 1, 1])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(data, cmap="cmo.topo", origin="lower", norm=TwoSlopeNorm(0))
    return fig


def make_logo(save: bool = False, show: bool = True) -> None:
    LON = [-117.30, -117.25]
    LAT = [32.84, 32.89]

    fig = make_image(LON, LAT, [1000, 1000], (3, 3))
    if save:
        fig.savefig(PATH / "logo.png", dpi=DPI)
        plt.close()
    if show:
        plt.show()


def make_banner(save: bool = False, show: bool = True) -> None:
    LON = [-117.36, -117.24]
    LAT = [32.845, 32.915]

    fig = make_image(LON, LAT, [2000, 1000], (6, 3))
    if save:
        fig.savefig(PATH / "banner.png", dpi=DPI)
        plt.close()
    if show:
        plt.show()


def main(args: argparse.Namespace) -> None:
    if args.banner:
        make_banner(args.save, args.show)
    if args.logo:
        make_logo(args.save, args.show)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Make logo and banner")
    parser.add_argument(
        "-l",
        "--logo",
        action="store_true",
        help="Make logo",
        default=True,
    )
    parser.add_argument(
        "-b",
        "--banner",
        action="store_true",
        help="Make banner",
        default=True,
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the logo and banner",
        default=False,
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the logo and banner",
        default=True,
    )
    args = parser.parse_args()
    main(args)
