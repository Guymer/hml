#!/usr/bin/env python3

# Import standard modules ...
import csv
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
    import matplotlib
    matplotlib.use("Agg")                                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
    import matplotlib.pyplot
    matplotlib.pyplot.rcParams.update({"font.size" : 8})
except:
    raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
try:
    import numpy
except:
    raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None

# Import my modules ...
import hml
import hml.f90
try:
    import pyguymer3
    import pyguymer3.geo
    import pyguymer3.image
except:
    raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

# ******************************************************************************

# Set resolution, pixel size, number of sub-divisions and extent of grid ...
dpi = 300                                                                       # [px/in]
px = 128                                                                        # [m]
ndiv = 128                                                                      # [#]
nx = 5200                                                                       # [#]
ny = 5200                                                                       # [#]

# Set mode and use it to override resolution and number of sub-divisions ...
debug = False
if debug:
    dpi = 150                                                                   # [px/in]
    ndiv = 16                                                                   # [#]

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

# Check if the JSON database exists ...
if os.path.exists("howMuchLandv2.json"):
    # Load database ...
    with open("howMuchLandv2.json", "rt", encoding = "utf-8") as fObj:
        data = json.load(fObj)

    # Initialize lists ...
    names = []
    easts = []                                                                  # [m]
    norths = []                                                                 # [m]
    lons = []                                                                   # [°]
    lats = []                                                                   # [°]

    # Un-merge dictionary in to lists ...
    for name, info in data.items():
        names.append(name)
        easts.append(info["easting"])                                           # [m]
        norths.append(info["northing"])                                         # [m]
        lons.append(info["longitude"])                                          # [°]
        lats.append(info["latitude"])                                           # [°]
else:
    # Initialize lists ...
    names = []
    easts = []                                                                  # [m]
    norths = []                                                                 # [m]
    lons = []                                                                   # [°]
    lats = []                                                                   # [°]

    # Load dataset ...
    with zipfile.ZipFile("NaPTANcsv.zip", "r") as zfObj:
        # Load CSV file into RAM as a UTF-8 string and remove erroneous NULL
        # bytes ...
        csvSrc = zfObj.read("StopAreas.csv").decode("utf-8").replace("\x00", " ").strip()

        # Loop over rows ...
        for row in csv.DictReader(csvSrc.splitlines()):
            # Skip row if it is not a railway station ...
            # NOTE: http://naptan.dft.gov.uk/naptan/stopTypes.htm
            if row["StopAreaType"] != "GRLS":
                continue

            # Append easting and northing to lists ...
            names.append(row["Name"])
            easts.append(int(row["Easting"]))                                   # [m]
            norths.append(int(row["Northing"]))                                 # [m]

            # Append longitude and latitude to lists ...
            lon, lat = pyguymer3.geo._en2ll(int(row["Easting"]), int(row["Northing"]))  # [°], [°]
            lons.append(lon)                                                    # [°]
            lats.append(lat)                                                    # [°]

    # Merge lists in to a dictionary ...
    data = {}
    for name, east, north, lon, lat in zip(names, easts, norths, lons, lats):
        data[name] = {
            "easting" : east,                                                   # [m]
            "northing" : north,                                                 # [m]
            "longitude" : lon,                                                  # [°]
            "latitude" : lat,                                                   # [°]
        }

    # Save database ...
    with open("howMuchLandv2.json", "wt", encoding = "utf-8") as fObj:
        json.dump(
            data,
            fObj,
            ensure_ascii = False,
                  indent = 4,
               sort_keys = True,
        )

# ******************************************************************************

# Convert lists to arrays ...
lons = numpy.array(lons)                                                        # [°]
lats = numpy.array(lats)                                                        # [°]

# Define bounding box (for the first plot) ...
xmin, xmax, ymin, ymax = -8.5, 2.5, 49.5, 56.0                                  # [°], [°], [°], [°]
extent1 = [xmin, xmax, ymin, ymax]                                              # [°]

# Define bounding box (for the second plots) ...
midx, midy = -2.0, 52.5                                                         # [°], [°]
extent2 = [midx - 3.75, midx + 3.75, midy - 2.5, midy + 2.5]                    # [°]

# ******************************************************************************

# Create figure ...
fg = matplotlib.pyplot.figure(
        dpi = dpi,
    figsize = (9, 9),
)

# Create axis ...
ax = fg.add_subplot(
    projection = cartopy.crs.Orthographic(
        central_longitude = 0.5 * (xmin + xmax),
         central_latitude = 0.5 * (ymin + ymax),
    ),
)

# Configure axis ...
ax.coastlines(
         color = "white",
     linewidth = 0.5,
    resolution = "10m",
)
ax.set_extent(extent1)
ax.set_title("NT & OA Land With Railway Stations")
pyguymer3.geo.add_map_background(ax, resolution = "large8192px")

# Add grid lines manually ...
for loc in range(math.ceil(xmin), math.floor(xmax) + 1):
    xlocs, ylocs = hml.calcVerticalGridlines(loc, extent1)                      # [°], [°]
    ax.plot(
        xlocs,
        ylocs,
            color = "white",
        linestyle = ":",
        linewidth = 0.5,
        transform = cartopy.crs.PlateCarree(),
    )
