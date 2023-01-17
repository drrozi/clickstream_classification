import sys
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import Fred as fred
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import RocCurveDisplay
import matplotlib.pyplot as plt
import re
import glob
from collections import defaultdict
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

        # Create train and test data, 80:20
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                            random_state=42, stratify=y)

        # Classification pipelines
        nachbar = 1

        # kNN for Manhattan Distance 
        CityPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=nachbar, metric='cityblock'))])
        # kNN for Euclidean Distance 
        EucPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=nachbar, metric='euclidean'))])
        # kNN for Chebychev Distance 
        ChebPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=nachbar, metric='chebyshev'))])
        # kNN for Discrete Frechet
        DiscFrechetPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=nachbar,
                                                                       metric=disc_frechet))])
        # kNN for Discrete Dynamic Time Warping
        DiscDTWPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=nachbar, metric=disc_dtw))])
        # kNN for Discrete Frechet with traversal constraint
        WDFPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=nachbar,
                                                               metric=window_disc_frechet))])
        # knn for DDTW with traversal constraint
        WDDTWPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=nachbar,
                                                                 metric=window_ddtw))])


        mypipeline = [CityPipeline, EucPipeline, ChebPipeline, DiscFrechetPipeline, DiscDTWPipeline,
                      WDFPipeline, WDDTWPipeline]

        for mypipe in mypipeline:
            mypipe.fit(X_train, y_train)

        # ROC
        fig, ax = plt.subplots(figsize=(10, 10))

        city_disp = RocCurveDisplay.from_estimator(CityPipeline, X_test, y_test,
                                                name="Manhattan", ax=ax)
        euc_disp = RocCurveDisplay.from_estimator(EucPipeline, X_test, y_test,
                                                name="Euclidean", ax=ax)
        che_disp = RocCurveDisplay.from_estimator(ChebPipeline, X_test, y_test,
                                                name="Maximum", ax=ax)
        fre_disp = RocCurveDisplay.from_estimator(DiscFrechetPipeline, X_test, y_test,
                                                name="DF", ax=ax)
        dtw_disp = RocCurveDisplay.from_estimator(DiscDTWPipeline, X_test, y_test,
                                                name="DDTW", ax=ax)
        wdf_disp = RocCurveDisplay.from_estimator(WDFPipeline, X_test, y_test,
                                                name="WDF", ax=ax)
        wdtw_disp = RocCurveDisplay.from_estimator(WDDTWPipeline, X_test, y_test,
                                                name="WDDTW", ax=ax)

        plt.axis('square')
        plt.ylabel('True Positive Rate')
        plt.xlabel('False Positive Rate')
        plt.title("ROC - Vergleich für Kurs " + re.sub(directory, '', course))
        plt.legend(loc='lower right')
        plt.plot([0, 1], [0, 1],'k:')
        plt.savefig(re.sub(directory,'', course) + '.pdf', dpi='figure', format='pdf', backend='pgf')


if __name__ == "__main__":
   courses('/home/drazan/myproject/Labor/Labordaten/Test/OneD/oneD_Courses_txt/')

