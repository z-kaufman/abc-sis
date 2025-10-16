#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converted from Jupyter Notebook: notebook.ipynb
Conversion Date: 2025-10-16T00:28:13.215Z
"""

# # API request and csv appender for IQAir data


import pandas as pd
import requests
import json
import csv
from datetime import datetime, timedelta
import numpy as np
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

response = requests.get(f'http://api.waqi.info/feed/@4469/?token=dae62b01eb4dfedf1f19937d2c3bedef664c4805')
print(response.status_code)

data = response.text

json_response = json.loads(data)

json_response

json_data = json_response['data']
json_data

json_loc = json_data['city']
json_loc

json_aqi = json_data['iaqi']
json_aqi

json_timestamp = json_data['time']
json_timestamp

values = []
headers = []

for i in json_data['iaqi']:
    headers.append(i)
    values.append(json_aqi[i]['v'])

values

headers

df = pd.DataFrame(values).T
df

df.columns = headers
df

date_string = json_data['time']['s']
date_string

format_string = "%Y-%m-%d %H:%M:%S"
datetime_object = datetime.strptime(date_string, format_string)
datetime_object

#Convert to MST
if json_data['time']['tz'] == '-06:00':
    datetime_object = datetime_object - timedelta(hours=1)
datetime_object

#Convert timestamp back to string
datetime_string = datetime_object.strftime('%Y-%m-%d %H:%M:%S')
datetime_string

datetime_list = [datetime_string]
datetime_list

cols = df.columns.tolist()
cols.insert(0, 'timestamp')
df['timestamp'] = datetime_list
df = df[cols]
df

new_data = df.iloc[0].tolist()
new_data

def append_to_csv(file_path, data_row):
    """
    Appends a single row of data to an existing CSV file.

    Args:
        file_path (str): The path to the CSV file.
        data_row (list): A list representing the row of data to append.
    """
    try:
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data_row)
        print(f"Data '{data_row}' appended successfully to '{file_path}'.")
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

csv_file = 'AirQualityOpenData_API_dump.csv'

#Check that this data call is new data by checking last timestamp
df_existingdata = pd.read_csv(csv_file)
print(df_existingdata.head())

print(df_existingdata.tail(1))

last_timestamp = df_existingdata.iloc[-1,0]
print(last_timestamp)

#Turn last timestamp into datetime object
format_string = "%m/%d/%Y %H:%M"
last_timestamp_object = datetime.strptime(last_timestamp, format_string)
print(last_timestamp_object)

#If this hour's data is not yet appended to the csv file, append data.
if last_timestamp_object < datetime_object:
    append_to_csv(csv_file,new_data)
else:
    print('last_timestamp_object is not less than current timestamp')