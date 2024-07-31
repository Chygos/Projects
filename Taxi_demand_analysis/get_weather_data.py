import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry


# code source: https://open-meteo.com/en/docs

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def get_weather_data(url, params, day_type='h'):	
	try:
		responses = openmeteo.weather_api(url, params=params)

		# Process first location. Add a for-loop for multiple locations or weather models
		response = responses[0]

		data = None

		if day_type == 'h':
			# Process hourly data. The order of variables needs to be the same as requested.
			hourly = response.Hourly()
			hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
			hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
			hourly_apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
			hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()

			hourly_data = {"date": pd.date_range(
				start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
				end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
				freq = pd.Timedelta(seconds = hourly.Interval()),
				inclusive = "left"
			)}
			hourly_data["temperature_2m"] = hourly_temperature_2m
			hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
			hourly_data["apparent_temperature"] = hourly_apparent_temperature
			hourly_data["precipitation"] = hourly_precipitation		

			data = pd.DataFrame(data = hourly_data)
		elif day_type == 'd':
			# Process hourly data. The order of variables needs to be the same as requested.
			daily = response.Daily()
			daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
			daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
			daily_apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
			daily_apparent_temperature_min = daily.Variables(3).ValuesAsNumpy()
			daily_precipitation_sum = daily.Variables(4).ValuesAsNumpy()

			daily_data = {"date": pd.date_range(
				start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
				end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
				freq = pd.Timedelta(seconds = daily.Interval()),
				inclusive = "left"
			)}
			daily_data["temperature_2m_max"] = daily_temperature_2m_max
			daily_data["temperature_2m_min"] = daily_temperature_2m_min
			daily_data["precipitation_sum"] = daily_precipitation_sum
			data = pd.DataFrame(data = daily_data)
		else:
			print(f'{day_type} not recognised!')
			quit()
		
		# print some information
		print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
		print(f"Elevation {response.Elevation()} m asl")
		print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
		print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
		return data
	except Exception as err:
		print(err)
		quit()




# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below

# url = "https://api.open-meteo.com/v1/forecast" # gets forecast (7-16 days)
# url = "https://archive-api.open-meteo.com/v1/archive" # gets actual historical
url = "https://historical-forecast-api.open-meteo.com/v1/forecast" # gets historical forecast


location_coords = input('Location Coordinates (Latitude Longitude): Separate multiple locations with a comma\n').strip().split(',')
location_coords = list(map(lambda x: x.split(), location_coords))


latitudes = [float(i[0]) for i in location_coords]
longitudes = [float(i[1]) for i in location_coords]


start_date = input('Start Date (format: yyyy-mm-dd): ').strip()
end_date = input('End Date (format: yyyy-mm-dd): ').strip()

day_type = input('Time type: Hourly (h) or Daily (d): ').strip().lower()
counts = 0 
while day_type not in ['h', 'd']:
	day_type = input('Time type: Hourly (h) or Daily (d): ').strip()
	counts += 1

	if counts == 3:
		quit()


# check the number of locations
num_locations = len(latitudes)


weather_df = []
if num_locations > 1:
	for latitude, longitude in zip(latitudes, longitudes):
		params = {
		"latitude": latitude,
		"longitude": longitude,
		"start_date": start_date,
		"end_date": end_date,
		"hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation"],
		"daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "precipitation_sum"],
		"timezone" : "GMT"
		}
		df = get_weather_data(url, params, day_type)
		df['lat'] = latitude
		df['long'] = lonitude
		weather_df.append(df)
	weather_df = pd.concat(weather_df)
else:
	latitude = latitudes[0]
	longitude = longitudes[0]

	params = {
		"latitude": latitude,
		"longitude": longitude,
		"start_date": start_date,
		"end_date": end_date,
		"hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation"],
		"daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "precipitation_sum"],
		"timezone" : "GMT"
		}
	weather_df = get_weather_data(url, params, day_type)
	weather_df['lat'] = latitude
	weather_df['long'] = longitude


print(weather_df.head())


weather_df.to_csv(f"weather_{start_date}_to_{end_date}.csv", index=False)
