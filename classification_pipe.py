
# Filtering warnings
import warnings
warnings.filterwarnings('ignore')

# Import packages
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
import Fred as fred

# Import data
import glob
from collections import defaultdict

dic = defaultdict(list)
ordner = '/home/drazan/myproject/Labor/Labordaten/Test/OneD/oneD_Courses_txt/FFF2013J/'
k = 1

for filename in glob.glob(ordner + "*"):
    if filename == ordner+"dataset.txt":
        continue
    dic[k] = fred.Curve(np.loadtxt(filename, skiprows=1, dtype=float),
                        filename.strip(ordner).strip('.txt'))
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
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42,
                                                    stratify=y)

# Classification pipelines

#kNN for Discrete Frechet
from my_dists import disc_frechet
DiscFrechetPipeline = Pipeline([('knn=5', KNeighborsClassifier(n_neighbors=5, metric=disc_frechet))])

# kNN for Discrete Dynamic Time Warping
from my_dists import disc_dtw
DiscDTWPipeline = Pipeline([('knn=5', KNeighborsClassifier(n_neighbors=5, metric=disc_dtw))])

# kNN for trafre
from my_dists import trafre
TraFrePipeline = Pipeline([('knn=5', KNeighborsClassifier(n_neighbors=5, metric=trafre))])

# Training and Validation
mypipeline = [DiscFrechetPipeline, DiscDTWPipeline, TraFrePipeline]
PipelineDict = {0: 'DF', 1: 'DDTW', 2: 'TraFre'}

for mypipe in mypipeline:
    mypipe.fit(X_train, y_train)

for i, model in enumerate(mypipeline):
    print("{} Test Accuracy: {}".format(PipelineDict[i], model.score(X_test, y_test)))

# ROC
from sklearn.metrics import roc_auc_score

prob = TraFrePipeline.predict_proba(X_test)[::,1]
prob_df = DiscFrechetPipeline.predict_proba(X_test)[::,1]
prob_dtw = DiscDTWPipeline.predict_proba(X_test)[::,1]

print("TraFre:", roc_auc_score(y_test, prob), "DF:", roc_auc_score(y_test, prob_df),
      "DDTW:", roc_auc_score(y_test, prob_dtw))

# ROC-Curves
from sklearn.metrics import RocCurveDisplay
import matplotlib.pyplot as plt

tra_disp = RocCurveDisplay.from_estimator(TraFrePipeline, X_test, y_test,
                                          name="TraFre")
fre_disp = RocCurveDisplay.from_estimator(DiscFrechetPipeline, X_test, y_test,
                                          name="DF", ax=tra_disp.ax_)
dtw_disp = RocCurveDisplay.from_estimator(DiscDTWPipeline, X_test, y_test,
                                          name="DDTW", ax=tra_disp.ax_)
dtw_disp.figure_.suptitle("ROC Vergleich")
plt.show()







