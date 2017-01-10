import copy

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
		
def get_list_of_symbols(filename):
	with open(filename, 'rb') as infile:
		lines = [line for line in infile]
		lines = lines[1::]
		lines = [line.split(',')[0] for line in lines]
		lines = [line.replace('"') for line in lines]
	return lines
	

def trading_strategy(data, trading_parameters):
	# Do something with data here.
	return data;


if __name__ == '__main__':
	symbols = get_list_of_symbols('companylist.csv')