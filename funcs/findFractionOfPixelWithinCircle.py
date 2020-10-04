def findFractionOfPixelWithinCircle(xmin, xmax, ymin, ymax, r, cx = 0.0, cy = 0.0, ndiv = 16):
    """
    Find the fraction of a pixel that is within a hard circular mask.

    Arguments:
    xmin -- left edge
    xmax -- right edge
    ymin -- lower edge
    ymax -- upper edge
    r -- radius of circle

    Keyword arguments:
    cx -- x position of centre of circle (default 0.0)
    cy -- y position of centre of circle (default 0.0)
    ndiv -- number sub-divisions (default 16)

    Note:
    This function is crying out for FORTRAN+OpenMP.
    """

    # Import special modules ...
    try:
        import numpy
    except:
        raise Exception("run \"pip install --user numpy\"")

    # Create nodes relative to the centre of the circle ...
    xaxis = numpy.linspace(xmin, xmax, num = ndiv + 1) - cx
    yaxis = numpy.linspace(ymin, ymax, num = ndiv + 1) - cy

    # Convert the nodes to centroids ...
    # NOTE: https://stackoverflow.com/a/23856065
    xaxis = 0.5 * (xaxis[1:] + xaxis[:-1])
    yaxis = 0.5 * (yaxis[1:] + yaxis[:-1])

    # Find out the distance of each corner to the centre of the circle ...
    dist = numpy.zeros((ndiv, ndiv), dtype = numpy.float64)
    for ix in range(ndiv):
        for iy in range(ndiv):
            dist[iy, ix] = numpy.hypot(xaxis[ix], yaxis[iy])

    # Return answer ...
    return float((dist <= r).sum()) / float(ndiv * ndiv)
