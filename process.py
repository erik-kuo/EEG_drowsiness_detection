libpath = 'physionet.org/files/slpdb/1.0.0/'

import wfdb
import matplotlib.pyplot as plt
import numpy as np
import glob

sample_time = 30
fs = 250

PSD_W = []
PSD_1 = []
f = []

def plot_segment(filename, eeg, stage, step):
    plt.figure()
    _psd, f = plt.psd(eeg[step*fs*30:(step+1)*fs*30], Fs=fs, return_line=False)
    PSD_W.append(_psd) if stage == 'W' else PSD_1.append(_psd)
    # plt.axis([0, 140, -90, -30])
    # plt.suptitle('PSD of ' + filename + ' using pyplot.psd()', fontweight ="bold") 
    # plt.savefig('1220/PSD_' + filename + '_' + stage + '_' + str(step) + '.png')
    plt.close()
    pass

def plot_file(filename):
    record = wfdb.rdrecord(libpath + filename)
    annotation = wfdb.rdann(libpath + filename, 'st')
    print(annotation.aux_note)
    # wfdb.plot_wfdb(record=record, annotation=annotation, title=filename, time_units='seconds', plot_sym=True)

    if len(annotation.aux_note) == 0:
        return

    eeg = record.p_signal[:, 2]
    print(record.sig_name[2], eeg)
    # wfdb.plot_items(eeg, title=filename, time_units='seconds', fs=fs)

    i = 0
    sig_len = len(eeg)
    while i < len(annotation.aux_note) and sig_len - i*fs*30 > sample_time * fs:
        if '1' in annotation.aux_note[i]:
            plot_segment(filename, eeg, '1', i)
        elif 'W' in annotation.aux_note[i]:
            plot_segment(filename, eeg, 'W', i)
        i = i + 1
    
    pass

dat_files=glob.glob(libpath + '*.dat')

for file in dat_files:
    print(file)
    if 'slp32' in file: break
    plot_file(file[len(libpath):-4])

PSD_W = np.array(PSD_W)
PSD_1 = np.array(PSD_1)

plt.figure()
plt.plot(f, np.mean(PSD_W, axis=0))
plt.plot(f, np.mean(PSD_1, axis=0))
plt.axis([0, 140, -90, -30])
plt.suptitle('PSD of ' + filename + ' using pyplot.psd()', fontweight ="bold") 
plt.show()

