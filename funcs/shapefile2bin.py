def shapefile2bin(sfObj, px = 32.0, nx = 21000, ny = 21000):
    """
    Rasterize a ShapeFile.

    Arguments:
    sfObj -- a shapefile.Reader of a ShapeFile

    Keyword arguments:
    px -- pixel size (default 32.0)
    nx -- number of x pixels (default 21000)
    ny -- number of y pixels (default 21000)
    """

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

    # **************************************************************************
    # *                    STEP 1: CREATE LIST OF POLYGONS                     *
    # **************************************************************************

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

        print(poly)

    print("      INFO: {:,d} records were skipped because they were invalid".format(n))
