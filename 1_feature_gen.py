import pandas as pd
import datetime
from my_functions import getAQI
from my_functions import getCoords
from my_functions import cleanData
import sys
import os
import logging
import logging.handlers
import private

"""
Retreive air pollution data from OpenWeather API 
and save to disk.

Feature Descriptions:
    datetime: timestamp of data,
    co: carbon monoxide concentration in micrograms per cubic meter,
    no: nitrogen monoxide concentration in micrograms per cubic meter,
    no2: nitrogen dioxide concentration in micrograms per cubic meter,
    o3: ozone concentration in micrograms per cubic meter,
    so2: sulfur dioxide concentration in micrograms per cubic meter,
    pm2_5: particulates concentration in micrograms per cubic meter,
    pm10: particulates concentration in micrograms per cubic meter,
    nh3: ammonia concentration in micrograms per cubic meter,
    lat: latitude of location,
    lon: longitude of location,   
    aqi: air quality index,   
    id: id number  
"""

# set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

zip_code = '60603'  # Chicago
country_code = 'US'
city = 'Chicago'

aqi_table_name = f'aqi_{city}_{zip_code}'.lower()

"""
If file exists already, we just need to download any new data.
"""
data_path = os.path.join('data', f'{aqi_table_name}.csv')

if os.path.exists(data_path):
    df = pd.read_csv(data_path, index_col='datetime', parse_dates=True)
    start_date = df.index.max() + datetime.timedelta(hours=1)
    start_date_id = df['id'].max() + 1
else:
    start_date = datetime.datetime(2020, 11, 27, 0, 0 ,0)
    start_date_id = 0

end_date = datetime.datetime.now() - datetime.timedelta(hours=3)
end_date = end_date.replace(second=0, microsecond=0, minute=0, hour=end_date.hour)
"""
If the start date is greater than or equal to the end date, we have the 
latest data and can quit.
"""
if start_date >= end_date:
    sys.exit('Data is up to date. Quitting now...')

try:
    api_key = os.environ['OPENWEATHERAPIKEY']
except KeyError:
    api_key = private.MY_API_KEY
    logger.info('Environment API Key not available!')


zip_code_api = f'{zip_code},{country_code}'
coords = getCoords(zip_code_api, api_key)

data = getAQI(start_date, end_date, coords['lat'], coords['lon'], api_key, start_date_id=start_date_id)

# Get rid of duplicates and deal with missing values.
data = cleanData(data, start_date_id)

# Append new data to old.
data.to_csv(data_path, mode='a', index=False, header=not os.path.exists(data_path))

logger.info(f'Downloaded AQI data for {start_date} to {end_date}.')