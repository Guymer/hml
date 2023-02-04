#!/usr/bin/env python3

# Define function ...
def rasterizePolygon(poly, /, *, px = 1024.0):
    """
    Rasterize a [Multi]Polygon.

    Arguments:
    poly -- a shapely.geometry.[multi]polygon.[Multi]Polygon

    Keyword arguments:
    px -- pixel size (default 1024.0)

    Note:
    This function only works for [Multi]Polygons that solely exist in the
    (positive, positive) quadrant.
    """

    # Import standard modules ...
    import math

    # Import special modules ...
    try:
        import numpy
    except:
        raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
    try:
        import shapely
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Check argument ...
    if not isinstance(poly, shapely.geometry.polygon.Polygon):
        if not isinstance(poly, shapely.geometry.multipolygon.MultiPolygon):
            raise TypeError("\"poly\" is not a shapely.geometry.[multi]polygon.[Multi]Polygon")

    # Find bounding pixel indices in the global grid ...
    ix1 = math.floor(poly.bounds[0] / px)
    iy1 = math.floor(poly.bounds[1] / px)
    ix2 = math.ceil(poly.bounds[2] / px)
    iy2 = math.ceil(poly.bounds[3] / px)

    # Find extent of the local grid ...
    nx = ix2 - ix1
    ny = iy2 - iy1

    # Initialize local grid ...
    localGrid = numpy.zeros((ny, nx), dtype = numpy.float32)                    # [m2]

    # Loop over x-axis ...
    for ix in range(nx):
        # Create short-hands ...
        xmin = float(ix1 + ix) * px                                             # [m]
        xmax = float(ix1 + ix + 1) * px                                         # [m]

        # Loop over y-axis ...
        for iy in range(ny):
            # Create short-hands ...
            ymin = float(iy1 + iy) * px                                         # [m]
            ymax = float(iy1 + iy + 1) * px                                     # [m]

            # Create a counter-clockwise polygon of the pixel, find its
            # intersection with the [Multi]Polygon and add the area to the local
            # grid ...
            localGrid[iy, ix] += poly.intersection(
                shapely.geometry.polygon.Polygon(
                    [
                        (xmin, ymin),
                        (xmax, ymin),
                        (xmax, ymax),
                        (xmin, ymax),
                        (xmin, ymin),
                    ]
                )
            ).area                                                              # [m2]

    # Return answer ...
    return ix1, iy1, localGrid
