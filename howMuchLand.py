#!/usr/bin/env python3

# Import standard modules ...
import copy
import glob
import io
import json
import math
import os
import zipfile

# Import special modules ...
try:
    import cartopy
    import cartopy.crs
except:
    raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
try:
    import convertbng
    import convertbng.util
except:
    raise Exception("\"convertbng\" is not installed; run \"pip install --user convertbng\"") from None
try:
    import matplotlib
    matplotlib.use("Agg")                                                       # NOTE: https://matplotlib.org/gallery/user_interfaces/canvasagg.html
    import matplotlib.pyplot
except:
    raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
try:
    import numpy
except:
    raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
try:
    import shapefile
except:
    raise Exception("\"pyshp\" is not installed; run \"pip install --user pyshp\"") from None

# Import my modules ...
import funcs
try:
    import pyguymer3
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# NOTE: This script (and the ShapeFiles that it uses) works in the OSGB
#       reference system whose coordinates are Eastings/Northings (in metres)
#       from an origin off the south west coast of Cornwall. For further details
#       see:
#         * https://scitools.org.uk/cartopy/docs/latest/crs/projections.html#osgb
#         * https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid
#         * https://commons.wikimedia.org/wiki/File:Ordnance_Survey_National_Grid.svg

# Set pixel size, number of sub-divisions, number of radii and extent of grid ...
dpi = 300                                                                       # [px/in]
px = 128                                                                        # [m]
ndiv = 128                                                                      # [#]
nr = 128                                                                        # [#]
nx = 5200                                                                       # [#]
ny = 5200                                                                       # [#]

# Set field-of-view and padding ...
fov = 0.5                                                                       # [°]
pad = 0.1                                                                       # [°]

# Set mode and use it to override pixel size, number of sub-divisions, number of
# radii and extent of grid ...
debug = False
if debug:
    dpi = 150                                                                   # [px/in]
    px = 1024                                                                   # [m]
    ndiv = 16                                                                   # [#]
    nr = 16                                                                     # [#]
    nx = 650                                                                    # [#]
    ny = 650                                                                    # [#]

# ******************************************************************************

# Check user input ...
if not isinstance(px, int):
    raise Exception("\"px\" must be an integer") from None

# Create copy of the colour map and hack the alpha values for our needs ...
# NOTE: https://stackoverflow.com/a/10127675
cmap = copy.copy(matplotlib.pyplot.get_cmap("jet"))
cmap._init()
for i in range(cmap.N):
    cmap._lut[i, 3] = float(i) / float(cmap.N - 1)

# Load tile metadata ...
meta = json.load(open("OrdnanceSurveyBackgroundImages/miniscale.json", "rt"))

# ******************************************************************************

# Start session ...
sess = pyguymer3.start_session()

# Download dataset if it is missing ...
fname = "alwaysOpen.zip"
if not os.path.exists(fname):
    url = "https://opendata.arcgis.com/datasets/202ec400dfe9471aaf257e4b6c956394_0.zip?outSR=%7B%22latestWkid%22%3A27700%2C%22wkid%22%3A27700%7D"
    pyguymer3.download_file(sess, url, fname)

# Download dataset if it is missing ...
fname = "limitedAccess.zip"
if not os.path.exists(fname):
    url = "https://opendata.arcgis.com/datasets/f3cd21fd165e4e3498a83973bb5ba82f_0.zip?outSR=%7B%22latestWkid%22%3A27700%2C%22wkid%22%3A27700%7D"
    pyguymer3.download_file(sess, url, fname)

# Download dataset if it is missing ...
fname = "openAccess.zip"
if not os.path.exists(fname):
    url = "https://opendata.arcgis.com/datasets/6ce15f2cd06c4536983d315694dad16b_0.zip?outSR=%7B%22latestWkid%22%3A27700%2C%22wkid%22%3A27700%7D"
    pyguymer3.download_file(sess, url, fname)

# Close session ...
sess.close()

# ******************************************************************************

