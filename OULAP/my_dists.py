import numpy as np
import Fred as fred
import math

# Create own Distance Measures and import from Fred-Frechet

# Discrete Frechet
def disc_frechet(x, y):
    a = fred.Curve(x)
    b = fred.Curve(y)
    dist = fred.discrete_frechet(a, b)
    return dist.value

# Discrete Dynamic Time Warping
def disc_dtw(x, y):
    a = fred.Curve(x)
    b = fred.Curve(y)
    dist = fred.discrete_dynamic_time_warping(a, b)
    return dist.value # returns DTW with p=1

# DTW with flexible p, default euclidean
def ddtw(x, y, p=2):
    n = len(x)
    m = len(y)

    # distancematrix filled with infinity
    dtw = np.full((n, m), math.inf)
    dtw[0, 0] = 0

    for i in range(n):
        for j in range(m):
            dtw[i,j] = abs(x[i] - y[j]) ** p
            if i > 0 or j > 0:
                dtw[i, j] = dtw[i,j] + min(dtw[i-1, j] if i > 0 else math.inf,
                                           dtw[i, j-1] if j > 0 else math.inf,
                                           dtw[i-1, j-1] if(i > 0 and j > 0) else math.inf
                                           )

    return (dtw[n-1, m-1])**(1/p)

# Discrete Dynamic Time Warping with traversal constraint
def window_ddtw(x, y, w=4, p=2):
    n = len(x)
    m = len(y)

    # maximal possible windowsize
    w = max(w, abs(n-m))

    # distancematrix filled with infinity
    dtw = np.full((n, m), math.inf)
    dtw[0, 0] = 0

    for i in range(0, n):
        for j in range(max(0, i-w), min(m, i+w)):
            dtw[i, j] = 0

    # all possible paths filled with zeros
    for i in range(1, n):
        for j in range(max(1, i-w), min(m, i+w)):
            cost = abs(x[i] - y[j]) ** p
            dtw[i, j] = cost + min(dtw[i-1, j],
                                   dtw[i, j-1],
                                   dtw[i-1, j-1]
                                   )

    return (dtw[n-1, m-1]) ** (1/p)

# Discrete Frechet with traversal constraint, other variant than w-DTW with zero columns better
# for viz the warpint_path
def window_disc_frechet(x, y, w=4, p=2):
    n = len(x)
    m = len(y)

    # maximal possible windowsize
    w = max(w, abs(n-m))

    # distancematrix filled with infinity
    dtw = np.full((n, m), math.inf)
    dtw[0, 0] = 0

    for i in range(0, n):
        for j in range(max(0, i-w), min(m, i+w)):
            dtw[i, j] = 0

    # all possible paths filled with zeros
    for i in range(n):
        for j in range(max(0, i-w), min(m, i+w)):
            dtw[i, j] = abs(x[i] - y[j]) ** p
            if i >0 or j >0:
                dtw[i, j] = max(dtw[i, j],  min(dtw[i-1, j] if i > 0 else math.inf,
                                            dtw[i, j-1] if j > 0 else math.inf,
                                            dtw[i-1, j-1] if (i > 0 and j > 0) else math.inf
                                            )
                                )

    return (dtw[n-1, m-1]) ** (1/p)

# Discrete Frechet with traversal constraint
def window_disc_frechet2(x, y, w=4):
    n = len(x)
    m = len(y)

    # maximal possible windowsize
    w = max(w, abs(n-m))

    # distancematrix filled with infinity
    dfre = np.full((n, m), math.inf)
    dfre[0, 0] = 0

    # all possible paths filled with zeros
    for i in range(1, n):
        for j in range(max(1, i-w), min(m, i+w)):
            cost = abs(x[i] - y[j])
            dfre[i, j] = max(cost, min(dfre[i-1, j],
                                       dfre[i, j-1],
                                       dfre[i-1, j-1]))

    return dfre[n-1, m-1]

# k-greatest-distances-Mahnhattandistanz
def k_greatest_manhattan(x, y, w=6):
    dists = np.abs(x - y)
    return np.sum(np.sort(dists)[-w:][::-1])

# Earth mover's distance
from scipy.stats import wasserstein_distance

def emd(u, v):
    # create bin-vectors
    bin_u = [i for i in range(0, len(u))]
    bin_v = [i for i in range(0, len(v))]

    # normalize input vectors to unit-vectors
    u_norm = u / np.linalg.norm(u, ord=1)
    v_norm = v / np.linalg.norm(v, ord=1)

    return wasserstein_distance(bin_u, bin_v, u_norm, v_norm)
