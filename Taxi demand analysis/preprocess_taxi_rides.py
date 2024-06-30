#!/usr/bin/env python
# coding: utf-8

# ## Data
# 
# Dataset contains car rides for yellow Taxi Cabs in the environs of New York, made between Jan 2021 and present

# ## Variable Description

# _Yellow Taxi Cab_
# 
# Field Name |Description
# :--|:--
# VendorID | A code indicating the TPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.
# tpep_pickup_datetime | The date and time when the meter was engaged.
# tpep_dropoff_datetime | The date and time when the meter was disengaged.
# Passenger_count | The number of passengers in the vehicle. This is a driver-entered value.
# Trip_distance | The elapsed trip distance in miles reported by the taximeter.
# PULocationID | TLC Taxi Zone in which the taximeter was engaged
# DOLocationID | TLC Taxi Zone in which the taximeter was disengaged
# RateCodeID | The final rate code in effect at the end of the trip. 1= Standard rate, 2=JFK, 3=Newark, 4=Nassau or Westchester, 5=Negotiated fare, 6=Group ride
# Store_and_fwd_flag |This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka “store and forward,” because the vehicle did not have a connection to the server. Y= store and forward trip. N= not a store and forward trip
# Payment_type | A numeric code signifying how the passenger paid for the trip. 0= Credit card 1= Cash 2= No charge 3= Dispute 4= Unknown 5= Voided trip
# Fare_amount | The time-and-distance fare calculated by the meter.
# Extra | Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges.
# MTA_tax | $0.50 MTA tax that is automatically triggered based on the metered rate in use.
# Improvement_surcharge | $0.30 improvement surcharge assessed trips at the flag drop. The improvement surcharge began being levied in 2015.
# Tip_amount | Tip amount – This field is automatically populated for credit card tips. Cash tips are not included.
# Tolls_amount | Total amount of all tolls paid in trip.
# Total_amount |The total amount charged to passengers. Does not include cash tips.
# Congestion_Surcharge | Total amount collected in trip for NYS congestion surcharge.
# Airport_fee | $1.25 for pick up only at LaGuardia and John F. Kennedy Airports


# import libraries
import pandas as pd
import numpy as np
import sqlite3
from tqdm import tqdm
from glob import glob
import gc, re
import datetime
import pyarrow.parquet as pq
from pathlib import os
import pyarrow.compute as pc


# get path
path = os.getcwd()


