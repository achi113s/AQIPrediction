import pandas as pd
import datetime
from my_functions import determineNewestAQIDate
from my_functions import getAQI
from my_functions import getCoords
import hopsworks
import sys
import os

"""
Retreive air pollution data from OpenWeather API, generate features,
upload it to Hopsworks feature store.
"""

project = hopsworks.login()
fs = project.get_feature_store()

zip_code = '60603'  # Chicago
country_code = 'US'
city = 'Chicago'

fg_name = f'{city}_{zip_code}_aqi'.lower()
start_date = determineNewestAQIDate(fs, fg_name)
end_date = datetime.datetime.now() - datetime.timedelta(hours=2)  # subtract two hours to add a lag

"""
If the start date is greater than or equal to the end date, we have the 
latest data in Hopsworks and don't need to download new data.
"""
if start_date >= end_date:
    sys.exit('Hopsworks has latest data. Quitting now...')

zip_code_api = f'{zip_code},{country_code}'
coords = getCoords(zip_code_api)

data = getAQI(start_date, end_date, coords['lat'], coords['lon'], fg_name)

data_path = os.path.join('data', f'{fg_name}.csv')  # save data to my disk
data.to_csv(data_path, mode='a', index=False, header=not os.path.exists(data_path))

"""
Upload data into a feature group.
"""
aqi_fg = fs.get_or_create_feature_group(
    name=fg_name,
    version=1,
    description=f'historical air quality index with predictors for {fg_name}',
    primary_key=['datetime'],  
    event_time='datetime',
    partition_key=['date'],
    online_enabled=True
)

aqi_fg.insert(data)