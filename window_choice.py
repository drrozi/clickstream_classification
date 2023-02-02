# Import packages
import math
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import Fred as fred
import time
import re

# Import data
import glob
from collections import defaultdict



def window (course):

        dic = defaultdict(list)
        k = 1
        for filename in glob.glob(course+ "/*"):
            if filename == course+"/dataset.txt":
                continue
            dic[k] = fred.Curve(np.loadtxt(filename, skiprows=1, dtype=float),
                                filename.strip(course).strip('.txt'))
            k = k+1

        # Separate clicks (X) and final_result (y)
        curves = fred.Curves()
        for k in dic:
            curves.add(fred.Curve(dic[k].values[:, 0], dic[k].name))

        y = np.array([])

        for k in dic:
            dran = np.unique(dic[k].values[:,1])
            y = np.append(y, dran, axis=0)

        data = np.asarray(curves)
        nsamples, nx, ny = data.shape
        X = data.reshape((nsamples, nx*ny))

        # logarithmic transformation
        X = np.log1p(X)

        from dtaidistance.dtw import distance_matrix, distance

        nachbarn=1
        fenster = 31
        aucs = []

        for w in range(1, fenster):
            knn = KNeighborsClassifier(n_neighbors=nachbarn, metric=distance,
                                      metric_params={'window': w, 'use_c': True})
            cv = cross_val_score(knn, X, y, cv=5, scoring='roc_auc')
            aucs.append(np.mean(cv))

        return aucs

if __name__ == '__main__':

    directory = '/home/drazan/myproject/Labor/Labordaten/Test/OneD/oneD_Courses_txt/'
    for course in glob.glob(directory + '*'):
        start = time.time()
        if course == directory + 'dataset.txt':
            continue
        aucs = window(course)

        plt.figure()
        plt.xlabel('Window Size', fontsize=15)
        plt.ylabel('AUC', fontsize=15)
        plt.axvline(x = np.argmax(aucs)+1, color='r', linestyle='dashed')
        plt.plot(range(1, 30), aucs)
        plt.savefig(re.sub(directory, '', course)+'_w.pdf', dpi='figure', format='pdf', backend='pgf')

        end = time.time()
        print("Total time elapsed:", end - start)


