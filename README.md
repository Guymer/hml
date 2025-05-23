# How Much Land (HML)

!["coverage" GitHub Action Status](https://github.com/Guymer/PyGuymer3/actions/workflows/coverage.yaml/badge.svg) !["gmake" GitHub Action Status](https://github.com/Guymer/hml/actions/workflows/gmake.yaml/badge.svg) !["mypy" GitHub Action Status](https://github.com/Guymer/hml/actions/workflows/mypy.yaml/badge.svg) !["profile" GitHub Action Status](https://github.com/Guymer/PyGuymer3/actions/workflows/profile.yaml/badge.svg) !["pylint" GitHub Action Status](https://github.com/Guymer/hml/actions/workflows/pylint.yaml/badge.svg) !["unittest" GitHub Action Status](https://github.com/Guymer/PyGuymer3/actions/workflows/unittest.yaml/badge.svg)

This project aims to show how much National Trust or Open Access land is nearby.

[The script](howMuchLandv1.py) rasterizes three vector datasets onto a grid of pixels covering Great Britain with each pixel containing the total area of National Trust or Open Access land within.

You may [browse the coverage report](https://guymer.github.io/hml/) for running [the unit tests](unitTests.py).

## Dependencies

HML requires the following Python modules to be installed and available in your `PYTHONPATH`.

* [cartopy](https://pypi.org/project/Cartopy/)
* [matplotlib](https://pypi.org/project/matplotlib/)
* [numpy](https://pypi.org/project/numpy/)
* [PIL](https://pypi.org/project/Pillow/)
* [pyguymer3](https://github.com/Guymer/PyGuymer3)
* [shapefile](https://pypi.org/project/pyshp/)
* [shapely](https://pypi.org/project/Shapely/)

## Notes

* Ironically enough, now that this project uses `multiprocessing` to calculate the intersections, it actually spends more time making the PNGs than the BINs.
