# Filtering warnings
import warnings
warnings.filterwarnings('ignore')

# Import packages
# import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import Fred as fred
import re

from collections import defaultdict

from sklearn.model_selection import train_test_split
from sklearn_extra.cluster import KMedoids
from my_dists import disc_dtw, disc_frechet, window_ddtw, window_disc_frechet

def clustering_kMedoids(directory, dist = 'manhattan', lg = 'y'):

    for course in glob.glob(directory + "*"):
        if course == directory + "dataset.txt":
            continue

        dic = defaultdict(list)
        k = 1
        for filename in glob.glob(course + "/*"):
            if filename == course + "/dataset.txt":
                continue
            dic[k] = fred.Curve(np.loadtxt(filename, skiprows=1, dtype=float),
                                filename.strip(course).strip('.txt'))
            k = k + 1

        # Separate clicks (X) and final_result (y)
        curves = fred.Curves()
        for k in dic:
            curves.add(fred.Curve(dic[k].values[:, 0], dic[k].name))

        y = np.array([])

        for k in dic:
            dran = np.unique(dic[k].values[:, 1])
            y = np.append(y, dran, axis=0)

        data = np.asarray(curves)
        nsamples, nx, ny = data.shape
        X = data.reshape((nsamples, nx*ny))

        if lg == 'y':
            X = np.log1p(X)
            print("Logarithmic scale")

        clus = KMedoids(n_clusters=1, metric=dist, init='random', random_state=1971).fit(X)
        print(re.sub(directory, '', course))
        print("Id:", clus.medoid_indices_)
        print("Medoid:", clus.cluster_centers_)


if __name__ == "__main__":

    clustering_kMedoids('/home/drazan/myproject/Labor/Labordaten/Test/OneD/oneD_Courses_txt/',
                        window_ddtw, 'y')