# Initialize extents ...
x1 = 1.0e10                                                                     # [m]
y1 = 1.0e10                                                                     # [m]
x2 = 0.0                                                                        # [m]
y2 = 0.0                                                                        # [m]

# ******************************************************************************

print("Finding extent of \"alwaysOpen.zip\" ...")

# Load dataset ...
with zipfile.ZipFile("alwaysOpen.zip", "r") as zfObj:
    # Read files into RAM so that they become seekable ...
    # NOTE: https://stackoverflow.com/a/12025492
    dbfObj = io.BytesIO(zfObj.read("d00dbcdd-ca42-4b51-9889-50627184f7602020313-1-1rdxbnd.c0er.dbf"))
    shpObj = io.BytesIO(zfObj.read("d00dbcdd-ca42-4b51-9889-50627184f7602020313-1-1rdxbnd.c0er.shp"))
    shxObj = io.BytesIO(zfObj.read("d00dbcdd-ca42-4b51-9889-50627184f7602020313-1-1rdxbnd.c0er.shx"))

    # Open shapefile ...
    sfObj = shapefile.Reader(dbf = dbfObj, shp = shpObj, shx = shxObj)

    # Update extents ...
    x1, y1, x2, y2 = funcs.findExtent(sfObj, x1 = x1, y1 = y1, x2 = x2, y2 = y2)# [m], [m], [m], [m]

# ******************************************************************************

print("Finding extent of \"limitedAccess.zip\" ...")

# Load dataset ...
with zipfile.ZipFile("limitedAccess.zip", "r") as zfObj:
    # Read files into RAM so that they become seekable ...
    # NOTE: https://stackoverflow.com/a/12025492
    dbfObj = io.BytesIO(zfObj.read("9a97e056-3bd9-4817-a9c5-ad7de1f31a1d2020313-1-rlrdj0.1jac.dbf"))
    shpObj = io.BytesIO(zfObj.read("9a97e056-3bd9-4817-a9c5-ad7de1f31a1d2020313-1-rlrdj0.1jac.shp"))
    shxObj = io.BytesIO(zfObj.read("9a97e056-3bd9-4817-a9c5-ad7de1f31a1d2020313-1-rlrdj0.1jac.shx"))

    # Open shapefile ...
    sfObj = shapefile.Reader(dbf = dbfObj, shp = shpObj, shx = shxObj)

    # Update extents ...
    x1, y1, x2, y2 = funcs.findExtent(sfObj, x1 = x1, y1 = y1, x2 = x2, y2 = y2)# [m], [m], [m], [m]

# ******************************************************************************

print("Finding extent of \"openAccess.zip\" ...")

# Load dataset ...
with zipfile.ZipFile("openAccess.zip", "r") as zfObj:
    # Read files into RAM so that they become seekable ...
    # NOTE: https://stackoverflow.com/a/12025492
    dbfObj = io.BytesIO(zfObj.read("CRoW_Access_Land___Natural_England.dbf"))
    shpObj = io.BytesIO(zfObj.read("CRoW_Access_Land___Natural_England.shp"))
    shxObj = io.BytesIO(zfObj.read("CRoW_Access_Land___Natural_England.shx"))

    # Open shapefile ...
    sfObj = shapefile.Reader(dbf = dbfObj, shp = shpObj, shx = shxObj)

    # Update extents ...
    x1, y1, x2, y2 = funcs.findExtent(sfObj, x1 = x1, y1 = y1, x2 = x2, y2 = y2)# [m], [m], [m], [m]

# ******************************************************************************

