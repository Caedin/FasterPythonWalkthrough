import copy
import requests
import numpy
import numpy as np

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
	
def moving_average(data_array, avg):
	
	
def compute_standard_deviation(data_array):
	return numpy.std(data_array)
	
def calculate_metrics(queue, results):
	while queue.empty() == False:
		next_stock = queue.get()
		data = get_stock_data(next_stock)
		if data == None:
			queue.task_done()
			continue
		else:
			daily_changes = compute_daily_percentage_change(data)
			avg = compute_average(daily_changes)
			std = compute_standard_deviation(daily_changes)
			results[next_stock] = (avg, std)
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
	
	# Load all symbols onto the process Queue
	for sym in get_list_of_symbols('companylist.csv'):
		queue.put(path_to_files(sym))
	
	
	# Spin up a process for each core on the machine
	for x in xrange(multiprocessing.cpu_count()):
		p = Process(target = calculate_metrics, args=(queue, data_metrics))
		p.start()
		
	# Wait for all the work to finish
	queue.join()
	