libpath = 'mit-bih-polysomnographic-database-1.0.0/'
csv_filename = 'IEEG_ZC_1226.csv'

import wfdb
import matplotlib.pyplot as plt
import numpy as np
import glob
import pywt
import csv
from scipy import signal
window_len = 30
sample_time = 10
fs = 250

def WT_alpha_beta_theta(eeg_frame):
	coeffs_1 = pywt.swt(eeg_frame, 'db2', trim_approx = True)
	coeffs_2 = pywt.swt(coeffs_1[0], 'db2', trim_approx = True)
	# wfdb.plot_items(coeffs_2[0], title='D5(theta)', time_units='seconds', fs=fs)
	# wfdb.plot_items(coeffs_2[1], title='D4(alpha)', time_units='seconds', fs=fs)
	# wfdb.plot_items(coeffs_2[2], title='D3(beta)', time_units='seconds', fs=fs)
	return coeffs_2[2], coeffs_2[1], coeffs_2[0]

def process_window(filename, eeg, stage, step):
	# extract alpha/beta/theta rythms

	abt_rythms = WT_alpha_beta_theta(eeg[step*fs*window_len:step*fs*window_len + fs*sample_time])

	# compute IEEGs
	IEEGs = []
	for i in range(len(abt_rythms)):
		IEEGs.append(np.sum(np.abs(abt_rythms[i])))

	# compute zero crossing
	ZCs = []
	for i in range(len(abt_rythms)):
		ZCs.append(np.sum(-1 * abt_rythms[i][:-1] * abt_rythms[i][1:] > 0 ))

	write_data_to_csv(csv_filename, [stage] + IEEGs + ZCs)

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

def write_data_to_csv(file, features):
	with open(file, 'a', newline='') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(features)

if __name__ == '__main__':
	dat_files=glob.glob(libpath + '*.dat')
	with open(csv_filename, 'w', newline='') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow(['stage', 'alpha IEEG', 'beta IEEG', 'theta IEEG', 'alpha ZC', 'beta ZC', 'theta ZC'])
	for file in dat_files:
		print(file)
		filename = file[len(libpath):-4]
		# if 'slp01b' in file: break
		original_eeg, aux_note =  read_eeg_file(filename)
		sos = signal.butter(2, [0.5, 60], 'bandpass', fs = 250, output = 'sos')
		eeg = signal.sosfilt(sos, original_eeg)

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