print("The overall extent of the three datasets is:")
print("    lower-left corner = ( {:,.1f}m , {:,.1f}m )".format(x1, y1))
print("    upper-right corner = ( {:,.1f}m , {:,.1f}m )".format(x2, y2))
print("    ∴ width = {:,.1f}m".format(x2 - x1))
print("    ∴ height = {:,.1f}m".format(y2 - y1))
print("I have chosen my pixels to be {:,d}m x {:,d}m as float32 values.".format(px, px))
print("    ∴ nx needs to be >= {:,d} (I have chosen {:,d})".format(math.ceil(x2 / float(px)), nx))
print("    ∴ ny needs to be >= {:,d} (I have chosen {:,d})".format(math.ceil(y2 / float(px)), ny))
print("    ∴ each raster will be {:,.1f}MiB".format(nx * ny * 4.0 / (1024.0 * 1024.0)))

# ******************************************************************************

# Check if the ZIP file needs rasterizing ...
if not os.path.exists("alwaysOpen.bin"):
    print("Rasterizing \"alwaysOpen.zip\" ...")

    # Load dataset ...
    with zipfile.ZipFile("alwaysOpen.zip", "r") as zfObj:
        # Read files into RAM so that they become seekable ...
        # NOTE: https://stackoverflow.com/a/12025492
        dbfObj = io.BytesIO(zfObj.read("d00dbcdd-ca42-4b51-9889-50627184f7602020313-1-1rdxbnd.c0er.dbf"))
        shpObj = io.BytesIO(zfObj.read("d00dbcdd-ca42-4b51-9889-50627184f7602020313-1-1rdxbnd.c0er.shp"))
        shxObj = io.BytesIO(zfObj.read("d00dbcdd-ca42-4b51-9889-50627184f7602020313-1-1rdxbnd.c0er.shx"))

        # Open shapefile ...
        sfObj = shapefile.Reader(dbf = dbfObj, shp = shpObj, shx = shxObj)

        # Rasterize and save to BIN ...
        grid = funcs.rasterizeShapefile(sfObj, px = float(px), nx = nx, ny = ny)
        grid.tofile("alwaysOpen.bin")

# ******************************************************************************

# Check if the ZIP file needs rasterizing ...
if not os.path.exists("limitedAccess.bin"):
    print("Rasterizing \"limitedAccess.zip\" ...")

    # Load dataset ...
    with zipfile.ZipFile("limitedAccess.zip", "r") as zfObj:
        # Read files into RAM so that they become seekable ...
        # NOTE: https://stackoverflow.com/a/12025492
        dbfObj = io.BytesIO(zfObj.read("9a97e056-3bd9-4817-a9c5-ad7de1f31a1d2020313-1-rlrdj0.1jac.dbf"))
        shpObj = io.BytesIO(zfObj.read("9a97e056-3bd9-4817-a9c5-ad7de1f31a1d2020313-1-rlrdj0.1jac.shp"))
        shxObj = io.BytesIO(zfObj.read("9a97e056-3bd9-4817-a9c5-ad7de1f31a1d2020313-1-rlrdj0.1jac.shx"))

        # Open shapefile ...
        sfObj = shapefile.Reader(dbf = dbfObj, shp = shpObj, shx = shxObj)

        # Rasterize and save to BIN ...
        grid = funcs.rasterizeShapefile(sfObj, px = float(px), nx = nx, ny = ny)
        grid.tofile("limitedAccess.bin")

# ******************************************************************************

# Check if the ZIP file needs rasterizing ...
if not os.path.exists("openAccess.bin"):
    print("Rasterizing \"openAccess.zip\" ...")

    # Load dataset ...
    with zipfile.ZipFile("openAccess.zip", "r") as zfObj:
        # Read files into RAM so that they become seekable ...
        # NOTE: https://stackoverflow.com/a/12025492
        dbfObj = io.BytesIO(zfObj.read("CRoW_Access_Land___Natural_England.dbf"))
        shpObj = io.BytesIO(zfObj.read("CRoW_Access_Land___Natural_England.shp"))
        shxObj = io.BytesIO(zfObj.read("CRoW_Access_Land___Natural_England.shx"))

        # Open shapefile ...
        sfObj = shapefile.Reader(dbf = dbfObj, shp = shpObj, shx = shxObj)

        # Rasterize and save to BIN ...
        grid = funcs.rasterizeShapefile(sfObj, px = float(px), nx = nx, ny = ny)
        grid.tofile("openAccess.bin")

