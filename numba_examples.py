import copy
import requests
import numpy
import numpy as np
import pandas as panda

# Read a csv file and return the last column from each line.
file_cache = {}
def get_stock_data(file_name):
	global file_cache
	if file_name in file_cache:
		return copy.copy(file_cache[file_name])
	else:
		with open(file_name, 'rb') as infile:
			# Read each line in the file into a list.
			data = [line for line in infile]
			
			# Skip the header row
			data = data[1::]
			
			# Split each line on a comma, and return a list of the last columns
			try:
				data = [float(line.split(',')[-1]) for line in data][::-1]
			except:
				# some files will have bad data due to mismatch of symbol names
				return
			
		file_cache[file_name] = np.asarray(data)
		return np.asarray(data)

def get_list_of_symbols(filename):
	with open(filename, 'rb') as infile:
		lines = [line for line in infile]
		lines = lines[1::]
		lines = [line.split(',')[0] for line in lines]
		lines = [line.replace('"', '') for line in lines]
	return lines
	
def load_all_stock_data():
	path = './stocks/'
	symbols = get_list_of_symbols('companylist.csv')
	data = {}
	for x in symbols:
		data[x] = get_stock_data(path + x + '.csv')
		
	data = dict([(x, data[x]) for x in data if data[x] is not None])
	return data
		
def compute_daily_percentage_change(data_array):
	yesterday = data_array[:-1]
	today = data_array[1:]
	changes = (today-yesterday) / yesterday
	changes += 1
	changes = numpy.insert(changes, 0, 1)
	return changes
	
def compute_average(data_array):
	return numpy.average(data_array)
	
def generate_moving_average(data, window_size):
	if window_size > 1:
		return panda.rolling_mean(data, window_size, min_periods = 1)
	else:
		return data
	
def compute_standard_deviation(data_array):
	return numpy.std(data_array)
	
import numba
from numba import jit, float64, int64


def evaluate_strategy(prices, moving_average, starting_money):
	shares = 0
	cash = starting_money
	can_trade = 0
	for price, avg in zip(prices, moving_average):
		if can_trade > 0:
			can_trade-=1
		else:
			if price > avg and shares == 0:
				shares += cash/float(price)
				cash = 0
				can_trade = 3
			elif price < avg and cash == 0:
				cash += shares * float(price)
				shares = 0
				can_trade = 3
	return cash + shares * prices[-1]
	
compiled_evaluate_strategy = numba.jit('float64(float64[:], float64[:], int64)')(evaluate_strategy)
	
def trading_strategy(queue, results, starting_money):
	while queue.empty() == False:
		next_stock = queue.get()
		data = get_stock_data(next_stock)
		if data == None:
			queue.task_done()
			continue
		else:
			moving_average = generate_moving_average(data, 100)
			result = compiled_evaluate_strategy(data, moving_average, starting_money)
			results[next_stock] = result
			queue.task_done()
		
def path_to_files(sym):
	path = './stocks/'
	return path + sym + '.csv'
	
	
if __name__ == '__main__':
	# Getting the libraries
	import multiprocessing
	from multiprocessing import Manager, Process
	
	# Setting up our queues and results dictionary
	man = Manager()
	queue = man.Queue()
	data_metrics = man.dict()
	amount_to_invest = 10000
	
	# Load all symbols onto the process Queue
	for sym in get_list_of_symbols('companylist.csv'):
		queue.put(path_to_files(sym))
	
	# Spin up a process for each core on the machine
	for x in xrange(multiprocessing.cpu_count()):
		p = Process(target = trading_strategy, args=(queue, data_metrics, amount_to_invest))
		p.start()
		
	# Wait for all the work to finish
	queue.join()
	