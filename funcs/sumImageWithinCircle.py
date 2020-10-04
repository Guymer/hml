def sumImageWithinCircle(img, xmin, xmax, ymin, ymax, r, cx = 0.0, cy = 0.0, ndiv = 16):
    """
    Sum the pixel values on an image that are within a hard circular mask.

    Arguments:
    img -- 2D image with axes (ny, nx)
    xmin -- left edge of leftmost pixel
    xmax -- right edge of rightmost pixel
    ymin -- lower edge of lowermost pixel
    ymax -- upper edge of uppermost pixel
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

    # Import sub-functions ...
    from .findFractionOfPixelWithinCircle import findFractionOfPixelWithinCircle

    # Create axes relative to the centre of the circle ...
    xaxis = numpy.linspace(xmin, xmax, num = img.shape[1] + 1) - cx
    yaxis = numpy.linspace(ymin, ymax, num = img.shape[0] + 1) - cy

    # Find out the distance of each corner to the centre of the circle ...
    dist = numpy.zeros((yaxis.size, xaxis.size), dtype = numpy.float64)
    for ix in range(xaxis.size):
        for iy in range(yaxis.size):
            dist[iy, ix] = numpy.hypot(xaxis[ix], yaxis[iy])

    # Initialize total ...
    tot = 0.0

    # Loop over x-axis ...
    for ix in range(img.shape[1]):
        # Loop over y-axis ...
        for iy in range(img.shape[0]):
            # Skip this pixel if it is empty ...
            if img[iy, ix] == 0.0:
                continue

            # Skip this pixel if it is all outside of the circle ...
            if numpy.all(dist[iy:iy + 2, ix:ix + 2] >= r):
                continue

            # Check if this pixel is entirely within the circle or if it
            # straddles the circumference ...
            if numpy.all(dist[iy:iy + 2, ix:ix + 2] <= r):
                # Add all of the value to total ...
                tot += img[iy, ix]
            else:
                # Add part of the value to total ...
                tot += img[iy, ix] * findFractionOfPixelWithinCircle(xaxis[ix], xaxis[ix + 1], yaxis[iy], yaxis[iy + 1], r, ndiv = ndiv)

    # Return answer ...
    return tot
