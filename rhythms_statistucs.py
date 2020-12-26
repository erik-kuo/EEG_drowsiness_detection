import numpy as np
import csv
import math
import sys
from pathlib import Path
from scipy.stats import trim_mean, entropy

def AAC(arr):
	s = 0
	for i in range(len(arr)-1):
		s += abs(arr[i+1]-arr[i])
	res = s/len(arr)
	return res

def mob(arr):
	return (np.var(np.diff(arr))/np.var(arr))**0.5

def Complexity(arr):
	return mob(np.diff(arr))/mob(arr)

def sort_key(file_str):
	str_list = str(file_str).split('_')
	return int(str_list[1])

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Usgae: python rhythm_statistics.py <rhythm>')
		sys.exit()
	rhythm = sys.argv[1]
	print('processing ' + rhythm + ' file...')
	with open(rhythm + '_1226.csv', 'w', newline = '') as file:
		writer = csv.writer(file)
		writer.writerow(["stage", "Mean", "AAC", "COV", "TM", "Ac", "Complexity"])

		pathlist = sorted(Path('./' + rhythm).glob('*.npy'), key = sort_key)
		for path in pathlist:
			path_in_str = str(path)
			signal = np.load(path_in_str)
			stat = []
			stat.append('W') if signal[-1] == 0 else stat.append('S')
			signal = np.delete(signal, -1)
			stat.append(np.mean(signal))
			stat.append(AAC(signal))
			stat.append(np.cov(signal))
			stat.append(trim_mean(signal, 0.25))
			stat.append(np.var(signal))
			stat.append(Complexity(signal))
			writer.writerow(stat)
