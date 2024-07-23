import pandas as pd
from tqdm import tqdm
from glob import glob
from pathlib import os
import numpy as np


# folder path
path = "D:/data/Bike_sharing_rentals/data/files/"

def calc_distance(lat1, long1, lat2, long2, unit='km'):
	"""
	Calculates the Haversine distance of two locations and converts to kilometres (km) or miles (mi)

	Parameters
	==========
	lat1, lat2: Latitudes of location points
	long1, long2: Longitudes of location points
	"""
	distance_map = {'km' : 6371, 'mi':3959}

	# convert to radians
	lat1 = np.deg2rad(lat1)
	long1 = np.deg2rad(long1)
	lat2 = np.deg2rad(lat2)
	long2 = np.deg2rad(long2)

	diff_lat = lat2 - lat1
	diff_long = long2 - long1

	angle_res = np.sqrt(np.sin(diff_lat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(diff_long/2)**2)

	distance = distance_map.get(unit) * angle_res
	return distance


def preprocess_data(data):
	"""
	Preprocesses bike sharing data and aggregates total
	bikes shared in all pickup stations
	"""
	# convert pickup time and arrival time to daily
	data = data.assign(started_at = pd.to_datetime(data.started_at),
					   ended_at = pd.to_datetime(data.ended_at))
	# get day pickup date
	data['pickup_hour'] = pd.DatetimeIndex(data.started_at).floor('h')
	data['rideable_type'] = data['rideable_type'].str.replace('_bike', '', regex=True).str.strip()
	data['distance'] = data.filter(regex='lat|lng').apply(lambda x: calc_distance(
		x.start_lat, x.start_lng, x.end_lat, x.end_lng, unit='km'), axis=1)
	data['duration'] = (data.ended_at - data.started_at).dt.total_seconds().abs().round(2)

	aggregated_data = (
		data
		.groupby(['rideable_type', 'pickup_hour', 'member_casual']).agg(
			{
			'started_at': 'count', 
			'duration' : 'mean', 
			'distance' : 'sum' # total distance
			})
		.reset_index()
		)
	aggregated_data = aggregated_data.rename(
		{'started_at':'num_rides', 'duration':'duration_secs', 'distance' : 'distance_km'}, axis=1)

	aggregated_data['duration_mins'] = round(aggregated_data['duration_secs']/60, 2)

	# select only for classic and electric bikes since they are the only two bike types used by Capital Bikeshare
	aggregated_data = aggregated_data.query("rideable_type != 'docked'")

	return aggregated_data


files = glob(os.path.join(path, 'extracted_files/', '*bikeshare-tripdata.csv'))

data = []


for file in tqdm(files):
	file_df = pd.read_csv(file)
	df = preprocess_data(file_df)
	data.append(df)

data = pd.concat(data)

print(data.head())
print(data.shape)

# save file
filepath = os.path.join(path, 'bike_shares.csv')

if os.path.exists(filepath):
	response = input(f'{os.path.basename(filepath)} exists.\nDo you want to overwrite it (Y/N)\n')
	if response.title()  == 'Y':
		data.to_csv(filepath, index=False)
	elif response.title() == 'N':
		# append recent data
		data.to_csv(filepath, mode='a', index=False)
else:
	data.to_csv(filepath, mode='w', index=False)

filename = os.path.basename(filepath)
folder = os.path.dirname(filepath)
print(f'{filename} saved in {folder}')