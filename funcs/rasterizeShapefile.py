def rasterizeShapefile(sfObj, px = 1024.0, nx = 650, ny = 650):
    """
    Rasterize a ShapeFile.

    Arguments:
    sfObj -- a shapefile.Reader of a ShapeFile

    Keyword arguments:
    px -- pixel size (default 1024.0)
    nx -- number of x pixels (default 650)
    ny -- number of y pixels (default 650)
    """

    # Import standard modules ...
    import math

    # Import special modules ...
    try:
        import numpy
    except:
        raise Exception("run \"pip install --user numpy\"")
    try:
        import shapefile
    except:
        raise Exception("run \"pip install --user pyshp\"")
    try:
        import shapely
    except:
        raise Exception("run \"pip install --user shapely\"")

    # Check argument ...
    if not isinstance(sfObj, shapefile.Reader):
        raise TypeError("\"sfObj\" is not a shapefile.Reader")

    # Initialize counter and grid ...
    n = 0                                                                       # [#]
    grid = numpy.zeros((ny, nx), dtype = numpy.float32)                         # [m2]

    # Loop over shape+record pairs ...
    for shapeRecord in sfObj.iterShapeRecords():
        # Crash if this shape+record is not a shapefile polygon ...
        if shapeRecord.shape.shapeType != shapefile.POLYGON:
            raise Exception("\"shape\" is not a POLYGON")

        # Convert shapefile.Shape to shapely.geometry.polygon.Polygon or
        # shapely.geometry.multipolygon.MultiPolygon ...
        poly = shapely.geometry.shape(shapeRecord.shape)
        if not poly.is_valid:
            n += 1                                                              # [#]
            continue

        # Find bounding pixel indices ...
        ix1 = math.floor(shapeRecord.shape.bbox[0] / px)
        iy1 = math.floor(shapeRecord.shape.bbox[1] / px)
        ix2 = math.ceil(shapeRecord.shape.bbox[2] / px)
        iy2 = math.ceil(shapeRecord.shape.bbox[3] / px)

        # Loop over x-axis ...
        for ix in range(ix1, ix2):
            # Create short-hands ...
            xmin = float(ix) * px                                               # [m]
            xmax = float(ix + 1) * px                                           # [m]

            # Loop over y-axis ...
            for iy in range(iy1, iy2):
                # Create short-hands ...
                ymin = float(iy) * px                                           # [m]
                ymax = float(iy + 1) * px                                       # [m]

                # Create a counter-clockwise polygon of the pixel, find its
                # intersection with the polygon and add the area to the total
                # grid ...
                grid[iy, ix] += poly.intersection(
                    shapely.geometry.polygon.Polygon(
                        [
                            (xmin, ymin),
                            (xmax, ymin),
                            (xmax, ymax),
                            (xmin, ymax),
                            (xmin, ymin),
                        ]
                    )
                ).area                                                          # [m2]

    print("INFO: {:,d} records were skipped because they were invalid".format(n))

    # Return answer ...
    return grid
