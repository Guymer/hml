def calcHorizontalGridlines(yloc, ext):
    x = []                                                                      # [°]
    y = []                                                                      # [°]
    for xloc in range(int(round(ext[0])), int(round(ext[1])) + 1):
        x.append(xloc)                                                          # [°]
        y.append(yloc)                                                          # [°]
    return x, y
