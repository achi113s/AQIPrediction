import pandas as pd
import datetime
from my_functions import determineNewestAQIDate
from my_functions import getAQI
from my_functions import getCoords
import hopsworks

"""
Retreive air pollution data from OpenWeather API, generate features,
upload it to Hopsworks feature store.
"""

project = hopsworks.login()
fs = project.get_feature_store()

# may change this later
zip_code = '60603'  # Chicago
country_code = 'US'
city = 'Chicago'

fg_name = f'{zip_code}_{city}_AQI'
start_date = determineNewestAQIDate(fs, fg_name)
end_date = datetime.datetime.now() - datetime.timedelta(hours=2)

zip_code_api = f'{zip_code},{country_code}'
coords = getCoords(zip_code_api)

data = getAQI(start_date, end_date, coords['lat'], coords['lon'], fg_name)
print(data.head())
"""
Upload data into a feature group.
"""
# aqi_fg = fs.get_or_create_feature_group(
#     name="historical_aqi",
#     version="1",
#     description="historical air quality index with predictors",
#     primary_key=['datetime'],   
#     event_time='datetime',
#     partition_key=['date']
# )

# aqi_fg.insert(data)