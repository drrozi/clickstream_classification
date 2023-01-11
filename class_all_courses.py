import sys
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import Fred as fred
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier

import glob
from collections import defaultdict

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

        # Create train and test data, 80:20
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                            random_state=42, stratify=y)

        # Classification pipelines

        #kNN for Discrete Frechet
        from my_dists import disc_frechet
        DiscFrechetPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=1, metric=disc_frechet))])

        # kNN for Discrete Dynamic Time Warping
        from my_dists import disc_dtw
        DiscDTWPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=1, metric=disc_dtw))])

        # kNN for trafre
        from my_dists import trafre
        TraFrePipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=1, metric=trafre))])

        mypipeline = [TraFrePipeline, DiscFrechetPipeline, DiscDTWPipeline]
        for mypipe in mypipeline:
            mypipe.fit(X_train, y_train)

        # ROC
        from sklearn.metrics import RocCurveDisplay
        import matplotlib.pyplot as plt

        tra_disp = RocCurveDisplay.from_estimator(TraFrePipeline, X_test, y_test, name="TraFre")
        fre_disp = RocCurveDisplay.from_estimator(DiscFrechetPipeline, X_test, y_test, 
                                                  name="DF", ax=tra_disp.ax_)
        dtw_disp = RocCurveDisplay.from_estimator(DiscDTWPipeline, X_test, y_test, 
                                                  name="DDTW", ax=tra_disp.ax_)
        dtw_disp.figure_.suptitle("ROC Vergleich für Kurs " + course.strip(directory))
        plt.xlabel('False positive rate')
        plt.ylabel('True positive rate')
        plt.savefig(course.strip(directory))


if __name__ == "__main__":
   courses('/home/drazan/myproject/Labor/Labordaten/Test/OneD/oneD_Courses_txt/')

