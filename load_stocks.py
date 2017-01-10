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
			try:
				data = [float(line.split(',')[-1]) for line in data][::-1]
			except:
				# some files will have bad data due to mismatch of symbol names
				return
			
		file_cache[file_name] = data
		return data

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
	daily_changes = [0.0] * len(data_array)
	for i, price in enumerate(data_array):
		if  i == 0:
			daily_changes[i] = 1
		else:
			yesterday = data_array[i-1]
			today = price
			daily_changes[i] = ((today - yesterday) / yesterday) + 1
	return daily_changes
	
def compute_average(data_array):
	sum = 0
	for data in data_array:
		sum += data
	return sum/len(data_array)
	
def compute_standard_deviation(data_array, avg):
	sum = 0 
	for x in data_array:
		sum += ((x - avg)*(x - avg))
	sum /= len(data_array)
	return sum**(1/2.0)

if __name__ == '__main__':
	data_metrics = {}
	data = load_all_stock_data()
	