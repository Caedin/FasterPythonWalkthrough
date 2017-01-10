import copy
import requests
import numpy
import numpy as np
import pandas as panda
from timeit import default_timer as timer
import numba
from numba import jit
from numba import cuda, float32
	
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
	
def load_stock_data(filter = None):
	path = './stocks/'
	symbols = get_list_of_symbols('companylist.csv')
	if filter is not None:
		symbols = set(symbols) & set(filter)
		
	data = {}
	for x in symbols:
		data[x] = get_stock_data(path + x + '.csv')
		

	data = dict([(x, data[x]) for x in data if data[x] is not None])
	return data

@cuda.jit('void(float64[:], int64[:], float64[:], int64)')
def evaluate_strategy(prices, moving_average_windows, results, starting_money):
	index = cuda.grid(1)
	
	shares = 0
	cash = starting_money
	can_trade = 0
	window_length = moving_average_windows[index]
	moving_window = cuda.local.array(shape=501, dtype=float32)
	
	day = 0
	while day < len(prices):
		price = prices[day]
		
		# Calculate moving average
		moving_window[day % window_length] = price
		sum = 0
		c = 0
		while c < window_length:
			if moving_window[c] != 0.0:
				sum += moving_window[c]
			c += 1
				
		avg = sum / float(window_length)
			
		# Evaluate trade
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
		day += 1
	results[index] = cash + shares * price
	
def path_to_files(sym):
	path = './stocks/'
	return path + sym + '.csv'

if __name__ == '__main__':
	amount_to_invest = 10000
	max_window_size = 500
	
	# Figure out blocks and threads
	threadsPerBlock = 1
	numBlocks = max_window_size/threadsPerBlock
	
	
	# Create our memory objects in Python
	stocks = load_stock_data(['XOM'])
	moving_windows = numpy.arange(max_window_size, dtype = numpy.int64)
	results = numpy.asarray([0.0] * max_window_size, dtype = numpy.float64)

	# Allocate the memory on the GPU
	stock_data_gpu = cuda.to_device(stocks['XOM'])
	moving_windows_gpu = cuda.to_device(moving_windows)
	results_gpu = cuda.to_device(results)
	
	# Execute our code on the GPU
	t = timer()
	evaluate_strategy[threadsPerBlock, numBlocks](stock_data_gpu, moving_windows_gpu, results_gpu, amount_to_invest)
	print 'Time taken to compute:', timer() - t
	
	# Move results off of GPU and back into Python/CPU memory
	results = results_gpu.copy_to_host()
	
	# Print results
	results_formated = [0.0] * len(results)
	for x, y in enumerate(results):
		results_formated[x] = ('XOM', x, y)
		
	results_formated.sort(key = lambda x: x[2])
	results_formated.reverse()
	
	for x in xrange(5):
		print results_formated[x]
		
    
	
	
	
	
	