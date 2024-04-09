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

import cmocean
from matplotlib.colors import TwoSlopeNorm
import matplotlib.pyplot as plt
import numpy as np


def plot_bathy(
    data: np.ndarray,
    lonvec: np.ndarray,
    latvec: np.ndarray,
    cmap_sea: str = "cmo.deep",
    cmap_land: str = "cmo.topo",
    ax: plt.Axes = None,
) -> None:

    if ax is None:
        ax = plt.gca()

    all_colors = np.vstack((colors_undersea, colors_land))

    ax.imshow(
        data,
        extent=(lonvec[0], lonvec[-1], latvec[0], latvec[-1]),
        cmap=cmap,
        origin="lower",
        norm=TwoSlopeNorm(0),
    )
    return
