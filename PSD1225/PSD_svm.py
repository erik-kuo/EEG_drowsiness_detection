from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from joblib import dump, load
import numpy as np
import pandas as pd
import csv
import time

start = time.time()

with open('PSD_feat.csv', newline='') as csvfile:
    rows = csv.reader(csvfile)

    X = []
    y = []

    for row in rows:
        if row[0] != '1' and row[0] != 'W': continue
        row_adj = row.copy()
        row_adj[4] = 10*np.log10(float(row_adj[4]))
        row_adj[5] = 10*np.log10(float(row_adj[5]))
        row_adj[6] = 10*np.log10(float(row_adj[6]))
        # row_adj[7] = 10*np.log10(float(row_adj[7]))
        X.append(row_adj[1:])
        y.append(row[0])

    X_train, X_test, y_train, y_test = train_test_split(X, y, 
        test_size=0.2,random_state=0)

    X_t_1 = []
    y_t_1 = []
    X_t_W = []
    y_t_W = []

    for Xt, yt in zip(X_test, y_test):
        if '1' in yt:
            X_t_1.append(Xt)
            y_t_1.append(yt)
        else:
            X_t_W.append(Xt)
            y_t_W.append(yt)

    clf = SVC(kernel='rbf', C=0.5, gamma=0.1, class_weight='balanced')
    clf.fit(X_train, y_train)
    print(clf)

    dump(clf, 'svm1225.joblib') 

    print('\nTraining set score: ', end='')
    print(clf.score(X_train,y_train))
    print('\nTesting set score: ', end='')
    print(clf.score(X_test, y_test))

    print('\nTP: ', end='')
    print(clf.score(X_t_1, y_t_1))

    print('\nTN: ', end='')
    print(clf.score(X_t_W, y_t_W))

end = time.time()
print('\nElasped time: ' + str(end-start))