# ******************************************************************************

# Check if the rasters needs merging ...
if not os.path.exists("merged.bin"):
    print("Merging rasters ...")

    # Load all three rasters, add them together and save to BIN ...
    # NOTE: I do not need to .reshape() them here as the total is being saved
    #       back to the disk immediately.
    (
        numpy.fromfile("alwaysOpen.bin", dtype = numpy.float32) +
        numpy.fromfile("limitedAccess.bin", dtype = numpy.float32) +
        numpy.fromfile("openAccess.bin", dtype = numpy.float32)
    ).tofile("merged.bin")

# ******************************************************************************

# Loop over BINs ...
for bname in sorted(glob.glob("*.bin")):
    # Deduce PNG name and skip this BIN if the PNG already exists ...
    iname = bname[:-4] + ".png"
    if os.path.exists(iname):
        continue

    print("Making \"{:s}\" ...".format(iname))

    # Load BIN, flip it, scale it correctly and save as PNG ...
    # NOTE: The OSGB reference system has positive axes from an origin in the
    #       lower-left corner whereas the PNG reference system has positive axes
    #       from an origin in the upper-left corner. Therefore, the y-axis needs
    #       flipping before the BIN can be saved as a PNG.
    grid = numpy.fromfile(bname, dtype = numpy.float32).reshape((ny, nx))       # [m2]
    grid = numpy.flip(grid, axis = 0)                                           # [m2]
    grid /= float(px * px)                                                      # [fraction]
    grid *= 255.0                                                               # [colour level]
    numpy.place(grid, grid > 255.0, 255.0)                                      # [colour level]
    numpy.place(grid, grid <   0.0,   0.0)                                      # [colour level]
    pyguymer3.save_array_as_image(grid, iname, ct = "rainbow")

# ******************************************************************************

# Define locations ...
locs = [
    (51.268, -1.088, "Basingstoke Train Station", "basingstoke"),               # [°], [°]
    (51.459, -0.974, "Reading Train Station"    , "reading"    ),               # [°], [°]
    (53.378, -1.462, "Sheffield Train Station"  , "sheffield"  ),               # [°], [°]
    (54.379, -2.905, "Windermere Train Station" , "windermere" ),               # [°], [°]
    (54.779, -1.583, "Durham Train Station"     , "durham"     ),               # [°], [°]
]

# Load grid ...
grid = numpy.fromfile("merged.bin", dtype = numpy.float32).reshape((ny, nx))    # [m2]

# ******************************************************************************

# Loop over locations ...
for lat, lon, title, stub in locs:
    # Skip this plot if it already exists ...
    if os.path.exists(stub + ".png"):
        continue

    print("Making \"{:s}.png\" ...".format(stub))

    # Define bounding box ...
    xmin, xmax, ymin, ymax = lon - fov, lon + fov, lat - fov, lat + fov         # [°], [°], [°], [°]

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = dpi)
    ax = matplotlib.pyplot.axes(projection = cartopy.crs.PlateCarree())
    ax.set_extent([xmin, xmax, ymin, ymax])
    ax.set_title("NT & OA Land Nearby ({:s})".format(title))
    if debug:
        ax.coastlines(resolution = "110m", color = "black", linewidth = 0.1)
    else:
        ax.coastlines(resolution = "10m", color = "black", linewidth = 0.1)

    # Draw background image ...
    ax.imshow(
        matplotlib.pyplot.imread("OrdnanceSurveyBackgroundImages/" + meta["MiniScale_(mono)_R22"]["greyscale"]),
        cmap = "gray",
        extent = meta["MiniScale_(relief1)_R22"]["extent"],
        interpolation = "bicubic",
        origin = "upper",
        transform = cartopy.crs.OSGB(),
        vmin = 0.0,
        vmax = 1.0
    )

    # Draw data ...
    ax.imshow(
        grid,
        cmap = cmap,
        extent = [0.0, nx * px, 0.0, ny * px],
        interpolation = "bicubic",
        origin = "lower",
        transform = cartopy.crs.OSGB(),
        vmin = 0.0,
        vmax = float(px * px)
    )

    # Save figure ...
    fg.savefig(stub + ".png", bbox_inches = "tight", dpi = dpi, pad_inches = 0.1)
    if not debug:
        pyguymer3.optimize_image(stub + ".png", strip = True)
    matplotlib.pyplot.close("all")

    # Stop looping if debugging ...
    if debug:
        break

