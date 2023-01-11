## Implementation of the greedy Algorithm by Gonzalez (1985)

import numpy as np
import math
from scipy.spatial import distance

def greedygonzalez(data, k, method = 'max'):
    centers = []
    cluster_idx = []
    cluster_idx.append(np.random.randit(o, len(data) - 1))
    centers.append(data[cluster_idx][0])

    while len(centers) != k:
        if method == 'max':
            centers.append(max_dist(data, centers))
    return centers

def max_dist(data, centers):
    distances = np.zeros(len(data))

    for center_id, center in enumerate(centers):
        for curve_id, curve in enumerate(data):
            if distance.euclidean(curve, center) == 0:
                distances[curve_id] = -math.inf
            if not math.isinf(distances[curve_id]):
                distances[curve_id] = distances[curve_id] + distance.euclidean(curve, center)

    return data[np.argmax(distances)

                

