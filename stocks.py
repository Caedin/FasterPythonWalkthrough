import copy
import requests

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
			data = [line.split(',')[-1] for line in data]
			
		file_cache[file_name] = data
		return data

def trading_strategy(data, trading_parameters):
	# Do something with data here.
	return data;
		
def get_list_of_symbols(filename):
	with open(filename, 'rb') as infile:
		lines = [line for line in infile]
		lines = lines[1::]
		lines = [line.split(',')[0] for line in lines]
		lines = [line.replace('"', '') for line in lines]
	return lines
	
# Code that the thread should execute. Note: Dictionaries are thread safe in CPython
def download_stock_data(data, symbol, url):
	data[symbol] = requests.get(url)
	return
	
def download_stocks(symbols):
	import threading
	data = {}
	
	url_symbol_pairs = [(sym,'http://ichart.yahoo.com/table.csv?s='+sym) for sym in symbols]
	thread_pool = []
	for pair in url_symbol_pairs:
		symbol = pair[0]
		url = pair[1]
		
		# Create and start a thread, track it in the thread pool
		thread = threading.Thread(target=download_stock_data, args=(data, symbol, url))
		thread_pool.append(thread)
		thread.start()
	
	# Wait for all threads to finish up
	for t in thread_pool:
		t.join()
		
	return data;

if __name__ == '__main__':
	symbols = get_list_of_symbols('companylist.csv')
	data = download_stocks(symbols[:100])