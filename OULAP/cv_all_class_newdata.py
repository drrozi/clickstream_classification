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
from my_dists import disc_dtw, disc_frechet, window_ddtw, window_disc_frechet, k_greatest_manhattan

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

        X = np.log1p(X)
        # binned classes
        delete = np.where(y == -97)
        y = np.delete(y, delete, 0)
        X = np.delete(X, delete, 0)

        y_bined = np.array([])
        for k in y:
            if k in [0, 1, 2, 3]:
                y_bined = np.append(y_bined, 'F')
            elif k in [4, 5, 6]:
                y_bined = np.append(y_bined, 'C')
            elif k in [7, 8, 9]:
                y_bined = np.append(y_bined, 'B')
            elif k in [10, 11, 12]:
                y_bined = np.append(y_bined, 'A')
        y = y_bined
        print(len(y))

        # Classification 
        distances = {'Manhattan':'cityblock', 'Euclidean': 'euclidean', 'Maximum': 'chebyshev',
                     'DF': disc_frechet, 'DDTW': disc_dtw, 'WDF': window_disc_frechet, 'WDDTW': window_ddtw,
                     'k_g_Manhattan': k_greatest_manhattan
                    }
        nachbar = 1
        scoring = ['accuracy', 'f1_micro']

        df = pd.DataFrame(columns = ['distance', 'accuracy', 'f1_micro'],
                 index = [0,1,2,3,4,5,6,7])

        df['distance'] = distances

        row = 0
        for key, dist in distances.items():
            knn = KNeighborsClassifier(n_neighbors=nachbar, metric=dist)
            scores = cross_validate(knn, X, y, scoring=scoring, n_jobs=-1,
                                    cv=5, return_train_score=True)
            score = [key, np.mean(scores['test_accuracy']), np.mean(scores['test_f1_micro'])]

            df.loc[row, 0:] = score

            row = row + 1

        print(re.sub(directory,'', course))
        print(df.to_latex(index=False))


if __name__ == "__main__":
    courses( "/home/drazan/Dokumente/TU Dortmund/Datenanalyse TU DO/Veranstaltungen/9_WiSe2022_23/Daten_BA/EinD/einD_Courses_txt/")
