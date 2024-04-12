#!/usr/bin/env python3

# Use the proper idiom in the main module ...
# NOTE: See https://docs.python.org/3.11/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
if __name__ == "__main__":
    # Import standard modules ...
    import argparse
    import csv
    import json
    import os
    import zipfile

    # Import special modules ...
    try:
        import cartopy
        cartopy.config.update(
            {
                "cache_dir" : os.path.expanduser("~/.local/share/cartopy_cache"),
            }
        )
    except:
        raise Exception("\"cartopy\" is not installed; run \"pip install --user Cartopy\"") from None
    try:
        import matplotlib
        matplotlib.rcParams.update(
            {
                       "backend" : "Agg",                                       # NOTE: See https://matplotlib.org/stable/gallery/user_interfaces/canvasagg.html
                    "figure.dpi" : 300,
                "figure.figsize" : (9.6, 7.2),                                  # NOTE: See https://github.com/Guymer/misc/blob/main/README.md#matplotlib-figure-sizes
                     "font.size" : 8,
            }
        )
        import matplotlib.pyplot
    except:
        raise Exception("\"matplotlib\" is not installed; run \"pip install --user matplotlib\"") from None
    try:
        import numpy
    except:
        raise Exception("\"numpy\" is not installed; run \"pip install --user numpy\"") from None
    try:
        import shapely
        import shapely.geometry
    except:
        raise Exception("\"shapely\" is not installed; run \"pip install --user Shapely\"") from None

    # Import my modules ...
    import hml
    import hml.f90
    try:
        import pyguymer3
        import pyguymer3.geo
        import pyguymer3.image
    except:
        raise Exception("\"pyguymer3\" is not installed; you need to have the Python module from https://github.com/Guymer/PyGuymer3 located somewhere in your $PYTHONPATH") from None

    # **************************************************************************

    # Create argument parser and parse the arguments ...
    parser = argparse.ArgumentParser(
           allow_abbrev = False,
            description = "HML: this project aims to show how much National Trust or Open Access land is nearby.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action = "store_true",
          help = "print debug messages",
    )
    args = parser.parse_args()

    # **************************************************************************

    # Set pixel size, number of sub-divisions and extent of grid ...
    px = 128                                                                    # [m]
    ndiv = 128                                                                  # [#]
    nx = 5200                                                                   # [#]
    ny = 5200                                                                   # [#]

    # Use mode to override number of sub-divisions ...
    if args.debug:
        ndiv = 16                                                               # [#]

    # **************************************************************************

    # Start session ...
    with pyguymer3.start_session() as sess:
        # Download dataset if it is missing ...
        fname = "NaPTANcsv.zip"
        if not os.path.exists(fname):
            url = "https://naptan.app.dft.gov.uk/DataRequest/Naptan.ashx?format=csv"
            pyguymer3.download_file(sess, url, fname)

    # **************************************************************************

    # Check if the JSON database exists ...
    if os.path.exists("howMuchLandv2.json"):
        # Load database ...
        with open("howMuchLandv2.json", "rt", encoding = "utf-8") as fObj:
            data = json.load(fObj)

        # Initialize lists ...
        names = []
        easts = []                                                              # [m]
        norths = []                                                             # [m]
        lons = []                                                               # [°]
        lats = []                                                               # [°]

        # Un-merge dictionary in to lists ...
        for name, info in data.items():
            names.append(name)
            easts.append(info["easting"])                                       # [m]
            norths.append(info["northing"])                                     # [m]
            lons.append(info["longitude"])                                      # [°]
            lats.append(info["latitude"])                                       # [°]
    else:
        # Initialize lists ...
        names = []
        easts = []                                                              # [m]
        norths = []                                                             # [m]
        lons = []                                                               # [°]
        lats = []                                                               # [°]

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
                easts.append(int(row["Easting"]))                               # [m]
                norths.append(int(row["Northing"]))                             # [m]

                # Convert easting/northing to longitude/latitude ...
                pointEN = shapely.geometry.Point(easts[-1], norths[-1])
                pointLL = pyguymer3.geo.en2ll(pointEN)

                # Append longitude and latitude to lists ...
                lons.append(pointLL.x)                                          # [°]
                lats.append(pointLL.y)                                          # [°]

        # Merge lists in to a dictionary ...
        data = {}
        for name, east, north, lon, lat in zip(names, easts, norths, lons, lats, strict = True):
            data[name] = {
                  "easting" : east,                                             # [m]
                 "northing" : north,                                            # [m]
                "longitude" : lon,                                              # [°]
                 "latitude" : lat,                                              # [°]
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

    # **************************************************************************

    # Convert lists to arrays ...
    lons = numpy.array(lons)                                                    # [°]
    lats = numpy.array(lats)                                                    # [°]

    # **************************************************************************

    # Create figure ...
    fg = matplotlib.pyplot.figure(figsize = (7.2, 7.2))

    # Create axis ...
    ax = pyguymer3.geo.add_axis(
        fg,
                       dist = 340.0e3,
        gridlines_linecolor = "white",
                        lat = 52.9,
                        lon = -3.0,
    )

    # Configure axis ...
    pyguymer3.geo.add_coastlines(ax, colorName = "white")
    pyguymer3.geo.add_map_background(ax, resolution = "large8192px")

    # Plot railway stations ...
    ax.scatter(
        lons,
        lats,
            color = "cyan",
                s = 10.0,
        transform = cartopy.crs.PlateCarree(),
    )

    # Draw background image ...
    # NOTE: "merged.png" is an indexed PNG and for some reason it is loaded with
    #       an alpha channel. This causes MatPlotLib to replace the entire
    #       background image with black. To avoid such behaviour I only use the
    #       first 3 channels.
    ax.imshow(
        matplotlib.pyplot.imread("merged.png")[:, :, :3],
               extent = [0.0, 128.0 * 5200.0, 0.0, 128.0 * 5200.0],
        interpolation = "bicubic",
               origin = "upper",
            transform = cartopy.crs.OSGB(),
    )

    # Configure axis ...
    ax.set_title("NT & OA Land With Railway Stations")

    # Configure figure ...
    fg.tight_layout()

    # Save figure ...
    fg.savefig("howMuchLandv2_plot1.png")
    matplotlib.pyplot.close(fg)

    # Optimize PNG ...
    pyguymer3.image.optimize_image("howMuchLandv2_plot1.png", strip = True)

    # **************************************************************************

    # Load grid ...
    grid = numpy.fromfile("merged.bin", dtype = numpy.float32).reshape((ny, nx))# [m2]

    # Make radii ...
    radii = numpy.linspace(0.0, 50.0e3, num = 6)                                # [m]

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
            )                                                                   # [m2]

    # Save database ...
    with open("howMuchLandv2.json", "wt", encoding = "utf-8") as fObj:
        json.dump(
            data,
            fObj,
            ensure_ascii = False,
                  indent = 4,
               sort_keys = True,
        )

    # **************************************************************************

    # Load tile metadata ...
    with open("OrdnanceSurveyBackgroundImages/miniscale.json", "rt", encoding = "utf-8") as fObj:
        meta = json.load(fObj)

    # Loop over radii (except the first one) ...
    for ir in range(1, radii.size):
        # Deduce key name ...
        key = f"{round(radii[ir]):,d}m"

        print(f"Summarising for a radius of {key} ...")

        # Initialize array ...
        areas = numpy.zeros(len(names), dtype = numpy.float64)                  # [m2]

        # Loop over stations ...
        for i, name in enumerate(names):
            # Populate array ...
            areas[i] = data[name]["integrals"][key]                             # [m2]

        # Find area of circle and convert areas to percentages ...
        area = numpy.pi * pow(radii[ir], 2)                                     # [m2]
        percs = 100.0 * areas / area                                            # [%]

        # **********************************************************************

        # Find the sorted keys ...
        keys = percs.argsort()

        # Create figure ...
        fg = matplotlib.pyplot.figure()

        # Create axis ...
        ax = pyguymer3.geo.add_axis(
            fg,
            dist = 340.0e3,
             lat = 52.9,
             lon = -3.0,
        )

        # Configure axis ...
        ax.set_title("Railway Stations")

        # Plot railway stations (layering them correctly) ...
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

        # Add colour bar ...
        cb = fg.colorbar(sc, ax = ax, orientation = "vertical")

        # Configure colour bar ...
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
        fg.savefig(f"howMuchLandv2_plot2_{key}.png")
        matplotlib.pyplot.close(fg)

        # Optimize PNG ...
        pyguymer3.image.optimize_image(f"howMuchLandv2_plot2_{key}.png", strip = True)

        # **********************************************************************

        # Reverse the sorted keys ...
        keys = keys[::-1]

        # Save the Top 25 ...
        with open(f"howMuchLandv2_plot2_{key}.csv", "wt", encoding = "utf-8") as fObj:
            fObj.write("name,area [m2],area [%]\n")
            for i in range(25):
                fObj.write(f"{names[keys[i]]},{areas[keys[i]]:e},{percs[keys[i]]:e}\n")