# functions
def reduce_memory(df):
    start = df.memory_usage().sum() /1024**2

    dtypes = df.dtypes
    cols = dtypes.index.tolist()

    for i in range(len(cols)):
        col = cols[i]
        col_type  = dtypes.iloc[i].name

        if 'float' in col_type or 'int' in col_type:
            c_min = df[col].min()
            c_max = df[col].max()

            if 'int' in col_type:
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.uint8).min and c_max < np.iinfo(np.uint8).max:
                    df[col] = df[col].astype(np.uint8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.uint16).min and c_max < np.iinfo(np.uint16).max:
                    df[col] = df[col].astype(np.uint16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.uint32).min and c_max < np.iinfo(np.uint32).max:
                    df[col] = df[col].astype(np.uint32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
                elif c_min > np.iinfo(np.uint64).min and c_max < np.iinfo(np.uint64).max:
                    df[col] = df[col].astype(np.uint64)
            else:
                df[col] = df[col].astype(np.float32)
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        elif col_type in ['object', 'category', 'datetime64[ns]']:
            df[col] = df[col].astype('category')
    
    end = df.memory_usage().sum() /1024**2 
    diff = (start-end)
    print(f'Start Memory: {start:.2f} MB \tEnd Memory: {end:.2f}MB\nMemory Reduced: {diff:.2f}MB ({diff/start*100:.2f}%)')
    return df


def change_dtypes(x):
    """Function to change the data types of variables to SQL variables"""
    if 'int' in x.name:
        return 'INT'
    if 'float' in x.name:
        return 'REAL'
    else:
        return 'TEXT'


def create_table_columns(data):
    """
    Create columns of table for provided data

    :param data: dataset to create table columns for database
    """    
    new_dtypes = np.vectorize(change_dtypes)(data.dtypes) # get dtypes for database table creation

    # database table description
    db_cols = ''

    # convert pandas dtypes to valid database 
    for i in range(len(new_dtypes)):
        db_cols = db_cols + (f'{data.columns[i]} {new_dtypes[i]},')
    return db_cols


def check_if_table_exists(cursor, table_name):
    """
    Checks and creates table in database. Deletes table if table exists and returns user_input
    :param table_name: Name of table to create
    :param data: Dataset to create table from

    """
    user_input = ''
    try:
        # query to get table if it exists in database
        table_query = f"""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name = '{table_name}';
        """
        # get list of tables
        list_of_tables = cursor.execute(table_query).fetchall()   
        if len(list_of_tables) > 0:     
            list_of_tables = list(map(lambda x:x[0], list_of_tables))
        
        if table_name in list_of_tables:
            user_input = input(f"{table_name} exists\nDo you want to delete table?: Y/N\n")
            if user_input.upper()  == 'Y':
                cursor.execute(f"Drop Table {table_name};")
            elif user_input.upper() not in ['Y', 'N']:
                print(f'{user_input} not recognised')
                exit(0)
    except Exception as err:
        print(err)
    return user_input




def create_table(cursor, table_name, data):
    """
    Checks and creates table in database. Deletes table if table exists and returns user_input
    :param table_name: Name of table to create
    :param data: Dataset to create table from

    """
    user_input = check_if_table_exists(cursor, table_name)
    db_cols = create_table_columns(data)

    # if user_input = '' (table hasn't been created before)
    # if user_input = 'Y' (table existed but has been dropped)
    if user_input == '' or user_input.upper() == 'Y':
        # create table
        table = f"""Create Table {table_name} ({db_cols})""".replace(',)', ')')
        cursor.execute(table)
        print(f'{table_name} table created')
    return user_input


# Insert to table
def insert_data_to_table(cursor, table_name, data):
    user_input = create_table(cursor, table_name, data)

    if user_input.upper() == 'Y' or user_input == '':
        try:
            # get table columns
            table_cols = [i[0] for i in cursor.execute(f'Select * from {table_name};').description]

            # insert data into table
            query = ','.join(table_cols) # columns
            val_query = '?,'*len(table_cols)
            
            data_query = """INSERT INTO {} ({}) VALUES ({});""".format(table_name, query, val_query)
            data_query = data_query.replace('[', '').replace(']', '').replace(',)', ')')
            
            for chunk in tqdm(range(0, len(df), size), desc=f"Writing to {table_name} table"):

                chunk_df = df.iloc[chunk:chunk+size, :]
                datetime_format = '[0-9]{,4}-[0-9]{,2}-[0-9]{,2} [0-9]{,2}:[0-9]{,2}:[0-9]{,2}' # 2021-01-10 10:30:00
                chunk_df =  chunk_df.assign(
                    ride_datetime = chunk_df['ride_datetime'].apply(lambda x: re.search(datetime_format, str(x)).group())
                    )

                chunk_df = chunk_df.values.tolist()
                
                cursor.executemany(data_query, chunk_df)
            print(f'data inserted to {table_name}')
        except Exception as err:
            print(err)
    elif user_input.upper()  == 'N':
        print('Table not created!\n')



# get location information
location_info = pd.read_csv(f'{path}/location_info.csv')

# get all trip files
trips = glob(f'{path}/data/yellow_tripdata*.parquet')


pickup_df = []
dropoff_df = []

for i in tqdm(range(len(trips)), desc='Reading Datasets'):
    # get month
    month = re.search('[0-9]{,4}-[0-9]{,2}', trips[i]).group()
    month_start = pd.to_datetime(month)
    month_start = re.search('[0-9]{,4}-[0-9]{,2}-[0-9]{,2}', str(month_start)).group()
    month_end = pd.date_range(month_start, periods=1, freq='ME')[0]
    month_end = str(month_end.date()) + ' 23:59:00'
    
    # load data
    temp = pq.read_table(
        trips[i], 
        columns=['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'payment_type', 
                 'PULocationID', 'DOLocationID', 'total_amount', 'trip_distance', 
                 'fare_amount']
                 )
                                            
    # filter rides that riders paid by cash (1), credit card (0)
    temp = temp.filter(pc.field('payment_type') < 2)

    # filter total amount that are positive
    temp = temp.filter(pc.field('total_amount') > 0)

    # convert to pandas dataframe
    temp = temp.to_pandas()
    temp['duration_secs'] = (temp.tpep_dropoff_datetime - temp.tpep_pickup_datetime).dt.total_seconds()

    # aggregate
    # convert to nearest hour range
    temp.tpep_pickup_datetime = pd.DatetimeIndex(temp.tpep_pickup_datetime).floor('h')

    # get pickup station data
    pickup_data = temp.groupby(['tpep_pickup_datetime', 'PULocationID']).agg(
        {
        'payment_type' : 'count', 
        'total_amount' : 'sum', 
        'duration_secs' : 'mean',
        'trip_distance' : 'mean',
        'fare_amount' : 'sum'
        })
    
    pickup_data = pickup_data.reset_index()
    pickup_data = pickup_data.rename(
        {
        'tpep_pickup_datetime' : 'ride_datetime', 
        'payment_type' : 'hourly_rides',
        'PULocationID' : 'pickup_station',
        'trip_distance' : 'distance_miles', 
        'total_amount' : 'revenue',
        'fare_amount' : 'total_fare_cost'
        }, axis=1)
    
    # filter pickupdata within month
    pickup_data = pickup_data.query(f"ride_datetime >= '{month_start}' & ride_datetime <= '{month_end}'")
    
    
    pickup_df.append(pickup_data)

    # get dropoff station data (total number of rides going to drop off station)
    dropoff_data = temp.groupby(['tpep_pickup_datetime', 'DOLocationID']).agg(
        {
        'payment_type' : 'count',
        'duration_secs' : 'mean',
        'trip_distance' : 'mean',
        'fare_amount' : 'sum'
        })

    dropoff_data = dropoff_data.reset_index()
    dropoff_data = dropoff_data.rename(
        {
        'tpep_pickup_datetime' : 'ride_datetime', 
        'payment_type' : 'hourly_rides',
        'DOLocationID' : 'dropoff_station',
        'trip_distance' : 'distance_miles',
        'fare_amount' : 'total_fare_cost'
        }, axis=1)
    
    # filter dropoff data within month
    dropoff_data = dropoff_data.query(f"ride_datetime >= '{month_start}' & ride_datetime <= '{month_end}'")
    
    
    dropoff_df.append(dropoff_data)


    gc.collect()

pickup_df = pd.concat(pickup_df)
pickup_df = pickup_df.reset_index(drop=True)

dropoff_df = pd.concat(dropoff_df)
dropoff_df = dropoff_df.reset_index(drop=True)

# reduce memory
pickup_df = reduce_memory(pickup_df)
dropoff_df = reduce_memory(dropoff_df)

# convert revenue back to float32
pickup_df['revenue'] = np.round(pickup_df['revenue'].astype('float64'), 2).astype('float32')

# save data
pickup_df.to_parquet(f'{path}/data/pickup_rides.parquet')
dropoff_df.to_parquet(f'{path}/data/dropoff_rides.parquet')



# # last date of collected data
# last_date = '2024-01-01'
# last_date = datetime.datetime.strptime(last_date, '%Y-%m-%d')
# # extract date part of dataset name
# trips_date = list(map(lambda x: re.search('[0-9]{,4}-[0-9]{,2}', x).group()), trips)
# # convert to datetime
# trips_date = list(map(lambda x: datetime.datetime.strptime(x, '%Y-%m'), trips_date))

# is_new_data = np.array(trips_date) > np.array(last_date)
# new_trips_data = trips[is_new_data] # get new data to update table




# create database

# create database connection
conn = sqlite3.connect(f'{path}/TLC_trips.sqlite') #db
cursor = conn.cursor()

# saving location info to sql
location_info.to_sql(name='location_info', con=conn, if_exists='replace', index=False)

size = 80000 # chunk size for writing to database


# create table and insert data to table
table_names = ['pickup_trips', 'dropoff_trips']
data = [pickup_df, dropoff_df]

for i in range(len(table_names)):
    table_name = table_names[i]
    df = data[i]
    insert_data_to_table(cursor, table_name, df)

# close database
conn.commit()
conn.close()

print()
print(pickup_df.shape)
print(dropoff_df.shape)
print('\nPickup Station\n*****************\n')
print(pickup_df.head())
print('\nDropoff Station\n*****************\n')
print(dropoff_df.head())