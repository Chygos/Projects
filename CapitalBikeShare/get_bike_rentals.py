import os
import requests
import datetime
from glob import glob
import re
import shutil
from tqdm import tqdm


path = "D:/data/Bike_sharing_rentals/data/files"

def get_bike_data(url):
	filename = os.path.basename(url)
	filepath = os.path.join(path, filename)

	try:
		result = requests.get(url, params={'downloadformat':'zip'})
		if result.status_code == 200:
			with open(filepath, mode='wb') as file:
				file.write(result.content)
		else:
			exit(1)
	except Exception as err:
		print(err)
		exit()


def unzip_file(file, folder_name=None):
	# unzip
	folder_name = os.path.join(path, folder_name)
	try:
		shutil.unpack_archive(file, folder_name)
	except Exception as err:
		print(err)
		exit()



# extract files

start = '2022-01-01'
start = datetime.datetime.strptime(start, '%Y-%m-%d')
end = datetime.datetime.today().strftime('%Y-%m') + '-01'
end  = datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=31)


# convert date to string and extract year and month eg '2022-03'
to_string = lambda x: re.search('[0-9]{4}-[0-9]{2}', str(x)).group().replace('-', '')
n_months = (end - start).days // 30
dates = [start] + [start + datetime.timedelta(days=31*i) for i in range(1, n_months+1)]


# download data
files = glob(os.path.join(path, '*capitalbikeshare-tripdata.zip'))

url = "https://s3.amazonaws.com/capitalbikeshare-data/202201-capitalbikeshare-tripdata.zip"

if len(files) == 0:
	dates = list(map(to_string, dates))
	for date in tqdm(dates):
		url = re.sub('[0-9]{6}', date, url)
		get_bike_data(url)
elif len(files) > 0:
	last_date = re.search('[0-9]{6}', files[-1]).group()
	last_date = datetime.datetime.strptime(last_date, '%Y%m')
	if last_date < end:
		n_months = (end - last_date).days // 30
		dates = [last_date + datetime.timedelta(days=31*i) for i in range(1, n_months+1)]
		for date in tqdm(dates):
			url = re.sub('[0-9]{6}', date, url)
			get_bike_data(url)
	else:
		print('Files up to date')
		pass





# extract files
print('Extracting file...\n')
if len(files) > 0:
	for file in tqdm(files):
		unzip_file(file, 'extracted_files')
else:
	print('No files exist')
	quit()