import os
import requests
import datetime
from glob import glob
import re

"""
Gets the Yellow trips data of New York TLC trips records
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
"""

def get_file(url=None):
	"""
	Downloads data from url and saves in working directory

	url: url linking the data
	"""
	filename = os.path.basename(url)
	filepath = os.path.join(path, 'data', filename)
	try:
		result = requests.get(url, params={'downloadformat' : 'parquet'})
		if result.status_code == 200:
			with open(filepath, mode='wb') as file:
				file.write(result.content)
			print(f'{filename} saved in {os.path.dirname(filepath)}')
		else:
			print(f'{filename} does not exist')
			exit(1)
	except Exception as err:
		print(err)



path = os.getcwd()
current_date = datetime.datetime.now().strftime('%Y-%m') + '-01'
current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d')

# get all previous data (if exists)
if not os.path.exists(os.path.join(path, 'data')):
	os.mkdir(os.path.join(path, 'data'))

all_data = glob(os.path.join(path, 'data', 'yellow_tripdata*.parquet'))
if len(all_data) > 0:
	# get the months in the dataset
	months = [re.search('[0-9]{,4}-[0-9]{,2}', i).group() for i in all_data]
	months = list(map(lambda i: datetime.datetime.strptime(i, '%Y-%m'), months))
	last_month = months[-1]

	# get number of months past since last date and get the months to get
	number_of_months_from_last_date = (current_date - last_month).days // 30 - 2  # lag by 2 months
	# create months to get
	months_to_get = [last_month + datetime.timedelta(days=31*i) for i in range(1,number_of_months_from_last_date+1)]
	# converts to str
	months_to_get = list(map(lambda i: str(datetime.datetime.strftime(i, '%Y-%m')), months_to_get))
else:
	last_month = current_date - datetime.timedelta(days=31*3) # lag of 3 months in case data for two months hasn't been released
	last_month = datetime.datetime.strftime(last_month, '%Y-%m')
	months_to_get = [last_month]


url = input('Enter URL: ').strip()
if len(url) == 0:
	# last data
	url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-03.parquet"
print(f"months to get {', '.join(months_to_get)}")
try:
	if len(months_to_get) == 0:
		print('No new data. Dataset up to date!')
		quit()
	for month in months_to_get:
		url = re.sub('\d{4}-\d{2}.parquet', '', url)
		url = url + month + '.parquet'
		get_file(url)
except Exception as err:
	print(err)

 #url = https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-03.parquet