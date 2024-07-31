# Overview

This notebook will continue analysing New York Yellow taxi cab demand. Based on the demand group insight obtained in the analysis notebook, we will predict the average hourly rides in two out of the three groups (medium and high). The goal is to accurately predict hourly taxi demands in these areas to provide adequate taxis to meet with the demand. Model development will be based on historical taxi rides in New York between January 2019 and March 2024 in these demand groups and evaluate the model's performance on taxi rides in April 2024. 

# Approach

## Data Preprocessing
But firstly, we will preprocess the new dataset (April 2024) to resemble the historical data. After that, we will perform feature engineering (transformations, categorical encoding and extraction of new features) to improve model performance. New features to be created would be the time features such as year, month, season, and hour. We will add forecasted hourly weather conditions downloaded from [Open-Meteo](https://open-meteo.com/) to improve the model's performance using their weather API. We assume that the predicted weather conditions of the next hour may affect demand. For example, if it rains the next hour, there may be an increase in taxi demand. Similarly, the average taxi demand in the preceding hours may also help improve model performance. As a result, we will create lagged and rolling features of taxi demand in these demand groups.

# Modelling

This modelling will be a time series task. We will split the historical data into train and validation sets. The validation data will contain the latest taxi demand data to resemble the test set and estimate how our model will perform on the test dataset.

A simple baseline model will predict each demand group's average hourly rides per month. After that, further approaches would be to improve performance.

## Loading Libraries and Packages


```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import lightgbm as lgb
import catboost as cat
from feature_engine.datetime import DatetimeFeatures
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.model_selection import cross_val_score
from feature_engine.encoding import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import root_mean_squared_error, mean_absolute_error
import plotnine as pn
from IPython.display import display
import holidays
```


```python
data = pd.read_csv('nyc_hourly_rides.csv', parse_dates=['ride_datetime'])
new_data = pd.read_parquet('data/yellow_tripdata_2024-04.parquet')
station_demand = pd.read_csv('station_demand_group.csv')
weather = pd.read_csv('weather_2019-01-01_to_2024-04-30.csv', parse_dates=['date'])
```

## Data Exploration


```python
data.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ride_datetime</th>
      <th>avg_hourly_rides</th>
      <th>demand_group</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2019-01-01 00:00:00</td>
      <td>219.2000</td>
      <td>high</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2019-01-01 00:00:00</td>
      <td>6.3711</td>
      <td>low</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2019-01-01 00:00:00</td>
      <td>141.5313</td>
      <td>medium</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2019-01-01 01:00:00</td>
      <td>244.3333</td>
      <td>high</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2019-01-01 01:00:00</td>
      <td>12.6429</td>
      <td>low</td>
    </tr>
  </tbody>
</table>
</div>




```python
new_data.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>VendorID</th>
      <th>tpep_pickup_datetime</th>
      <th>tpep_dropoff_datetime</th>
      <th>passenger_count</th>
      <th>trip_distance</th>
      <th>RatecodeID</th>
      <th>store_and_fwd_flag</th>
      <th>PULocationID</th>
      <th>DOLocationID</th>
      <th>payment_type</th>
      <th>fare_amount</th>
      <th>extra</th>
      <th>mta_tax</th>
      <th>tip_amount</th>
      <th>tolls_amount</th>
      <th>improvement_surcharge</th>
      <th>total_amount</th>
      <th>congestion_surcharge</th>
      <th>Airport_fee</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2024-04-01 00:02:40</td>
      <td>2024-04-01 00:30:42</td>
      <td>0.0</td>
      <td>5.2</td>
      <td>1.0</td>
      <td>N</td>
      <td>161</td>
      <td>7</td>
      <td>1</td>
      <td>29.6</td>
      <td>3.5</td>
      <td>0.5</td>
      <td>8.65</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>43.25</td>
      <td>2.5</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2024-04-01 00:41:12</td>
      <td>2024-04-01 00:55:29</td>
      <td>1.0</td>
      <td>5.6</td>
      <td>1.0</td>
      <td>N</td>
      <td>264</td>
      <td>264</td>
      <td>1</td>
      <td>25.4</td>
      <td>1.0</td>
      <td>0.5</td>
      <td>10.00</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>37.90</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>




```python
station_demand.head(3)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>pickup_station</th>
      <th>group</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Low</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Low</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Low</td>
    </tr>
  </tbody>
</table>
</div>




```python
weather.head(4)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>temperature_2m</th>
      <th>relative_humidity_2m (%)</th>
      <th>apparent_temperature</th>
      <th>precipitation</th>
      <th>lat</th>
      <th>long</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2019-01-01 00:00:00+00:00</td>
      <td>5.6575</td>
      <td>94</td>
      <td>1.943899</td>
      <td>1.1</td>
      <td>40.71427</td>
      <td>-74.00597</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2019-01-01 01:00:00+00:00</td>
      <td>5.9075</td>
      <td>96</td>
      <td>2.698992</td>
      <td>2.9</td>
      <td>40.71427</td>
      <td>-74.00597</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2019-01-01 02:00:00+00:00</td>
      <td>6.4575</td>
      <td>95</td>
      <td>3.667387</td>
      <td>2.2</td>
      <td>40.71427</td>
      <td>-74.00597</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2019-01-01 03:00:00+00:00</td>
      <td>6.7575</td>
      <td>95</td>
      <td>4.112215</td>
      <td>10.1</td>
      <td>40.71427</td>
      <td>-74.00597</td>
    </tr>
  </tbody>
</table>
</div>




```python
data.shape
```




    (137994, 3)




```python
# get holidays in the US from beginning to current
us_holidays = holidays.UnitedStates(years=list(range(min(data.ride_datetime.dt.year), 
                                                     max(data.ride_datetime.dt.year)+1)))
us_holidays = pd.DataFrame(us_holidays.items(), columns=['date', 'name'])
us_holidays = us_holidays.sort_values('date').reset_index(drop=True)
```


```python
station_demand.group = station_demand.group.str.lower()
```

### Visualisation


```python
# summary statistics
data.pivot(columns='demand_group', index='ride_datetime', values='avg_hourly_rides').describe().T
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>count</th>
      <th>mean</th>
      <th>std</th>
      <th>min</th>
      <th>25%</th>
      <th>50%</th>
      <th>75%</th>
      <th>max</th>
    </tr>
    <tr>
      <th>demand_group</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>high</th>
      <td>45993.0</td>
      <td>123.773394</td>
      <td>104.464494</td>
      <td>1.0</td>
      <td>29.3333</td>
      <td>110.40000</td>
      <td>183.93330</td>
      <td>534.2667</td>
    </tr>
    <tr>
      <th>low</th>
      <td>46000.0</td>
      <td>2.926801</td>
      <td>1.363811</td>
      <td>1.0</td>
      <td>1.8409</td>
      <td>2.73885</td>
      <td>3.71015</td>
      <td>12.6429</td>
    </tr>
    <tr>
      <th>medium</th>
      <td>46001.0</td>
      <td>53.522088</td>
      <td>43.108503</td>
      <td>1.0</td>
      <td>15.0968</td>
      <td>49.68750</td>
      <td>75.00000</td>
      <td>276.5000</td>
    </tr>
  </tbody>
</table>
</div>



- All demand group had 1 ride in a certain hour
- Low demand group had a maximum of 12 rides in an hour. We will drop rows for low demand group since they won't be of much importance since the aim is to accurately predict demand for appropriate logistics.

#### Distribution of hourly rides by group


```python
plt.figure(figsize=(8,4.3))
sns.boxplot(data, x='demand_group', y='avg_hourly_rides', hue='demand_group', 
            order=['low', 'medium', 'high'])
plt.title('Average Hourly rides by Demand group', loc='left', fontsize=11, fontweight='bold')
plt.ylabel('Taxi Rides')
plt.show()
```


    
![png](output_16_0.png)
    


#### Daily demand by group


```python
weekday_rides = (
    data.assign(hour=data.ride_datetime.dt.hour,
                weekday = data.ride_datetime.dt.weekday)
        .groupby(['weekday', 'hour', 'demand_group']).avg_hourly_rides.mean()
        .unstack(2)
)
```


```python
# fig, ax= plt.subplots(figsize=(10,4), dpi=150)
ax = weekday_rides[['low', 'medium', 'high']].plot(subplots=True, layout=(1,3), figsize=(11,4),
                       title='Average hourly taxi demand during the week',
                       ylabel='Hourly Demand', xlabel='Time of week', fontsize=8)
plt.xticks([i * 24 for i in range(7)], ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
plt.tight_layout()
plt.show()
```


    
![png](output_19_0.png)
    


- For all demand areas, demand is lowest on Sunday
- For low demand areas, the demand for rides increases during the week
- For medium and high, it increases from Monday and relatively remains the same throughout the week except on weekends

#### Daily demand in demand areas during holidays and non-holidays


```python
weekday_rides = (
    data.assign(hour=data.ride_datetime.dt.hour,
                is_holiday=data.ride_datetime.dt.date.isin(us_holidays.date),
                weekday = data.ride_datetime.dt.weekday)
        .groupby(['weekday', 'hour', 'demand_group', 'is_holiday']).avg_hourly_rides.mean()
        .reset_index(level=[2,3])
)
```


```python
d = sns.relplot(weekday_rides, x=range(0,len(weekday_rides)), y='avg_hourly_rides', 
                hue='is_holiday', col='demand_group', kind='line', 
                aspect=.9, height=4, facet_kws={'sharey':False}, 
                col_order=['low', 'medium', 'high'])

d.set(xticks=[i * 24*7 for i in range(7)], ylabel='Hourly Rides', 
      xlabel='Time of week')
d.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
plt.suptitle('Average hourly taxi demand during the week', y=1.0, fontsize=11, x=0.23, fontweight='bold')
d.despine();
```


    
![png](output_23_0.png)
    


- Demand is also affected by holiday and non-holidays. Lower demand during holidays


```python
demand_monthly_rides = (
    data
    .pivot(columns='demand_group', index='ride_datetime', values='avg_hourly_rides')
    .rolling('28D').mean()
    .reset_index().melt(id_vars='ride_datetime', value_name='rides')
)
```


```python
sns.relplot(demand_monthly_rides, x='ride_datetime', y='rides', hue='demand_group', 
            col='demand_group', kind='line', aspect=1, height=4, legend=False,
            facet_kws={'sharey':False}, col_order=['low', 'medium', 'high'])
plt.suptitle('Taxi Demand (28-Day moving average)', y=1.0, fontsize=11, x=0.23, fontweight='bold');
```


    
![png](output_26_0.png)
    



```python
data.pivot(columns='demand_group', index='ride_datetime', 
           values='avg_hourly_rides').resample('ME').mean()[14:35]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>demand_group</th>
      <th>high</th>
      <th>low</th>
      <th>medium</th>
    </tr>
    <tr>
      <th>ride_datetime</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2020-03-31</th>
      <td>94.999462</td>
      <td>2.608939</td>
      <td>44.704695</td>
    </tr>
    <tr>
      <th>2020-04-30</th>
      <td>5.030768</td>
      <td>1.402341</td>
      <td>4.618032</td>
    </tr>
    <tr>
      <th>2020-05-31</th>
      <td>6.809483</td>
      <td>1.702374</td>
      <td>5.828882</td>
    </tr>
    <tr>
      <th>2020-06-30</th>
      <td>13.648428</td>
      <td>1.687634</td>
      <td>8.414476</td>
    </tr>
    <tr>
      <th>2020-07-31</th>
      <td>20.579858</td>
      <td>1.741007</td>
      <td>11.132022</td>
    </tr>
    <tr>
      <th>2020-08-31</th>
      <td>26.703521</td>
      <td>1.828960</td>
      <td>14.027971</td>
    </tr>
    <tr>
      <th>2020-09-30</th>
      <td>39.419459</td>
      <td>1.878191</td>
      <td>20.086987</td>
    </tr>
    <tr>
      <th>2020-10-31</th>
      <td>49.962599</td>
      <td>1.957599</td>
      <td>25.324542</td>
    </tr>
    <tr>
      <th>2020-11-30</th>
      <td>46.365617</td>
      <td>1.899701</td>
      <td>23.548067</td>
    </tr>
    <tr>
      <th>2020-12-31</th>
      <td>43.240019</td>
      <td>1.840649</td>
      <td>21.347912</td>
    </tr>
    <tr>
      <th>2021-01-31</th>
      <td>40.666387</td>
      <td>1.873252</td>
      <td>20.158661</td>
    </tr>
    <tr>
      <th>2021-02-28</th>
      <td>45.368678</td>
      <td>1.942672</td>
      <td>22.950529</td>
    </tr>
    <tr>
      <th>2021-03-31</th>
      <td>57.899257</td>
      <td>2.104313</td>
      <td>29.319254</td>
    </tr>
    <tr>
      <th>2021-04-30</th>
      <td>69.740868</td>
      <td>2.218365</td>
      <td>34.177286</td>
    </tr>
    <tr>
      <th>2021-05-31</th>
      <td>80.758318</td>
      <td>2.291611</td>
      <td>38.524638</td>
    </tr>
    <tr>
      <th>2021-06-30</th>
      <td>96.238631</td>
      <td>2.574683</td>
      <td>44.429747</td>
    </tr>
    <tr>
      <th>2021-07-31</th>
      <td>92.131059</td>
      <td>2.577831</td>
      <td>41.667154</td>
    </tr>
    <tr>
      <th>2021-08-31</th>
      <td>91.292338</td>
      <td>2.598810</td>
      <td>41.334366</td>
    </tr>
    <tr>
      <th>2021-09-30</th>
      <td>102.213037</td>
      <td>2.712828</td>
      <td>46.772900</td>
    </tr>
    <tr>
      <th>2021-10-31</th>
      <td>120.024783</td>
      <td>2.803169</td>
      <td>53.172838</td>
    </tr>
    <tr>
      <th>2021-11-30</th>
      <td>126.917848</td>
      <td>2.816906</td>
      <td>53.465793</td>
    </tr>
  </tbody>
</table>
</div>



#### Correlation


```python
# remove UTC timezone to none
weather.date = weather.date.dt.tz_convert(None)
```


```python
weather.select_dtypes('number').describe()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>temperature_2m</th>
      <th>relative_humidity_2m (%)</th>
      <th>apparent_temperature</th>
      <th>precipitation</th>
      <th>lat</th>
      <th>long</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>46728.000000</td>
      <td>46728.000000</td>
      <td>46728.000000</td>
      <td>46728.000000</td>
      <td>4.672800e+04</td>
      <td>46728.00000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>12.620202</td>
      <td>66.438388</td>
      <td>10.750268</td>
      <td>0.135951</td>
      <td>4.071427e+01</td>
      <td>-74.00597</td>
    </tr>
    <tr>
      <th>std</th>
      <td>9.670907</td>
      <td>20.125199</td>
      <td>12.236330</td>
      <td>1.540261</td>
      <td>1.421101e-14</td>
      <td>0.00000</td>
    </tr>
    <tr>
      <th>min</th>
      <td>-16.892500</td>
      <td>8.000000</td>
      <td>-24.796299</td>
      <td>0.000000</td>
      <td>4.071427e+01</td>
      <td>-74.00597</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>4.857500</td>
      <td>50.000000</td>
      <td>0.704694</td>
      <td>0.000000</td>
      <td>4.071427e+01</td>
      <td>-74.00597</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>12.207500</td>
      <td>68.000000</td>
      <td>9.658443</td>
      <td>0.000000</td>
      <td>4.071427e+01</td>
      <td>-74.00597</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>20.807500</td>
      <td>84.000000</td>
      <td>21.259793</td>
      <td>0.000000</td>
      <td>4.071427e+01</td>
      <td>-74.00597</td>
    </tr>
    <tr>
      <th>max</th>
      <td>37.257500</td>
      <td>100.000000</td>
      <td>42.437160</td>
      <td>100.400000</td>
      <td>4.071427e+01</td>
      <td>-74.00597</td>
    </tr>
  </tbody>
</table>
</div>




```python
corr = (
    data.pivot(columns='demand_group', index='ride_datetime', values='avg_hourly_rides')
    .reset_index()
    .merge(weather, left_on='ride_datetime', right_on='date')
    .eval('mean_temp = (apparent_temperature + temperature_2m)/2')
    .eval('temp_diff = abs(apparent_temperature - temperature_2m)')
    .drop(columns=['lat', 'long'])
    .corr(numeric_only=True)
)
```


```python
fig, ax = plt.subplots(figsize=(9,5), dpi=100)
sns.heatmap(corr, mask=np.triu(corr), fmt='.2f', annot=True, 
            annot_kws={'fontsize':8}, cbar=False)
plt.title('Correlation Matrix', loc='left')
plt.xticks(fontsize=8, rotation=20)
plt.yticks(fontsize=8);
```


    
![png](output_32_0.png)
    


## Feature Engineering & Preprocessing

- We will create time-related features
- Merge weather data
- Encode categorical variables and transform numerical variables
- Average the temperature and apparent temperature and absolute difference since they show perfect correlation (from correlation matrix)
- Filter data and select data from May 2021 till present. We will also select datasets for medium and high-demand areas since they are major area of focus.

The first three steps will be done in a pipeline of functions


```python
criteria = (
    (data.ride_datetime >= pd.to_datetime('2021-05-01')) & 
    (data.ride_datetime <= pd.to_datetime('2024-04-01'))
)

filtered_data = data.loc[criteria].query("demand_group != 'low'").reset_index(drop=True)
```


```python
# filter out low from station demand
station_demand = station_demand.query("group != 'low'").reset_index(drop=True)
```

#### __Visualise weather data__


```python
fig, ax = plt.subplots(1,2, figsize=(8,4))
sns.boxplot(filtered_data, y='avg_hourly_rides', x='demand_group', ax=ax[0], hue='demand_group')
ax[0].set_title('Original values')

sns.boxplot(filtered_data.assign(
    avg_hourly_rides = filtered_data.avg_hourly_rides.map(np.sqrt)
), x='demand_group', y='avg_hourly_rides', ax=ax[1],hue='demand_group')
ax[1].set_title('Square-root Transformed')
fig.tight_layout();
```


    
![png](output_37_0.png)
    


- No group is affected by outliers. Hence, we will use them in their original values


```python
plt.figure(figsize=(11,3.5))
for i, col in enumerate(weather.columns[1:5]):
    plt.subplot(1,4,i+1)
    sns.boxplot(weather, y=col)
    plt.title(col, fontsize=11, fontweight='bold')
    plt.ylabel('')
plt.tight_layout()
plt.show()
```


    
![png](output_39_0.png)
    


- We will classify precipitation (in millimeters) into groups.
    - 'no' -> 0 mm
    - 'light' -> between 0 and 2.6 (exclusive)
    - 'moderate' -> between 2.6 and 7.6
    - 'heavy' -> above 7.6

#### __Helper data preprocessing functions__


```python
def season(x):
    if x in range(3,6): return 'spring'
    elif x in range(6,9): return 'summer'
    elif x in range(9,12): return 'fall'
    else: return 'winter'
```


```python
def rain_class(x):
    if x == 0: return 'no'
    elif 0 < x < 2.6: return 'light'
    elif 2.6 <= x <= 7.6: return 'moderate'
    elif x > 7.6: return 'heavy'
    else: return 'invalid'
    return x

def is_snow(x):
    if x < 1: 
        return 1
    else:
        return 0
```


```python
weather.precipitation.map(rain_class).value_counts(normalize=True).plot.bar(
    alpha=0.8, rot=0, edgecolor='black', title='Relative Frequency Distribution', 
    ylabel='Relative frequency', xlabel='Rain Type', ylim=(0,1)
);
```


    
![png](output_44_0.png)
    


- New York weather is mostly characterised by no rainfall


```python
def feature_engineer(df):
    """
    Function 
    a. merges weather to demand data
    b. creates some time features (holiday and season)
    c. bins precipitation into four classes and drops precipitation
    d. dummy encode demand group variable
    
    Returns
    -------
    df: pandas dataframe with engineered features
    """
    # merge weather
    df = df.merge(weather, left_on='ride_datetime', right_on='date'
                 ).drop(['date', 'lat', 'long'], axis=1)

    df = df.assign(
        mean_temp = (df.apparent_temperature + df.temperature_2m)/2,
        abs_temp_diff = np.abs(df.temperature_2m - df.apparent_temperature)
        )
    # drop temperature features
    df = df.drop(['temperature_2m', 'apparent_temperature'], axis=1)

    # create holiday and season
    df = df.assign(holiday=1*df.ride_datetime.dt.date.isin(us_holidays.date),
                   season = df.ride_datetime.dt.month.map(season)
                  )

    # create rain class
    df['rain_class'] = df.precipitation.map(rain_class)
    df['is_snow'] = df.mean_temp.map(is_snow)
    # remove precipitation after creating rain class
    df = df.drop('precipitation', axis=1)
    # convert to dummy variable
    df.demand_group = df.demand_group.map({'high':1, 'medium':0})
    return df
```


```python
def prepare_test(df):
    """
    Function
    a. selects rides paid by cash or card and rows where total amount is positive
    b. converts pickup time to nearest hour
    c. groups the pickup station and finding rides at particular hour of day
    d. renames grouped data and selects only data for April 2024
    e. groups pickup stations based on demand group, groups them and gets their mean hourly demand

    Returns
    -------
    prepared test data
    -------
    """
    # filter rows where taxi customer paid by cash or card and total amount is positive
    df = df.query('(payment_type < 2) & (total_amount > 0)').reset_index(drop=True)
    
    # convert to hour, group by pickup station and time
    df['tpep_pickup_datetime'] = pd.DatetimeIndex(df['tpep_pickup_datetime']).floor('h')
    test = df.groupby(
        ['tpep_pickup_datetime', 'PULocationID']).agg({'payment_type' : 'count'}).reset_index()
    test = test.rename(
        {'tpep_pickup_datetime' : 'ride_datetime', 
         'payment_type' : 'hourly_rides',
         'PULocationID' : 'pickup_station'
        }, axis=1)

    # filter out rows for april
    april = (
        (test.ride_datetime >= pd.to_datetime('2024-04-01 00:00:00')) & 
        (test.ride_datetime < pd.to_datetime('2024-05-01 00:00:00'))
    )
    test = test.loc[april]

    # assign to groups
    high = station_demand.query("group == 'high'").pickup_station.tolist()
    test['demand_group'] = test.pickup_station.apply(lambda x: 'high' if x in high else 'medium')

    test = test.groupby(['ride_datetime', 'demand_group']).hourly_rides.mean()
    test = test.reset_index().rename({'hourly_rides' : 'avg_hourly_rides'}, axis=1)
    return test
```


```python
def preprocessor(df, data_type='train'):
    """
    Returns preprocessors performed on train data which will be used for transformation
    """
    if data_type == 'train':
        df = feature_engineer(df)
        # get time features
        time_features = ['weekend', 'hour', 'month', 'year', 'week', 'quarter', 
                         'day_of_year', 'day_of_week']
        date_features_fit = DatetimeFeatures(variables='ride_datetime', 
                                             features_to_extract=time_features,
                                             drop_original=False
                                            ).fit(df)

        # one hot encode
        one_hot = OneHotEncoder(variables=['rain_class', 'season']).fit(df)
        return date_features_fit, one_hot
    return None, None
```


```python
def preprocess_data(df, onehot_encoder=None, date_preprocessor=None):
    """
    Preprocesses both train and test data
    Returns
    -------
    Preprocessed data
    """
    df = feature_engineer(df)
    
    if onehot_encoder is None and date_preprocessor is None:
        raise TypeError ('onehot_encoder and date_preprocessor must not be None')

    time_features = date_preprocessor.transform(df)
    df = onehot_encoder.transform(df)
    
    same_cols = time_features.columns.intersection(df.columns)
    df = df.merge(time_features, on=same_cols.tolist())

    # remove rain_class and season
    df = df.drop(['rain_class', 'season'], axis=1)
    # remove ride_datetime_ from created time features like ride_datetime_month etc
    df.columns = df.columns.str.replace('ride_datetime_|[\s(%)]', '', regex=True)
    df = df.set_index('ride_datetime')
    return df
```

#### Data Preprocessing


```python
date_encoder, onehot_encoder = preprocessor(filtered_data, 'train')
```


```python
filtered_data = preprocess_data(filtered_data, onehot_encoder, date_encoder)
```


```python
test = prepare_test(new_data)
test = preprocess_data(test, onehot_encoder, date_encoder)
```


```python
filtered_data.shape, test.shape
```




    ((51162, 23), (1440, 23))



#### __Checking for missing values__


```python
# checking for missing values
filtered_data.isna().sum().any(), test.isna().sum().any()
```




    (False, False)




```python
filtered_data.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>avg_hourly_rides</th>
      <th>demand_group</th>
      <th>relative_humidity_2m</th>
      <th>mean_temp</th>
      <th>abs_temp_diff</th>
      <th>holiday</th>
      <th>is_snow</th>
      <th>rain_class_no</th>
      <th>rain_class_light</th>
      <th>rain_class_moderate</th>
      <th>...</th>
      <th>season_fall</th>
      <th>season_winter</th>
      <th>weekend</th>
      <th>hour</th>
      <th>month</th>
      <th>year</th>
      <th>week</th>
      <th>quarter</th>
      <th>day_of_year</th>
      <th>day_of_week</th>
    </tr>
    <tr>
      <th>ride_datetime</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2021-05-01</th>
      <td>53.60</td>
      <td>1</td>
      <td>40</td>
      <td>10.381534</td>
      <td>6.251932</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>5</td>
      <td>2021</td>
      <td>17</td>
      <td>2</td>
      <td>121</td>
      <td>5</td>
    </tr>
    <tr>
      <th>2021-05-01</th>
      <td>36.75</td>
      <td>0</td>
      <td>40</td>
      <td>10.381534</td>
      <td>6.251932</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>5</td>
      <td>2021</td>
      <td>17</td>
      <td>2</td>
      <td>121</td>
      <td>5</td>
    </tr>
  </tbody>
</table>
<p>2 rows × 23 columns</p>
</div>




```python
test.head(2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>avg_hourly_rides</th>
      <th>demand_group</th>
      <th>relative_humidity_2m</th>
      <th>mean_temp</th>
      <th>abs_temp_diff</th>
      <th>holiday</th>
      <th>is_snow</th>
      <th>rain_class_no</th>
      <th>rain_class_light</th>
      <th>rain_class_moderate</th>
      <th>...</th>
      <th>season_fall</th>
      <th>season_winter</th>
      <th>weekend</th>
      <th>hour</th>
      <th>month</th>
      <th>year</th>
      <th>week</th>
      <th>quarter</th>
      <th>day_of_year</th>
      <th>day_of_week</th>
    </tr>
    <tr>
      <th>ride_datetime</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2024-04-01</th>
      <td>41.933333</td>
      <td>1</td>
      <td>37</td>
      <td>11.263631</td>
      <td>3.587739</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>4</td>
      <td>2024</td>
      <td>14</td>
      <td>2</td>
      <td>92</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2024-04-01</th>
      <td>6.063492</td>
      <td>0</td>
      <td>37</td>
      <td>11.263631</td>
      <td>3.587739</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>4</td>
      <td>2024</td>
      <td>14</td>
      <td>2</td>
      <td>92</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>2 rows × 23 columns</p>
</div>



## __Modelling__

Here, we will split our data into train and validation sets. The validation set would be used to validate the performance of the model. To tune hyperparameters for optimal values, a 5-fold cross-validation (Time series type) will be used the train data will be so


```python
class Model:
    def __init__(self):
        self.is_fitted = False
        self.model = None
        
    def train(self, model, X, y, eval_set=None, epochs=50):
        self.model = model
        self.is_fitted = True
        self.eval_set = eval_set
        if self.eval_set is None:
            return self.model.fit(X, y)
        elif self.model.__class__.__name__ == 'LGBMRegressor' and self.eval_set is not None:
            return self.model.fit(
                X, y, 
                eval_set=self.eval_set, 
                eval_metric='rmse',
                callbacks=[lgb.callback.early_stopping(epochs, first_metric_only=True)]
        )
        elif self.model.__class__.__name__ == 'CatBoostRegressor' and self.eval_set is not None:
            return self.model.fit(X, y, eval_set=self.eval_set)
        else:
            return self.model.fit(X, y)
        
    def predict(self, X):
        if self.is_fitted:
            return self.model.predict(X)
        else:
            raise Exception(f'{self.model.__class__.__name__} not fitted')
```


```python
def model_metrics(model, x, y, sqrt=None):
    if sqrt:
        ypred = model.predict(x)**2
        y = y**2
    else:
        ypred = model.predict(x)
    rmse = root_mean_squared_error(y, ypred)
    mae = mean_absolute_error(y, ypred)
    return f'RMSE: {rmse:.4f}\tMAE: {mae:.4f}'
```


```python
def filter_data(df, demand_type='medium'):
    """
    Filters data based on demand type
    """
    demand_map = {'Medium':0, 'High':1}
    demand_type = demand_type.title()
    if demand_type == 'Medium':
        criteria = df.demand_group == demand_map.get(demand_type)
        return df.loc[criteria, :].drop('demand_group', axis=1)
    elif demand_type == 'High':
        criteria = df.demand_group == demand_map.get(demand_type)
        return df.loc[criteria, :].drop('demand_group', axis=1)
```


```python
def create_demand_features(train, test, hours):
    """
    Creates percentage changes and rolling means and deviations of taxi demands
    train : train dataset pd.DataFrame
    test : test dataset pd.DataFrame
    """
    df = pd.concat([train, test])
    for h in hours:
        # lags
        df[f'demand_last_{h}_hr'] = df.avg_hourly_rides.shift(h)
        # rate of change
        df[f'demand_pct_chg_last_{h}_hr'] = df.avg_hourly_rides.shift().pct_change(h)
        # variance
        df[f'demand_var_last_{h+1}_hr'] = df.avg_hourly_rides.shift().rolling(f'{h+1}h').std()
        # mean
        df[f'demand_avg_last_{h+1}_hr'] = df.avg_hourly_rides.shift().rolling(f'{h+1}h').mean()
    
    df = df.filter(regex='^demand_[a-z_0-9]+_hr$|demand_group')
    a, b = df.loc[train.index], df.loc[test.index]
    return a, b
```


```python
def cross_validate_scores(model, x, y, cv, scoring='neg_root_mean_squared_error'):
    cvs = cross_val_score(model, x, y, scoring=scoring, cv=cv, n_jobs=-1)
    return -cvs
```

### __Splitting into train and validation sets__

> Data will be split into two: a train and validation sets. <br>The train data will be used to fit a model and its performance evaluated on the validation data. 
<br>The validation data will contain demands from Jan-March 2024. <br>The train data will be split in a time series fashion using a 5-fold classification

__Create demand features__


```python
# get the newly generated demand features
train_demand, test_demand = [], []

for group in ['high', 'medium']:
    res = create_demand_features(train=filter_data(filtered_data, group), 
                                 test=filter_data(test, group), 
                                 hours=[1,5,8,17,23])
    train_demand.append(res[0].assign(demand_group={'medium':0, 'high':1}.get(group)))
    test_demand.append(res[1].assign(demand_group=group))

train_demand = pd.concat(train_demand).sort_index()
test_demand = pd.concat(test_demand).sort_index()
```


```python
# test size should contain 3 months data like in validation data
tsplit = TimeSeriesSplit(n_splits=5, test_size=24*90*2)
```


```python
TARGET = 'avg_hourly_rides'
```


```python
train_set = pd.concat([filtered_data, train_demand.drop('demand_group', axis=1)], axis=1)[
            train_demand.index < pd.to_datetime('2024-01-01')
]
valid_set = pd.concat([filtered_data, train_demand.drop('demand_group', axis=1)], axis=1)[
            train_demand.index >= pd.to_datetime('2024-01-01')
]
```


```python
xtrain, ytrain = train_set.iloc[:, 1:], train_set[TARGET]
xval, yval = valid_set.iloc[:, 1:], valid_set[TARGET]
```

#### __Naive Model__

A model that predicts the average hourly demand every month


```python
hourly_preds = ytrain.groupby(
    [xtrain.hour, xtrain.demand_group, xtrain.month]).mean().reset_index()
```


```python
avg_5_predictions = (
    filtered_data.drop(TARGET, axis=1).reset_index()
    .merge(hourly_preds, on=['hour', 'demand_group', 'month'], how='left')
    .set_index('ride_datetime')[TARGET]
)
avg_5_predictions.name = avg_5_predictions.name + '_pred'
```


```python
# concatenate 
df = pd.concat([filtered_data.avg_hourly_rides, avg_5_predictions], axis=1)
```


```python
df = (
    df
    .eval('sq_error = (avg_hourly_rides - avg_hourly_rides_pred)**2')
    .assign(abs_error = np.abs(df.avg_hourly_rides - df.avg_hourly_rides_pred))
)
```


```python
# performance on train
print((f'RMSE: {np.sqrt(df.loc[xtrain.index].sq_error.mean()):.4f}\tMAE: {df.loc[xtrain.index].abs_error.mean():.4f}'))
```

    RMSE: 25.4509	MAE: 18.0859
    


```python
# perfor,amce on validation set
print((f'RMSE: {np.sqrt(df.loc[xval.index].sq_error.mean()):.4f}\tMAE: {df.loc[xval.index].abs_error.mean():.4f}'))
```

    RMSE: 28.6607	MAE: 20.3629
    


```python
seed = 234
```


```python
# instantiate model class
regressor = Model()
```

#### __LightGBM Model__


```python
lgbm = lgb.LGBMRegressor(n_estimators=2500, min_child_samples=3, subsample=0.7, 
                         learning_rate=0.07, min_child_weight=1, random_state=seed, 
                         colsample_bytree=0.6, reg_alpha=10, reg_lambda=1, n_jobs=-1,
                         max_depth=6, verbose=-1, num_leaves=20,importance_type='gain')
```


```python
cvs = cross_validate_scores(lgbm, xtrain, ytrain, cv=tsplit)
print(cvs)
print(f'{cvs.mean():.3f} +- {cvs.std():.3f}')
```

    [10.70352319 10.04906408  9.65357803  8.97845102 12.77581122]
    10.432 +- 1.299
    


```python
# training and evaluating on validation set
regressor.train(lgbm, xtrain, ytrain, [(xval, yval)])
```

    Training until validation scores don't improve for 50 rounds
    Early stopping, best iteration is:
    [1961]	valid_0's rmse: 13.3635	valid_0's l2: 178.583
    Evaluated only: rmse
    




<style>#sk-container-id-1 {
  /* Definition of color scheme common for light and dark mode */
  --sklearn-color-text: black;
  --sklearn-color-line: gray;
  /* Definition of color scheme for unfitted estimators */
  --sklearn-color-unfitted-level-0: #fff5e6;
  --sklearn-color-unfitted-level-1: #f6e4d2;
  --sklearn-color-unfitted-level-2: #ffe0b3;
  --sklearn-color-unfitted-level-3: chocolate;
  /* Definition of color scheme for fitted estimators */
  --sklearn-color-fitted-level-0: #f0f8ff;
  --sklearn-color-fitted-level-1: #d4ebff;
  --sklearn-color-fitted-level-2: #b3dbfd;
  --sklearn-color-fitted-level-3: cornflowerblue;

  /* Specific color for light theme */
  --sklearn-color-text-on-default-background: var(--sg-text-color, var(--theme-code-foreground, var(--jp-content-font-color1, black)));
  --sklearn-color-background: var(--sg-background-color, var(--theme-background, var(--jp-layout-color0, white)));
  --sklearn-color-border-box: var(--sg-text-color, var(--theme-code-foreground, var(--jp-content-font-color1, black)));
  --sklearn-color-icon: #696969;

  @media (prefers-color-scheme: dark) {
    /* Redefinition of color scheme for dark theme */
    --sklearn-color-text-on-default-background: var(--sg-text-color, var(--theme-code-foreground, var(--jp-content-font-color1, white)));
    --sklearn-color-background: var(--sg-background-color, var(--theme-background, var(--jp-layout-color0, #111)));
    --sklearn-color-border-box: var(--sg-text-color, var(--theme-code-foreground, var(--jp-content-font-color1, white)));
    --sklearn-color-icon: #878787;
  }
}

#sk-container-id-1 {
  color: var(--sklearn-color-text);
}

#sk-container-id-1 pre {
  padding: 0;
}

#sk-container-id-1 input.sk-hidden--visually {
  border: 0;
  clip: rect(1px 1px 1px 1px);
  clip: rect(1px, 1px, 1px, 1px);
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
  position: absolute;
  width: 1px;
}

#sk-container-id-1 div.sk-dashed-wrapped {
  border: 1px dashed var(--sklearn-color-line);
  margin: 0 0.4em 0.5em 0.4em;
  box-sizing: border-box;
  padding-bottom: 0.4em;
  background-color: var(--sklearn-color-background);
}

#sk-container-id-1 div.sk-container {
  /* jupyter's `normalize.less` sets `[hidden] { display: none; }`
     but bootstrap.min.css set `[hidden] { display: none !important; }`
     so we also need the `!important` here to be able to override the
     default hidden behavior on the sphinx rendered scikit-learn.org.
     See: https://github.com/scikit-learn/scikit-learn/issues/21755 */
  display: inline-block !important;
  position: relative;
}

#sk-container-id-1 div.sk-text-repr-fallback {
  display: none;
}

div.sk-parallel-item,
div.sk-serial,
div.sk-item {
  /* draw centered vertical line to link estimators */
  background-image: linear-gradient(var(--sklearn-color-text-on-default-background), var(--sklearn-color-text-on-default-background));
  background-size: 2px 100%;
  background-repeat: no-repeat;
  background-position: center center;
}

/* Parallel-specific style estimator block */

#sk-container-id-1 div.sk-parallel-item::after {
  content: "";
  width: 100%;
  border-bottom: 2px solid var(--sklearn-color-text-on-default-background);
  flex-grow: 1;
}

#sk-container-id-1 div.sk-parallel {
  display: flex;
  align-items: stretch;
  justify-content: center;
  background-color: var(--sklearn-color-background);
  position: relative;
}

#sk-container-id-1 div.sk-parallel-item {
  display: flex;
  flex-direction: column;
}

#sk-container-id-1 div.sk-parallel-item:first-child::after {
  align-self: flex-end;
  width: 50%;
}

#sk-container-id-1 div.sk-parallel-item:last-child::after {
  align-self: flex-start;
  width: 50%;
}

#sk-container-id-1 div.sk-parallel-item:only-child::after {
  width: 0;
}

/* Serial-specific style estimator block */

#sk-container-id-1 div.sk-serial {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: var(--sklearn-color-background);
  padding-right: 1em;
  padding-left: 1em;
}


/* Toggleable style: style used for estimator/Pipeline/ColumnTransformer box that is
clickable and can be expanded/collapsed.
- Pipeline and ColumnTransformer use this feature and define the default style
- Estimators will overwrite some part of the style using the `sk-estimator` class
*/

/* Pipeline and ColumnTransformer style (default) */

#sk-container-id-1 div.sk-toggleable {
  /* Default theme specific background. It is overwritten whether we have a
  specific estimator or a Pipeline/ColumnTransformer */
  background-color: var(--sklearn-color-background);
}

/* Toggleable label */
#sk-container-id-1 label.sk-toggleable__label {
  cursor: pointer;
  display: block;
  width: 100%;
  margin-bottom: 0;
  padding: 0.5em;
  box-sizing: border-box;
  text-align: center;
}

#sk-container-id-1 label.sk-toggleable__label-arrow:before {
  /* Arrow on the left of the label */
  content: "▸";
  float: left;
  margin-right: 0.25em;
  color: var(--sklearn-color-icon);
}

#sk-container-id-1 label.sk-toggleable__label-arrow:hover:before {
  color: var(--sklearn-color-text);
}

/* Toggleable content - dropdown */

#sk-container-id-1 div.sk-toggleable__content {
  max-height: 0;
  max-width: 0;
  overflow: hidden;
  text-align: left;
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-0);
}

#sk-container-id-1 div.sk-toggleable__content.fitted {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-0);
}

#sk-container-id-1 div.sk-toggleable__content pre {
  margin: 0.2em;
  border-radius: 0.25em;
  color: var(--sklearn-color-text);
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-0);
}

#sk-container-id-1 div.sk-toggleable__content.fitted pre {
  /* unfitted */
  background-color: var(--sklearn-color-fitted-level-0);
}

#sk-container-id-1 input.sk-toggleable__control:checked~div.sk-toggleable__content {
  /* Expand drop-down */
  max-height: 200px;
  max-width: 100%;
  overflow: auto;
}

#sk-container-id-1 input.sk-toggleable__control:checked~label.sk-toggleable__label-arrow:before {
  content: "▾";
}

/* Pipeline/ColumnTransformer-specific style */

#sk-container-id-1 div.sk-label input.sk-toggleable__control:checked~label.sk-toggleable__label {
  color: var(--sklearn-color-text);
  background-color: var(--sklearn-color-unfitted-level-2);
}

#sk-container-id-1 div.sk-label.fitted input.sk-toggleable__control:checked~label.sk-toggleable__label {
  background-color: var(--sklearn-color-fitted-level-2);
}

/* Estimator-specific style */

/* Colorize estimator box */
#sk-container-id-1 div.sk-estimator input.sk-toggleable__control:checked~label.sk-toggleable__label {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-2);
}

#sk-container-id-1 div.sk-estimator.fitted input.sk-toggleable__control:checked~label.sk-toggleable__label {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-2);
}

#sk-container-id-1 div.sk-label label.sk-toggleable__label,
#sk-container-id-1 div.sk-label label {
  /* The background is the default theme color */
  color: var(--sklearn-color-text-on-default-background);
}

/* On hover, darken the color of the background */
#sk-container-id-1 div.sk-label:hover label.sk-toggleable__label {
  color: var(--sklearn-color-text);
  background-color: var(--sklearn-color-unfitted-level-2);
}

/* Label box, darken color on hover, fitted */
#sk-container-id-1 div.sk-label.fitted:hover label.sk-toggleable__label.fitted {
  color: var(--sklearn-color-text);
  background-color: var(--sklearn-color-fitted-level-2);
}

/* Estimator label */

#sk-container-id-1 div.sk-label label {
  font-family: monospace;
  font-weight: bold;
  display: inline-block;
  line-height: 1.2em;
}

#sk-container-id-1 div.sk-label-container {
  text-align: center;
}

/* Estimator-specific */
#sk-container-id-1 div.sk-estimator {
  font-family: monospace;
  border: 1px dotted var(--sklearn-color-border-box);
  border-radius: 0.25em;
  box-sizing: border-box;
  margin-bottom: 0.5em;
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-0);
}

#sk-container-id-1 div.sk-estimator.fitted {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-0);
}

/* on hover */
#sk-container-id-1 div.sk-estimator:hover {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-2);
}

#sk-container-id-1 div.sk-estimator.fitted:hover {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-2);
}

/* Specification for estimator info (e.g. "i" and "?") */

/* Common style for "i" and "?" */

.sk-estimator-doc-link,
a:link.sk-estimator-doc-link,
a:visited.sk-estimator-doc-link {
  float: right;
  font-size: smaller;
  line-height: 1em;
  font-family: monospace;
  background-color: var(--sklearn-color-background);
  border-radius: 1em;
  height: 1em;
  width: 1em;
  text-decoration: none !important;
  margin-left: 1ex;
  /* unfitted */
  border: var(--sklearn-color-unfitted-level-1) 1pt solid;
  color: var(--sklearn-color-unfitted-level-1);
}

.sk-estimator-doc-link.fitted,
a:link.sk-estimator-doc-link.fitted,
a:visited.sk-estimator-doc-link.fitted {
  /* fitted */
  border: var(--sklearn-color-fitted-level-1) 1pt solid;
  color: var(--sklearn-color-fitted-level-1);
}

/* On hover */
div.sk-estimator:hover .sk-estimator-doc-link:hover,
.sk-estimator-doc-link:hover,
div.sk-label-container:hover .sk-estimator-doc-link:hover,
.sk-estimator-doc-link:hover {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-3);
  color: var(--sklearn-color-background);
  text-decoration: none;
}

div.sk-estimator.fitted:hover .sk-estimator-doc-link.fitted:hover,
.sk-estimator-doc-link.fitted:hover,
div.sk-label-container:hover .sk-estimator-doc-link.fitted:hover,
.sk-estimator-doc-link.fitted:hover {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-3);
  color: var(--sklearn-color-background);
  text-decoration: none;
}

/* Span, style for the box shown on hovering the info icon */
.sk-estimator-doc-link span {
  display: none;
  z-index: 9999;
  position: relative;
  font-weight: normal;
  right: .2ex;
  padding: .5ex;
  margin: .5ex;
  width: min-content;
  min-width: 20ex;
  max-width: 50ex;
  color: var(--sklearn-color-text);
  box-shadow: 2pt 2pt 4pt #999;
  /* unfitted */
  background: var(--sklearn-color-unfitted-level-0);
  border: .5pt solid var(--sklearn-color-unfitted-level-3);
}

.sk-estimator-doc-link.fitted span {
  /* fitted */
  background: var(--sklearn-color-fitted-level-0);
  border: var(--sklearn-color-fitted-level-3);
}

.sk-estimator-doc-link:hover span {
  display: block;
}

/* "?"-specific style due to the `<a>` HTML tag */

#sk-container-id-1 a.estimator_doc_link {
  float: right;
  font-size: 1rem;
  line-height: 1em;
  font-family: monospace;
  background-color: var(--sklearn-color-background);
  border-radius: 1rem;
  height: 1rem;
  width: 1rem;
  text-decoration: none;
  /* unfitted */
  color: var(--sklearn-color-unfitted-level-1);
  border: var(--sklearn-color-unfitted-level-1) 1pt solid;
}

#sk-container-id-1 a.estimator_doc_link.fitted {
  /* fitted */
  border: var(--sklearn-color-fitted-level-1) 1pt solid;
  color: var(--sklearn-color-fitted-level-1);
}

/* On hover */
#sk-container-id-1 a.estimator_doc_link:hover {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-3);
  color: var(--sklearn-color-background);
  text-decoration: none;
}

#sk-container-id-1 a.estimator_doc_link.fitted:hover {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-3);
}
</style><div id="sk-container-id-1" class="sk-top-container"><div class="sk-text-repr-fallback"><pre>LGBMRegressor(colsample_bytree=0.6, importance_type=&#x27;gain&#x27;, learning_rate=0.07,
              max_depth=6, min_child_samples=3, min_child_weight=1,
              n_estimators=2500, n_jobs=-1, num_leaves=20, random_state=234,
              reg_alpha=10, reg_lambda=1, subsample=0.7, verbose=-1)</pre><b>In a Jupyter environment, please rerun this cell to show the HTML representation or trust the notebook. <br />On GitHub, the HTML representation is unable to render, please try loading this page with nbviewer.org.</b></div><div class="sk-container" hidden><div class="sk-item"><div class="sk-estimator fitted sk-toggleable"><input class="sk-toggleable__control sk-hidden--visually" id="sk-estimator-id-1" type="checkbox" checked><label for="sk-estimator-id-1" class="sk-toggleable__label fitted sk-toggleable__label-arrow fitted">&nbsp;LGBMRegressor<span class="sk-estimator-doc-link fitted">i<span>Fitted</span></span></label><div class="sk-toggleable__content fitted"><pre>LGBMRegressor(colsample_bytree=0.6, importance_type=&#x27;gain&#x27;, learning_rate=0.07,
              max_depth=6, min_child_samples=3, min_child_weight=1,
              n_estimators=2500, n_jobs=-1, num_leaves=20, random_state=234,
              reg_alpha=10, reg_lambda=1, subsample=0.7, verbose=-1)</pre></div> </div></div></div></div>




```python
print(model_metrics(lgbm, xtrain, ytrain))
```

    RMSE: 4.5074	MAE: 3.1373
    


```python
print(model_metrics(lgbm, xval, yval))
```

    RMSE: 13.3635	MAE: 7.4841
    

#### __CatBoost Model__


```python
catm = cat.CatBoostRegressor(n_estimators=2500, random_state=seed, verbose=0, 
                             rsm=0.7, l2_leaf_reg=10, learning_rate=0.06, 
                             od_wait=50, subsample=0.65, bootstrap_type='Bernoulli')
```


```python
cvs = cross_validate_scores(catm, xtrain, ytrain, cv=tsplit)
print(cvs)
print(f'{cvs.mean():.3f} +- {cvs.std():.3f}')
```

    [ 9.54868608  9.16007338  9.3025454   9.17622784 11.96613251]
    9.831 +- 1.077
    


```python
regressor.train(catm, xtrain, ytrain, [(xval, yval)])
```




    <catboost.core.CatBoostRegressor at 0x21d4b465550>




```python
print(model_metrics(catm, xtrain, ytrain))
```

    RMSE: 5.7964	MAE: 3.8829
    


```python
print(model_metrics(catm, xval, yval))
```

    RMSE: 13.2474	MAE: 7.3250
    

#### Model Predictions and forecast


```python
pred_df = pd.DataFrame(index=valid_set.index, columns=['demand_group', 'actual', 'naive', 'lgbm', 'catm'])
pred_df['demand_group'] = xval.demand_group.map({1:'High', 0:'Medium'})
pred_df['actual'] = yval
pred_df['naive'] = avg_5_predictions[avg_5_predictions.index >= xval.index[0]].values
for i, model in enumerate([lgbm, catm], start=3):
    pred = model.predict(xval)
    pred_df.iloc[:, i] = pred
```


```python
pred_df[['lgbm', 'catm']] = pred_df[['lgbm', 'catm']].map(float)

corr = pred_df.corr(numeric_only=True)

sns.heatmap(corr, mask=np.triu(corr), annot=True, cbar=False, cmap='coolwarm', alpha=0.7, fmt='.3f')
plt.title('Correlation between Actual vs Predictions', fontweight='bold', loc='left');
```


    
![png](output_95_0.png)
    



```python
(
    pn.ggplot(
        (pred_df.pivot(columns='demand_group', values=['actual', 'naive', 'lgbm', 'catm'])
                .resample('24h').mean()
                .melt(value_name='values', ignore_index=False)
                .rename(columns={None:'pred_type'})
                .reset_index()
                .query('pred_type != "naive"')
        ), pn.aes(x='ride_datetime', y='np.float64(values)', color='factor(pred_type)')) +
    pn.geom_line(size=0.7) +
    pn.facet_wrap('~demand_group', scales='free_y', nrow=2) +
    pn.theme_538() +
    pn.theme(figure_size=(12,6), 
             legend_key=pn.element_blank(),
             strip_background=pn.element_rect(fill='steelblue'),
             strip_text=pn.element_text(color='white', face='bold'),
             panel_grid=pn.element_blank(),
             plot_title=pn.element_text(hjust=0, face='bold'),
             legend_position_inside=(0.03,1.02),
             legend_position='inside') +
    pn.scale_x_date(date_labels='%b %d\n%Y', date_minor_breaks='1 day') +
    pn.labs(title='Actual vs Model Predictions (Daily Average)', x='Date', y='Taxi Demand', color='') +
    pn.scale_color_manual(values=('steelblue', 'orange', 'green'), labels=('Actual', 'CatBoost', 'LightGBM')) +
    pn.scale_y_continuous(expand=(0, 0, 0.1, 2))
)
```


    
![png](output_96_0.png)
    


Above figure shows the actual average daily demand versus the model predicted demands from Jan 1, 2024 to Mar 31, 2024. 
- Both models seem to better predict the demand for high-demand zones than medium-demand zones
- Both models seem to under-predict taxi demands for March 2024

### April Predictions


```python
# instantiate model class
regressor = Model()
```


```python
regressor.train(lgbm, pd.concat([xtrain, xval]), pd.concat([ytrain, yval]))
```




<style>#sk-container-id-2 {
  /* Definition of color scheme common for light and dark mode */
  --sklearn-color-text: black;
  --sklearn-color-line: gray;
  /* Definition of color scheme for unfitted estimators */
  --sklearn-color-unfitted-level-0: #fff5e6;
  --sklearn-color-unfitted-level-1: #f6e4d2;
  --sklearn-color-unfitted-level-2: #ffe0b3;
  --sklearn-color-unfitted-level-3: chocolate;
  /* Definition of color scheme for fitted estimators */
  --sklearn-color-fitted-level-0: #f0f8ff;
  --sklearn-color-fitted-level-1: #d4ebff;
  --sklearn-color-fitted-level-2: #b3dbfd;
  --sklearn-color-fitted-level-3: cornflowerblue;

  /* Specific color for light theme */
  --sklearn-color-text-on-default-background: var(--sg-text-color, var(--theme-code-foreground, var(--jp-content-font-color1, black)));
  --sklearn-color-background: var(--sg-background-color, var(--theme-background, var(--jp-layout-color0, white)));
  --sklearn-color-border-box: var(--sg-text-color, var(--theme-code-foreground, var(--jp-content-font-color1, black)));
  --sklearn-color-icon: #696969;

  @media (prefers-color-scheme: dark) {
    /* Redefinition of color scheme for dark theme */
    --sklearn-color-text-on-default-background: var(--sg-text-color, var(--theme-code-foreground, var(--jp-content-font-color1, white)));
    --sklearn-color-background: var(--sg-background-color, var(--theme-background, var(--jp-layout-color0, #111)));
    --sklearn-color-border-box: var(--sg-text-color, var(--theme-code-foreground, var(--jp-content-font-color1, white)));
    --sklearn-color-icon: #878787;
  }
}

#sk-container-id-2 {
  color: var(--sklearn-color-text);
}

#sk-container-id-2 pre {
  padding: 0;
}

#sk-container-id-2 input.sk-hidden--visually {
  border: 0;
  clip: rect(1px 1px 1px 1px);
  clip: rect(1px, 1px, 1px, 1px);
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
  position: absolute;
  width: 1px;
}

#sk-container-id-2 div.sk-dashed-wrapped {
  border: 1px dashed var(--sklearn-color-line);
  margin: 0 0.4em 0.5em 0.4em;
  box-sizing: border-box;
  padding-bottom: 0.4em;
  background-color: var(--sklearn-color-background);
}

#sk-container-id-2 div.sk-container {
  /* jupyter's `normalize.less` sets `[hidden] { display: none; }`
     but bootstrap.min.css set `[hidden] { display: none !important; }`
     so we also need the `!important` here to be able to override the
     default hidden behavior on the sphinx rendered scikit-learn.org.
     See: https://github.com/scikit-learn/scikit-learn/issues/21755 */
  display: inline-block !important;
  position: relative;
}

#sk-container-id-2 div.sk-text-repr-fallback {
  display: none;
}

div.sk-parallel-item,
div.sk-serial,
div.sk-item {
  /* draw centered vertical line to link estimators */
  background-image: linear-gradient(var(--sklearn-color-text-on-default-background), var(--sklearn-color-text-on-default-background));
  background-size: 2px 100%;
  background-repeat: no-repeat;
  background-position: center center;
}

/* Parallel-specific style estimator block */

#sk-container-id-2 div.sk-parallel-item::after {
  content: "";
  width: 100%;
  border-bottom: 2px solid var(--sklearn-color-text-on-default-background);
  flex-grow: 1;
}

#sk-container-id-2 div.sk-parallel {
  display: flex;
  align-items: stretch;
  justify-content: center;
  background-color: var(--sklearn-color-background);
  position: relative;
}

#sk-container-id-2 div.sk-parallel-item {
  display: flex;
  flex-direction: column;
}

#sk-container-id-2 div.sk-parallel-item:first-child::after {
  align-self: flex-end;
  width: 50%;
}

#sk-container-id-2 div.sk-parallel-item:last-child::after {
  align-self: flex-start;
  width: 50%;
}

#sk-container-id-2 div.sk-parallel-item:only-child::after {
  width: 0;
}

/* Serial-specific style estimator block */

#sk-container-id-2 div.sk-serial {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: var(--sklearn-color-background);
  padding-right: 1em;
  padding-left: 1em;
}


/* Toggleable style: style used for estimator/Pipeline/ColumnTransformer box that is
clickable and can be expanded/collapsed.
- Pipeline and ColumnTransformer use this feature and define the default style
- Estimators will overwrite some part of the style using the `sk-estimator` class
*/

/* Pipeline and ColumnTransformer style (default) */

#sk-container-id-2 div.sk-toggleable {
  /* Default theme specific background. It is overwritten whether we have a
  specific estimator or a Pipeline/ColumnTransformer */
  background-color: var(--sklearn-color-background);
}

/* Toggleable label */
#sk-container-id-2 label.sk-toggleable__label {
  cursor: pointer;
  display: block;
  width: 100%;
  margin-bottom: 0;
  padding: 0.5em;
  box-sizing: border-box;
  text-align: center;
}

#sk-container-id-2 label.sk-toggleable__label-arrow:before {
  /* Arrow on the left of the label */
  content: "▸";
  float: left;
  margin-right: 0.25em;
  color: var(--sklearn-color-icon);
}

#sk-container-id-2 label.sk-toggleable__label-arrow:hover:before {
  color: var(--sklearn-color-text);
}

/* Toggleable content - dropdown */

#sk-container-id-2 div.sk-toggleable__content {
  max-height: 0;
  max-width: 0;
  overflow: hidden;
  text-align: left;
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-0);
}

#sk-container-id-2 div.sk-toggleable__content.fitted {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-0);
}

#sk-container-id-2 div.sk-toggleable__content pre {
  margin: 0.2em;
  border-radius: 0.25em;
  color: var(--sklearn-color-text);
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-0);
}

#sk-container-id-2 div.sk-toggleable__content.fitted pre {
  /* unfitted */
  background-color: var(--sklearn-color-fitted-level-0);
}

#sk-container-id-2 input.sk-toggleable__control:checked~div.sk-toggleable__content {
  /* Expand drop-down */
  max-height: 200px;
  max-width: 100%;
  overflow: auto;
}

#sk-container-id-2 input.sk-toggleable__control:checked~label.sk-toggleable__label-arrow:before {
  content: "▾";
}

/* Pipeline/ColumnTransformer-specific style */

#sk-container-id-2 div.sk-label input.sk-toggleable__control:checked~label.sk-toggleable__label {
  color: var(--sklearn-color-text);
  background-color: var(--sklearn-color-unfitted-level-2);
}

#sk-container-id-2 div.sk-label.fitted input.sk-toggleable__control:checked~label.sk-toggleable__label {
  background-color: var(--sklearn-color-fitted-level-2);
}

/* Estimator-specific style */

/* Colorize estimator box */
#sk-container-id-2 div.sk-estimator input.sk-toggleable__control:checked~label.sk-toggleable__label {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-2);
}

#sk-container-id-2 div.sk-estimator.fitted input.sk-toggleable__control:checked~label.sk-toggleable__label {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-2);
}

#sk-container-id-2 div.sk-label label.sk-toggleable__label,
#sk-container-id-2 div.sk-label label {
  /* The background is the default theme color */
  color: var(--sklearn-color-text-on-default-background);
}

/* On hover, darken the color of the background */
#sk-container-id-2 div.sk-label:hover label.sk-toggleable__label {
  color: var(--sklearn-color-text);
  background-color: var(--sklearn-color-unfitted-level-2);
}

/* Label box, darken color on hover, fitted */
#sk-container-id-2 div.sk-label.fitted:hover label.sk-toggleable__label.fitted {
  color: var(--sklearn-color-text);
  background-color: var(--sklearn-color-fitted-level-2);
}

/* Estimator label */

#sk-container-id-2 div.sk-label label {
  font-family: monospace;
  font-weight: bold;
  display: inline-block;
  line-height: 1.2em;
}

#sk-container-id-2 div.sk-label-container {
  text-align: center;
}

/* Estimator-specific */
#sk-container-id-2 div.sk-estimator {
  font-family: monospace;
  border: 1px dotted var(--sklearn-color-border-box);
  border-radius: 0.25em;
  box-sizing: border-box;
  margin-bottom: 0.5em;
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-0);
}

#sk-container-id-2 div.sk-estimator.fitted {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-0);
}

/* on hover */
#sk-container-id-2 div.sk-estimator:hover {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-2);
}

#sk-container-id-2 div.sk-estimator.fitted:hover {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-2);
}

/* Specification for estimator info (e.g. "i" and "?") */

/* Common style for "i" and "?" */

.sk-estimator-doc-link,
a:link.sk-estimator-doc-link,
a:visited.sk-estimator-doc-link {
  float: right;
  font-size: smaller;
  line-height: 1em;
  font-family: monospace;
  background-color: var(--sklearn-color-background);
  border-radius: 1em;
  height: 1em;
  width: 1em;
  text-decoration: none !important;
  margin-left: 1ex;
  /* unfitted */
  border: var(--sklearn-color-unfitted-level-1) 1pt solid;
  color: var(--sklearn-color-unfitted-level-1);
}

.sk-estimator-doc-link.fitted,
a:link.sk-estimator-doc-link.fitted,
a:visited.sk-estimator-doc-link.fitted {
  /* fitted */
  border: var(--sklearn-color-fitted-level-1) 1pt solid;
  color: var(--sklearn-color-fitted-level-1);
}

/* On hover */
div.sk-estimator:hover .sk-estimator-doc-link:hover,
.sk-estimator-doc-link:hover,
div.sk-label-container:hover .sk-estimator-doc-link:hover,
.sk-estimator-doc-link:hover {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-3);
  color: var(--sklearn-color-background);
  text-decoration: none;
}

div.sk-estimator.fitted:hover .sk-estimator-doc-link.fitted:hover,
.sk-estimator-doc-link.fitted:hover,
div.sk-label-container:hover .sk-estimator-doc-link.fitted:hover,
.sk-estimator-doc-link.fitted:hover {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-3);
  color: var(--sklearn-color-background);
  text-decoration: none;
}

/* Span, style for the box shown on hovering the info icon */
.sk-estimator-doc-link span {
  display: none;
  z-index: 9999;
  position: relative;
  font-weight: normal;
  right: .2ex;
  padding: .5ex;
  margin: .5ex;
  width: min-content;
  min-width: 20ex;
  max-width: 50ex;
  color: var(--sklearn-color-text);
  box-shadow: 2pt 2pt 4pt #999;
  /* unfitted */
  background: var(--sklearn-color-unfitted-level-0);
  border: .5pt solid var(--sklearn-color-unfitted-level-3);
}

.sk-estimator-doc-link.fitted span {
  /* fitted */
  background: var(--sklearn-color-fitted-level-0);
  border: var(--sklearn-color-fitted-level-3);
}

.sk-estimator-doc-link:hover span {
  display: block;
}

/* "?"-specific style due to the `<a>` HTML tag */

#sk-container-id-2 a.estimator_doc_link {
  float: right;
  font-size: 1rem;
  line-height: 1em;
  font-family: monospace;
  background-color: var(--sklearn-color-background);
  border-radius: 1rem;
  height: 1rem;
  width: 1rem;
  text-decoration: none;
  /* unfitted */
  color: var(--sklearn-color-unfitted-level-1);
  border: var(--sklearn-color-unfitted-level-1) 1pt solid;
}

#sk-container-id-2 a.estimator_doc_link.fitted {
  /* fitted */
  border: var(--sklearn-color-fitted-level-1) 1pt solid;
  color: var(--sklearn-color-fitted-level-1);
}

/* On hover */
#sk-container-id-2 a.estimator_doc_link:hover {
  /* unfitted */
  background-color: var(--sklearn-color-unfitted-level-3);
  color: var(--sklearn-color-background);
  text-decoration: none;
}

#sk-container-id-2 a.estimator_doc_link.fitted:hover {
  /* fitted */
  background-color: var(--sklearn-color-fitted-level-3);
}
</style><div id="sk-container-id-2" class="sk-top-container"><div class="sk-text-repr-fallback"><pre>LGBMRegressor(colsample_bytree=0.6, importance_type=&#x27;gain&#x27;, learning_rate=0.07,
              max_depth=6, min_child_samples=3, min_child_weight=1,
              n_estimators=2500, n_jobs=-1, num_leaves=20, random_state=234,
              reg_alpha=10, reg_lambda=1, subsample=0.7, verbose=-1)</pre><b>In a Jupyter environment, please rerun this cell to show the HTML representation or trust the notebook. <br />On GitHub, the HTML representation is unable to render, please try loading this page with nbviewer.org.</b></div><div class="sk-container" hidden><div class="sk-item"><div class="sk-estimator fitted sk-toggleable"><input class="sk-toggleable__control sk-hidden--visually" id="sk-estimator-id-2" type="checkbox" checked><label for="sk-estimator-id-2" class="sk-toggleable__label fitted sk-toggleable__label-arrow fitted">&nbsp;LGBMRegressor<span class="sk-estimator-doc-link fitted">i<span>Fitted</span></span></label><div class="sk-toggleable__content fitted"><pre>LGBMRegressor(colsample_bytree=0.6, importance_type=&#x27;gain&#x27;, learning_rate=0.07,
              max_depth=6, min_child_samples=3, min_child_weight=1,
              n_estimators=2500, n_jobs=-1, num_leaves=20, random_state=234,
              reg_alpha=10, reg_lambda=1, subsample=0.7, verbose=-1)</pre></div> </div></div></div></div>




```python
regressor.train(catm, pd.concat([xtrain, xval]), pd.concat([ytrain, yval]))
```




    <catboost.core.CatBoostRegressor at 0x21d4b465550>




```python
test.index = test.index.astype('datetime64[ns]')
```


```python
test_set = (
    test_demand.assign(demand_group = test_demand.demand_group.map({'high':1, 'medium':0})).reset_index()
    .merge(test.reset_index(), on=['ride_datetime', 'demand_group'], how='right')
    .set_index('ride_datetime')
)

test_set = test_set[train_set.columns]
```


```python
xtest, ytest = test_set.drop(columns=TARGET), test_set[TARGET]
```


```python
print(model_metrics(lgbm, xtest, ytest))
print(model_metrics(catm, xtest, ytest))
```

    RMSE: 10.3520	MAE: 7.5352
    RMSE: 9.5740	MAE: 6.8133
    


```python
test_pred_df = pd.DataFrame(index=test_set.index, columns=['demand_group', 'actual', 'lgbm', 'catm'])

test_pred_df['demand_group'] = xtest.demand_group.map({1:'High', 0:'Medium'})
test_pred_df['actual'] = ytest
for i, model in enumerate([lgbm, catm], start=2):
    pred = model.predict(xtest)
    test_pred_df.iloc[:, i] = pred
```


```python
test_pred_df[['lgbm', 'catm']] = test_pred_df[['lgbm', 'catm']].map(float)

corr = test_pred_df.corr(numeric_only=True)

sns.heatmap(corr, mask=np.triu(corr), annot=True, cbar=False, cmap='coolwarm', alpha=0.7, fmt='.3f')
plt.title('Correlation between Actual vs Predictions', fontweight='bold', loc='left');
```


    
![png](output_107_0.png)
    



```python
(
    pn.ggplot(
        (test_pred_df.melt(id_vars='demand_group', ignore_index=False, var_name='pred_type', value_name='values')
                .reset_index()
        ), pn.aes(x='ride_datetime', y='np.float64(values)', color='factor(pred_type)')) +
    pn.geom_line(size=0.7) +
    pn.facet_wrap('~demand_group', scales='free_y', nrow=2) +
    pn.theme_538() +
    pn.theme(figure_size=(12,6), 
             legend_key=pn.element_blank(),
             strip_background=pn.element_rect(fill='steelblue'),
             strip_text=pn.element_text(color='white', face='bold'),
             panel_grid=pn.element_blank(),
             plot_title=pn.element_text(hjust=0, face='bold'),
             legend_position='top') +
    pn.scale_x_datetime(date_breaks='2 day', date_labels='%b %d\n%Y', date_minor_breaks='1 hour') +
    pn.labs(title='Actual vs Model Predictions (April 2024)', x='Datetime', y='Taxi Demand', color='') +
    pn.scale_color_manual(values=('steelblue', 'orange', 'green'), labels=('Actual', 'CatBoost', 'LightGBM')) +
    pn.scale_y_continuous(expand=(0, 0, 0.1, 2))
)
```


    
![png](output_108_0.png)
    


- Looking at the predictions for April, both models also seem to better predict taxi demands in high demand areas than in medium demand areas.
- The catboost model seem to better model the demands for medium-demand areas than lightgbm model which seem to under predict and overpredict at some points.
- Looking at the correlation between the actual demand and model predictions, predictions from both models highly correlate with the actual taxi demands.


```python
fig, ax = plt.subplots(1,2,figsize=(9,5))
sns.scatterplot(test_pred_df, x='actual', y='catm', ax=ax[0])
ax[0].set_title('Actual vs Catboost Predictions', loc='left', fontweight='bold')

sns.scatterplot(test_pred_df, x='actual', y='lgbm',ax=ax[1])
ax[1].set_title('Actual vs LightGBM Predictions', loc='left', fontweight='bold')

fig.tight_layout()
```


    
![png](output_110_0.png)
    



```python

```
