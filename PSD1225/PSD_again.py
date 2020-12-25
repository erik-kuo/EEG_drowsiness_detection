import numpy as np
from spectrum import *
import glob
import csv
from scipy import signal

sample_time = 10
fs = 250

dat_files=glob.glob('EEG/*.npy')

PSD_feats = []

for file in dat_files:
    # if 'slp02' in file: break
    print(file + '\t' + file[4:-4])
    eeg = np.load(file)
    sos = signal.butter(2, 0.5, 'high', fs=250, output='sos')
    eeg = signal.sosfilt(sos, eeg)
    sos = signal.butter(2, 60, 'low', fs=250, output='sos')
    eeg = signal.sosfilt(sos, eeg)

    psd = pburg(eeg[0:sample_time*fs], 20, sampling=fs)
    burg = psd.psd
    f = psd.frequencies()

    _sum = np.sum(burg)
    cdf = np.array([np.sum(burg[0:i]) for i in range(len(f))]) / _sum
    
    features1 = np.searchsorted(cdf, [0.25, 0.5, 0.95]) *0.1
    features2 = np.array([np.sum(burg[40:80]), np.sum(burg[80:120]), _sum])

    feat = np.concatenate(([file[4]], features1, features2))
    print(feat)
    PSD_feats.append(feat.copy())

with open('PSD_feat.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    writer.writerow(['Stage', '25%', 'Central', 'Max', 'Theta', 'Alpha', 'Total'])
    for feats in PSD_feats:
        writer.writerow(feats)
    pass