for loc in range(math.ceil(ymin), math.floor(ymax) + 1):
    xlocs, ylocs = hml.calcHorizontalGridlines(loc, extent1)                    # [°], [°]
    ax.plot(
        xlocs,
        ylocs,
            color = "white",
        linestyle = ":",
        linewidth = 0.5,
        transform = cartopy.crs.PlateCarree(),
    )

# Plot railway stations ...
ax.scatter(
    lons,
    lats,
        color = "cyan",
            s = 10.0,
    transform = cartopy.crs.PlateCarree(),
)

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
        transform = cartopy.crs.OSGB(),
)

# Configure figure ...
fg.tight_layout()

# Save figure ...
fg.savefig(
    "howMuchLandv2_plot1.png",
           dpi = dpi,
    pad_inches = 0.1,
)
matplotlib.pyplot.close(fg)

# Optimize PNG ...
pyguymer3.image.optimize_image("howMuchLandv2_plot1.png", strip = True)

# ******************************************************************************

# Load grid ...
grid = numpy.fromfile("merged.bin", dtype = numpy.float32).reshape((ny, nx))    # [m2]

# Make radii ...
radii = numpy.linspace(0.0, 50.0e3, num = 6)                                    # [m]

# Loop over stations ...
for name in names:
    print(f"Integrating around \"{name}\" ...")

    # Initialize dictionary ...
    if "integrals" not in data[name]:
        data[name]["integrals"] = {}

    # Loop over radii (except the first one) ...
    for ir in range(1, radii.size):
        # Deduce key name and skip if it already exists ...
        key = f"{round(radii[ir]):,d}m"
        if key in data[name]["integrals"]:
            continue

        print(f" > {key} ...")

        # Find out how much open land there is within this circle ...
        data[name]["integrals"][key] = hml.f90.funcs.sumimagewithincircle(
              cx = float(data[name]["easting"]),
              cy = float(data[name]["northing"]),
             img = grid,
            ndiv = ndiv,
               r = radii[ir],
            xmax = float(nx * px),
            xmin = 0.0,
            ymax = float(ny * px),
            ymin = 0.0,
        )                                                                       # [m2]

# Save database ...
with open("howMuchLandv2.json", "wt", encoding = "utf-8") as fObj:
    json.dump(
        data,
        fObj,
        ensure_ascii = False,
              indent = 4,
           sort_keys = True,
    )

# ******************************************************************************

# Load tile metadata ...
with open("OrdnanceSurveyBackgroundImages/miniscale.json", "rt", encoding = "utf-8") as fObj:
    meta = json.load(fObj)

# Loop over radii (except the first one) ...
for ir in range(1, radii.size):
    # Deduce key name ...
    key = f"{round(radii[ir]):,d}m"

    print(f"Summarising for a radius of {key} ...")

    # Initialize array ...
    areas = numpy.zeros(len(names), dtype = numpy.float64)                      # [m2]

    # Loop over stations ...
    for i, name in enumerate(names):
        # Populate array ...
        areas[i] = data[name]["integrals"][key]                                 # [m2]

    # Find area of circle and convert areas to percentages ...
    area = numpy.pi * (radii[ir] ** 2)                                          # [m2]
    percs = 100.0 * areas / area                                                # [%]

    # **************************************************************************

    # Find the sorted keys ...
    keys = percs.argsort()

    # Create figure ...
    fg = matplotlib.pyplot.figure(
            dpi = dpi,
        figsize = (9, 9),
    )

    # Create axis ...
    ax = fg.add_subplot(
        projection = cartopy.crs.Orthographic(
            central_longitude = midx,
             central_latitude = midy,
        ),
    )

    # Configure axis ...
    ax.set_extent(extent2)
    ax.set_title("Railway Stations")

    # Plot railway stations (layering them correctly) and add colour bar ...
    sc = ax.scatter(
        lons[keys],
        lats[keys],
                 c = percs[keys],
              cmap = matplotlib.pyplot.cm.rainbow,
        edgecolors = "black",
         linewidth = 0.1,
                 s = 10.0,
         transform = cartopy.crs.PlateCarree(),
              vmax = 70.0,
              vmin = 0.0,
    )
    cb = fg.colorbar(sc)
    cb.set_label(f"NT & OA Land Within {key} [%]")

    # Draw background image ...
    ax.imshow(
        matplotlib.pyplot.imread(f'OrdnanceSurveyBackgroundImages/{meta["MiniScale_(mono)_R22"]["greyscale"]}'),
                 cmap = "gray",
               extent = meta["MiniScale_(mono)_R22"]["extent"],
        interpolation = "bicubic",
               origin = "upper",
            transform = cartopy.crs.OSGB(),
                 vmax = 1.0,
                 vmin = 0.0,
    )

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig(
        f"howMuchLandv2_plot2_{key}.png",
               dpi = dpi,
        pad_inches = 0.1,
    )
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image(f"howMuchLandv2_plot2_{key}.png", strip = True)

    # **************************************************************************

    # Reverse the sorted keys ...
    keys = keys[::-1]

    # Save the Top 25 ...
    with open(f"howMuchLandv2_plot2_{key}.csv", "wt", encoding = "utf-8") as fObj:
        fObj.write("name,area [m2],area [%]\n")
        for i in range(25):
            fObj.write(f"{names[keys[i]]},{areas[keys[i]]:e},{percs[keys[i]]:e}\n")
