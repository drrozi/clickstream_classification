import sys
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import Fred as fred
import glob
import re
import matplotlib.pyplot as plt

from collections import defaultdict
from sklearn.model_selection import cross_validate
from sklearn.neighbors import KNeighborsClassifier
from my_dists import disc_dtw, disc_frechet, window_ddtw, window_disc_frechet

def courses(directory):

    for course in glob.glob(directory + '*'):
        if course == directory + 'dataset.txt':
            continue

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

        # Classification 
        distances = {'Manhattan':'cityblock', 'Euclidean': 'euclidean', 'Maximum': 'chebyshev',
                     'DF': disc_frechet, 'DDTW': disc_dtw, 'WDF': window_disc_frechet, 'WDDTW': window_ddtw}
        nachbar = 1
        scoring = ['accuracy', 'roc_auc', 'precision', 'recall', 'f1']

        df = pd.DataFrame(columns = ['distance', 'accuracy', 'roc_auc', 'precision', 'recall', 'f1'],
                 index = [0,1,2,3,4,5,6])

        df['distance'] = distances

        row = 0
        for key, dist in distances.items():
            knn = KNeighborsClassifier(n_neighbors=nachbar, metric=dist, n_jobs=-1)
            scores = cross_validate(knn, X, y, scoring=scoring, n_jobs=-1,
                                    cv=5, return_train_score=True)
            score = [key, np.mean(scores['test_accuracy']), np.mean(scores['test_roc_auc']),
                     np.mean(scores['test_precision']), np.mean(scores['test_recall']),
                     np.mean(scores['test_f1'])]

            df.loc[row, 0:] = score

            row = row + 1

        print(re.sub(directory,'', course))
        print(df.to_latex(index=False))


if __name__ == "__main__":
   courses('/home/drazan/myproject/Labor/Labordaten/Test/OneD/oneD_Courses_txt/')

