def findExtent(sfObj, kwArgCheck = None, x1 = 1.0e10, x2 = 0.0, y1 = 1.0e10, y2 = 0.0):
    """
    Update the supplied bounding box so that it encompasses the overall bounding
    box of the Polygons in the supplied ShapeFile.

    Arguments:
    sfObj -- a shapefile.Reader of a ShapeFile

    Keyword arguments:
    x1 -- lower x position of bounding box (default 1.0e100)
    y1 -- left y position of bounding box (default 1.0e100)
    x2 -- upper x position of bounding box (default 0.0)
    y2 -- right y position of bounding box (default 0.0)
    """

    # Import special modules ...
    try:
        import shapefile
    except:
        raise Exception("\"shapefile\" is not installed; run \"pip install --user pyshp\"") from None

    # Check keyword arguments ...
    if kwArgCheck is not None:
        print(f"WARNING: \"{__name__}\" has been called with an extra positional argument")

    # Check argument ...
    if not isinstance(sfObj, shapefile.Reader):
        raise TypeError("\"sfObj\" is not a shapefile.Reader")

    # Loop over shape+record pairs ...
    for shapeRecord in sfObj.iterShapeRecords():
        # Crash if this shape+record is not a shapefile polygon ...
        if shapeRecord.shape.shapeType != shapefile.POLYGON:
            raise Exception("\"shape\" is not a POLYGON") from None

        # Update extents ...
        x1 = min(x1, shapeRecord.shape.bbox[0])                                 # [m]
        y1 = min(y1, shapeRecord.shape.bbox[1])                                 # [m]
        x2 = max(x2, shapeRecord.shape.bbox[2])                                 # [m]
        y2 = max(y2, shapeRecord.shape.bbox[3])                                 # [m]

    # Return answer ...
    return x1, y1, x2, y2