# ******************************************************************************

# Make radii ...
radii = numpy.linspace(0.0, 100.0e3, num = nr)                                  # [m]

# Loop over locations ...
for lat, lon, title, stub in locs:
    # Skip this CSV if it already exists ...
    if os.path.exists(stub + ".csv"):
        continue

    print("Making \"{:s}.csv\" ...".format(stub))

    # Convert longitude/latitude to easting/northing ...
    x, y = convertbng.util.convert_bng(lon, lat)                                # [m], [m]

    # Open output file ...
    with open(stub + ".csv", "wt") as fobj:
        # Write header ...
        fobj.write("radius [m],open area [m2]\n")

        # Loop over radii (except the first one) ...
        for ir in range(1, nr):
            # Find out how much open land there is within this circle and save
            # it to the CSV ...
            fobj.write(
                "{:e},{:e}\n".format(
                    radii[ir],
                    funcs.sumImageWithinCircle(grid, 0.0, nx * px, 0.0, ny * px, radii[ir], cx = x[0], cy = y[0], ndiv = ndiv),
                )
            )

# ******************************************************************************

# Create figure ...
fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = dpi)
ax = matplotlib.pyplot.subplot()

# Loop over locations ...
for lat, lon, title, stub in locs:
    # Plot data ...
    x, y = numpy.loadtxt(stub + ".csv", delimiter = ",", skiprows = 1, unpack = True)   # [m], [m2]
    ax.plot(x / 1.0e3, y / 1.0e6, label = title)

# Plot theoretical maximum ...
ax.plot(radii / 1.0e3, numpy.pi * pow(radii, 2) / 1.0e6, label = "(theoretical maximum)", linestyle = ":")

# Save figure ...
ax.grid(True)
ax.legend(fontsize = "small", loc = "upper left")
ax.set_title("How much National Trust or Open Access land is nearby?")
ax.set_xlabel("Radius [km]")
ax.set_xlim(radii[0], radii[-1] / 1.0e3)
ax.set_ylabel("Area [km2]")
ax.set_ylim(0.0, 6.0e3)
fg.savefig("howMuchLand.png", bbox_inches = "tight", dpi = dpi, pad_inches = 0.1)
if not debug:
    pyguymer3.optimize_image("howMuchLand.png", strip = True)
matplotlib.pyplot.close("all")

# ******************************************************************************

# Create figure ...
fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = dpi)
ax = matplotlib.pyplot.subplot()

# Loop over locations ...
for lat, lon, title, stub in locs:
    # Plot data ...
    x, y = numpy.loadtxt(stub + ".csv", delimiter = ",", skiprows = 1, unpack = True)   # [m], [m2]
    ax.plot(x / 1.0e3, 100.0 * y / (numpy.pi * pow(x, 2)), label = title)

# Save figure ...
ax.grid(True)
ax.legend(fontsize = "small", loc = "upper left")
ax.set_title("How much National Trust or Open Access land is nearby?")
ax.set_xlabel("Radius [km]")
ax.set_xlim(radii[0], radii[-1] / 1.0e3)
ax.set_ylabel("Area [%]")
ax.set_ylim(0.0, 100.0)
fg.savefig("howMuchLand2.png", bbox_inches = "tight", dpi = dpi, pad_inches = 0.1)
if not debug:
    pyguymer3.optimize_image("howMuchLand2.png", strip = True)
matplotlib.pyplot.close("all")