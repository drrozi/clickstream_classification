## Implementation of the greedy Algorithm by Gonzalez (1985)

import numpy as np
import math
from scipy.spatial import distance
from my_dists import disc_dtw, window_ddtw
from dtaidistance.dtw import distance_matrix

def greedygonzalez(data, k, method = 'euclidean'):
    centers_idx = []
    centers_idx.append(np.random.randint(0, len(data) - 1))

    while len(centers_idx) != k:
        if method == 'euclidean':
            centers_idx.append(max_euclidean(data, centers_idx))
        if method == 'dtw':
            centers_idx.append(max_dtw(data, centers_idx))
        if method == 'wdtw':
            centers_idx.append(max_wdtw(data, centers_idx))

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

def max_wdtw(data, centers_idx):
    distances = np.zeros(len(data))

    for center_idx in centers_idx:
        for curve_idx, curve in enumerate(data):
            if window_ddtw(curve, data[center_idx]) == 0:
                distances[curve_idx] = -math.inf
            if not math.isinf(distances[curve_idx]):
                distances[curve_idx] = distances[curve_idx] + window_ddtw(curve, data[center_idx])

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

def speedy_gonzalez(data, k, window=None, random_state=1971):
    centers_idx = []

    # Set seed for reproducibility
    np.random.seed(random_state)

    # First center random
    centers_idx.append(np.random.randint(0, len(data) +1))

    # Compute disctance matrix with dtaidistance package
    dm = distance_matrix(data, window=window, parallel=True, use_c=True, only_triu=False)

    # Compute all other k's which are fartest away von actual centroids
    while len(centers_idx) != k:
        newcenter_idx = np.argmax(dm[centers_idx].sum(axis=0))
        centers_idx.append(newcenter_idx)

    return centers_idx









