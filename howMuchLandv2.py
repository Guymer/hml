#!/usr/bin/env python3

# Import standard modules ...
import csv
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

# Import my modules ...
try:
    import pyguymer3
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# ******************************************************************************

# Define function ...
def calc_horizontal_gridlines(yloc, ext):
    x = []                                                                      # [°]
    y = []                                                                      # [°]
    for xloc in range(int(round(ext[0])), int(round(ext[1])) + 1):
        x.append(xloc)                                                          # [°]
        y.append(yloc)                                                          # [°]
    return x, y

# Define function ...
def calc_vertical_gridlines(xloc, ext):
    x = []                                                                      # [°]
    y = []                                                                      # [°]
    for yloc in range(int(round(ext[2])), int(round(ext[3])) + 1):
        x.append(xloc)                                                          # [°]
        y.append(yloc)                                                          # [°]
    return x, y

# ******************************************************************************

# Start session ...
sess = pyguymer3.start_session()

# Download dataset if it is missing ...
fname = "NaPTANcsv.zip"
if not os.path.exists(fname):
    url = "https://naptan.app.dft.gov.uk/DataRequest/Naptan.ashx?format=csv"
    pyguymer3.download_file(sess, url, fname)

# Close session ...
sess.close()

# ******************************************************************************

# Initialize lists ...
easts = []                                                                      # [m]
norths = []                                                                     # [m]

# Load dataset ...
with zipfile.ZipFile("NaPTANcsv.zip", "r") as zfObj:
    # Load CSV file into RAM as a UTF-8 string and remove erroneous NULL bytes ...
    csvSrc = zfObj.read("StopAreas.csv").decode("utf-8").replace("\x00", "")

    # Loop over rows ...
    for row in csv.DictReader(csvSrc.splitlines()):
        # Skip row if it is not a railway station ...
        # NOTE: http://naptan.dft.gov.uk/naptan/stopTypes.htm
        if row["StopAreaType"] != "GRLS":
            continue

        # Append easting and northing to lists ...
        easts.append(int(row["Easting"]))                                       # [m]
        norths.append(int(row["Northing"]))                                     # [m]

# Convert eastings and northings to longitudes and latitudes ...
lons, lats = convertbng.util.convert_lonlat(easts, norths)                      # [°], [°]

# ******************************************************************************

# Define bounding box ...
xmin, xmax, ymin, ymax = -8.5, 2.5, 49.5, 56.0                                  # [°], [°], [°], [°]
extent = [xmin, xmax, ymin, ymax]                                               # [°], [°], [°], [°]

# ******************************************************************************

# Create figure ...
fg = matplotlib.pyplot.figure(figsize = (9, 6), dpi = 300)
ax = matplotlib.pyplot.axes(projection = cartopy.crs.PlateCarree())
ax.set_extent(extent)
ax.set_title("NT & OA Land With Railway Stations")
pyguymer3.add_map_background(ax, resolution = "large4096px")
ax.coastlines(resolution = "10m", color = "white", linewidth = 0.5)

# Add grid lines manually ...
for loc in range(math.ceil(xmin), math.floor(xmax) + 1):
    xlocs, ylocs = calc_vertical_gridlines(loc, extent)                         # [°], [°], [°], [°]
    ax.plot(xlocs, ylocs, transform = cartopy.crs.PlateCarree(), color = "white", linewidth = 0.5, linestyle = ":")
for loc in range(math.ceil(ymin), math.floor(ymax) + 1):
    xlocs, ylocs = calc_horizontal_gridlines(loc, extent)                       # [°], [°], [°], [°]
    ax.plot(xlocs, ylocs, transform = cartopy.crs.PlateCarree(), color = "white", linewidth = 0.5, linestyle = ":")

# Plot railway stations ...
ax.scatter(lons, lats, s = 1.0, transform = cartopy.crs.PlateCarree(), color = "cyan", marker = "o")

# Draw background image ...
# NOTE: "merged.png" is an indexed PNG and for some reason it is loaded with an
#       alpha channel. This causes MatPlotLib to replace the entire background
#       image with black. To avoid such behaviour I only use the first 3
#       channels.
ax.imshow(
    matplotlib.pyplot.imread("merged.png")[:, :, :3],
    extent = [0.0, 128.0 * 5200.0, 0.0, 128.0 * 5200.0],
    interpolation = "bicubic",
    origin = "upper",
    transform = cartopy.crs.OSGB()
)

# Save figure ...
fg.savefig("howMuchLandv2_plot1.png", bbox_inches = "tight", dpi = 300, pad_inches = 0.1)
pyguymer3.optimize_image("howMuchLandv2_plot1.png", strip = True)
matplotlib.pyplot.close("all")

# ******************************************************************************
