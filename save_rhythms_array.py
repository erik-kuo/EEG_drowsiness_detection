libpath = 'mit-bih-polysomnographic-database-1.0.0/'

import wfdb
import matplotlib.pyplot as plt
import numpy as np
import glob
from pyhht import EMD
from pyhht.visualization import plot_imfs
from pyhht.utils import inst_freq
from scipy.signal import hilbert
from scipy.stats import trim_mean, entropy
import csv
import math
from pathlib import Path

window_len = 30
sample_time = 10
fs = 250

def process_window(filename, eeg, stage, step):
	# plt.figure()
	s = np.zeros((5,2501))
	print('step: ', step)
	# t = np.linspace(step*fs*30,step*fs*30+fs*10,fs*10)
	decomposer = EMD(eeg[step*fs*window_len:step*fs*window_len+fs*sample_time])
	imfs = decomposer.decompose()
	# print(len(imfs))
	# plot_imfs(eeg[step*fs*30:step*fs*30+fs*10], imfs, t)
	for imf in imfs:
		analytic_signal = hilbert(imf)
		instantaneous_phase = np.unwrap(np.angle(analytic_signal))
		instantaneous_freq = (np.diff(instantaneous_phase)/(2.0*np.pi)*fs)
		# print(len(instantaneous_freq))
		for i in range(len(instantaneous_freq)):
			if instantaneous_freq[i]>1 and instantaneous_freq[i]<=4:
				s[0][i] += imf[i]
			elif instantaneous_freq[i]>4 and instantaneous_freq[i]<=8:
				s[1][i] += imf[i]
			elif instantaneous_freq[i]>8 and instantaneous_freq[i]<=12:
				s[2][i] += imf[i]
			elif instantaneous_freq[i]>12 and instantaneous_freq[i]<=30:
				s[3][i] += imf[i]
			elif instantaneous_freq[i]>30 and instantaneous_freq[i]<=60:
				s[4][i] += imf[i]

	for i in range(5):
		if stage == 'W':
			s[i][-1] = 0
		else:
			s[i][-1] = 1
		
	# save np array
	Path('./delta').mkdir(parents=True, exist_ok=True)
	Path('./theta').mkdir(parents=True, exist_ok=True)
	Path('./alpha').mkdir(parents=True, exist_ok=True)
	Path('./beta').mkdir(parents=True, exist_ok=True)
	Path('./gamma').mkdir(parents=True, exist_ok=True)
	
	np.save('./delta/' + filename + '_' + str(step) + '_delta', s[0])
	np.save('./theta/' +filename + '_' + str(step) + '_theta', s[1])
	np.save('./alpha/' +filename + '_' + str(step) + '_alpha', s[2])
	np.save('./beta/' +filename + '_' + str(step) + '_beta', s[3])
	np.save('./gamma/' +filename + '_' + str(step) + '_gamma', s[4])


	pass

def read_eeg_file(filename):
	record = wfdb.rdrecord(libpath + filename)
	annotation = wfdb.rdann(libpath + filename, 'st')
	# print(annotation.aux_note)
	# wfdb.plot_wfdb(record=record, annotation=annotation, title=filename, time_units='seconds', plot_sym=True)
	eeg = record.p_signal[:, 2]
	# print(record.sig_name[2], eeg)
	# wfdb.plot_items(eeg, title=filename, time_units='seconds', fs=fs)
	return eeg, annotation.aux_note

if __name__ == '__main__':
	dat_files=glob.glob(libpath + '*.dat')

	for file in dat_files:
		print(file)
		filename = file[len(libpath):-4]
		# if 'slp01b' in file: break
		if 'slp41' not in file: continue
		eeg, aux_note =  read_eeg_file(filename)

		if len(aux_note) == 0:
			continue

		i = 0
		sig_len = len(eeg)
		while i < len(aux_note) and sig_len - i*fs*window_len > sample_time * fs:
			if '1' in aux_note[i]:
				process_window(filename, eeg, 'S', i)
			elif 'W' in aux_note[i]:
				process_window(filename, eeg, 'W', i)
			i = i + 1