def calcVerticalGridlines(xloc, ext):
    x = []                                                                      # [°]
    y = []                                                                      # [°]
    for yloc in range(int(round(ext[2])), int(round(ext[3])) + 1):
        x.append(xloc)                                                          # [°]
        y.append(yloc)                                                          # [°]
    return x, y
