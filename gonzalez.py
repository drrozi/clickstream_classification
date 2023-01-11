## Implementation of the greedy Algorithm by Gonzalez (1985)

import numpy as np
import math
from scipy.spatial import distance
from my_dists import disc_dtw

def greedygonzalez(data, k, method = 'euclidean'):
    centers_idx = []
    centers_idx.append(np.random.randint(0, len(data) - 1))

    while len(centers_idx) != k:
        if method == 'euclidean':
            centers_idx.append(max_euclidean(data, centers_idx))
        if method == 'dtw':
            centers_idx.append(max_dtw(data, centers_idx))

    return centers_idx

def max_euclidean(data, centers_idx):
    distances = np.zeros(len(data))

    for center_idx in centers_idx:
        for curve_idx, curve in enumerate(data):
            if distance.euclidean(curve, data[center_idx]) == 0:
                distances[curve_idx] = -math.inf
            if not math.isinf(distances[curve_idx]):
                distances[curve_idx] = distances[curve_idx] + distance.euclidean(curve, data[center_idx])

    return np.argmax(distances)

def max_dtw(data, centers_idx):
    distances = np.zeros(len(data))

    for center_idx in centers_idx:
        for curve_idx, curve in enumerate(data):
            if disc_dtw(curve, data[center_idx]) == 0:
                distances[curve_idx] = -math.inf
            if not math.isinf(distances[curve_idx]):
                distances[curve_idx] = distances[curve_idx] + disc_dtw(curve, data[center_idx])

    return np.argmax(distances)


def gonzalez_cost(data, centers_idx, method = 'euclidean'):
    cluster_distance = np.full(len(data), np.inf)

    for curve_idx, curve in enumerate(data):
        for center_idx in centers_idx:
            if method == 'euclidean':
                dist = distance.euclidean(curve, data[center_idx])
            if method == 'dtw':
                dist = disc_dtw(curve, data[center_idx])

            if cluster_distance[curve_idx] == math.inf:
                cluster_distance[curve_idx] = dist
                continue
            if dist < cluster_distance[curve_idx]:
                cluster_distance[curve_idx] = dist
    return np.max(cluster_distance)




