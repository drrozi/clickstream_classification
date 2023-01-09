import numpy as np
import Fred as fred
import math

# Create own Distance Measures and import from Fred-Frechet

def trafre(x, y):
    return max(abs(x - y))


def disc_frechet(x, y):
    a = fred.Curve(x)
    b = fred.Curve(y)
    dist = fred.discrete_frechet(a, b)
    return dist.value

def disc_dtw(x, y):
    a = fred.Curve(x)
    b = fred.Curve(y)
    dist = fred.discrete_dynamic_time_warping(a, b)
    return dist.value

def window_ddtw(x, y, w):
    n = len(x)
    m = len(y)

    # maximal possible windowsize
    w = max(w, abs(n-m))

    # distancematrix filled with infinity
    dtw = np.full((n, m), math.inf)
    dtw[0, 0] = 0

    # all possible paths filled with zeros
    for i in range(1, n):
        for j in range(max(1, i-w), min(m, i+w)):
            cost = abs(x[i] - y[j])
            dtw[i, j] = cost + min(dtw[i-1, j],
                                   dtw[i, j-1],
                                   dtw[i-1, j-1])

    return dtw[n-1, m-1]

def tradtw(x, y, w):
    return sum((abs(x-y))[:w])


