import sys
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import Fred as fred
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
import re
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
        
        # kNN for cityblock
        CityPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=1, metric='cityblock'))])

        # kNN for euclidean
        EucPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=1, metric='euclidean'))])
        
        # kNN for correlation
        CorPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=1, metric='correlation'))])
        
        # kNN for cosine
        CosPipeline = Pipeline([('knn=1', KNeighborsClassifier(n_neighbors=1, metric='cosine'))])

        mypipeline = [TraFrePipeline, DiscFrechetPipeline, DiscDTWPipeline, CityPipeline, EucPipeline, CorPipeline, CosPipeline]
        for mypipe in mypipeline:
            mypipe.fit(X_train, y_train)

        # ROC
        from sklearn.metrics import RocCurveDisplay
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 10))

        tra_disp = RocCurveDisplay.from_estimator(TraFrePipeline, X_test, y_test,
                                                name="TraFre", ax=ax)
        fre_disp = RocCurveDisplay.from_estimator(DiscFrechetPipeline, X_test, y_test,
                                                name="DF", ax=ax)
        dtw_disp = RocCurveDisplay.from_estimator(DiscDTWPipeline, X_test, y_test,
                                                name="DDTW", ax=ax)
        city_disp = RocCurveDisplay.from_estimator(CityPipeline, X_test, y_test,
                                                name="City", ax=ax)
        euc_disp = RocCurveDisplay.from_estimator(EucPipeline, X_test, y_test,
                                                name="Euc", ax=ax)
        cor_disp = RocCurveDisplay.from_estimator(CorPipeline, X_test, y_test,
                                                name="Cor", ax=ax)
        cos_disp = RocCurveDisplay.from_estimator(CosPipeline, X_test, y_test,
                                                name="Cos", ax=ax)

        plt.axis('square')
        plt.ylabel('True Positive Rate')
        plt.xlabel('False Positive Rate')
        plt.title("ROC - Vergleich" + re.sub(directory, '', course))
        plt.legend(loc='lower right')
        plt.plot([0, 1], [0, 1],'k:')
        plt.savefig(re.sub(directory,'', course) + '.pdf', dpi='figure', format='pdf', backend='pgf')


if __name__ == "__main__":
   courses('/home/drazan/myproject/Labor/Labordaten/Test/OneD/oneD_Courses_txt/')

