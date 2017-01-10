import requests

def get_list_of_symbols(filename):
	with open(filename, 'rb') as infile:
		lines = [line for line in infile]
		lines = lines[1::]
		lines = [line.split(',')[0] for line in lines]
		lines = [line.replace('"', '') for line in lines]
	return lines
	
# Code that the thread should execute. Note: Dictionaries are thread safe in CPython
def download_stock_data(data, queue):
	while True:
		pair = queue.get()
		symbol = pair[0]
		url = pair[1]
		data[symbol] = requests.get(url)
		queue.task_done()

def download_stocks(symbols):
	import threading, Queue
	data = {}
	work_queue = Queue.Queue()
	
	url_symbol_pairs = [(sym,'http://ichart.yahoo.com/table.csv?s='+sym) for sym in symbols]
	for pair in url_symbol_pairs:
		work_queue.put(pair)
	
	for x in xrange(50):
		thread = threading.Thread(target=download_stock_data, args=(data, work_queue))
		thread.daemon = True
		thread.start()
	
	# Wait for all threads to finish up
	work_queue.join()
		
	return data;

def write_stocks_to_file(stocks):
	path = './stocks/'
	for symbol in stocks:
		with open(path+symbol+'.csv', 'wb') as outfile:
			for x in stocks[symbol].text:
				outfile.write(x)

if __name__ == '__main__':
	symbols = get_list_of_symbols('companylist.csv')
	data = download_stocks(symbols)
	write_stocks_to_file(data)