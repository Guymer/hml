#!/usr/bin/env python3

# Define function ...
def rasterizeShapefile(sfObj, /, *, nx = 1024, ny = 1024, px = 1024.0):
    """
    Rasterize a ShapeFile.

    Arguments:
    sfObj -- a shapefile.Reader of a ShapeFile

    Keyword arguments:
    px -- pixel size (default 1024.0)
    nx -- number of x pixels (default 1024)
    ny -- number of y pixels (default 1024)

    Note:
    This function only works for ShapeFiles that solely exist in the (positive,
    positive) quadrant.
    """

    # Import standard modules ...
    import multiprocessing

    # Import special modules ...
    try:
        import numpy
    except:
        raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
    try:
        import shapefile
    except:
        raise Exception("\"shapefile\" is not installed; run \"pip install --user pyshp\"") from None
    try:
        import shapely
        import shapely.geometry
        import shapely.validation
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import sub-functions ...
    from .rasterizePolygon import rasterizePolygon

    # Check argument ...
    if not isinstance(sfObj, shapefile.Reader):
        raise TypeError("\"sfObj\" is not a shapefile.Reader")

    # Initialize counter and global grid ...
    n = 0                                                                       # [#]
    globalGrid = numpy.zeros((ny, nx), dtype = numpy.float32)                   # [m2]

    # Create a pool of workers ...
    with multiprocessing.Pool(maxtasksperchild = 1) as pObj:
        # Initialize list ...
        results = []

        # Loop over shape+record pairs ...
        for shapeRecord in sfObj.iterShapeRecords():
            # Crash if this shape+record is not a shapefile polygon ...
            if shapeRecord.shape.shapeType != shapefile.POLYGON:
                raise Exception("\"shape\" is not a POLYGON") from None

            # Convert shapefile.Shape to shapely.geometry.polygon.Polygon or
            # shapely.geometry.multipolygon.MultiPolygon ...
            poly = shapely.geometry.shape(shapeRecord.shape)
            if not poly.is_valid:
                print(f"WARNING: Skipping a shape as it is not valid ({shapely.validation.explain_validity(poly)}).")
                n += 1                                                          # [#]
                continue
            if poly.is_empty:
                n += 1                                                          # [#]
                continue

            # Add rasterization job to worker pool ...
            results.append(
                pObj.apply_async(
                    rasterizePolygon,
                    (poly,),
                    {
                        "px" : px,
                    },
                )
            )

        print(f"INFO: {n:,d} records were skipped because they were invalid")

        # Loop over results ...
        for result in results:
            # Get result ...
            ix1, iy1, localGrid = result.get()

            # Check result ...
            if not result.successful():
                raise Exception("\"multiprocessing.Pool().apply_async()\" was not successful") from None

            # Loop over x-axis ...
            for ix in range(localGrid.shape[1]):
                # Loop over y-axis ...
                for iy in range(localGrid.shape[0]):
                    # Add local grid to global grid ...
                    globalGrid[iy1 + iy, ix1 + ix] += localGrid[iy, ix]         # [m2]

        # Close the pool of worker processes and wait for all of the tasks to
        # finish ...
        # NOTE: The "__exit__()" call of the context manager for
        #       "multiprocessing.Pool()" calls "terminate()" instead of
        #       "join()", so I must manage the end of the pool of worker
        #       processes myself.
        pObj.close()
        pObj.join()

    # Return answer ...
    return globalGrid
