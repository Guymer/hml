# How Much Land (HML)

This project aims to show how much National Trust or Open Access land is nearby.

[The script](howMuchLandv1.py) rasterizes three vector datasets onto a grid of pixels covering Great Britain with each pixel containing the total area of National Trust or Open Access land within.

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
