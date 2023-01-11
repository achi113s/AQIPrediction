import pandas as pd
import datetime
from my_functions import determineNewestAQIDate
from my_functions import getAQI
from my_functions import getCoords

"""
Retreive air pollution data from OpenWeather API, generate features,
upload it to Hopsworks feature store.
"""

# may change this later
zip_code = '60603'  # Chicago
country_code = 'US'
city = 'Chicago'

fg_name = f'{zip_code}_{city}_AQI'
start_date = determineNewestAQIDate(fg_name)
end_date = datetime.datetime.now() - datetime.timedelta(hours=2)

zip_code_api = f'{zip_code},{country_code}'
coords = getCoords(zip_code_api)

data = getAQI(start_date, end_date, coords[0], coords[1], fg_name)

print(data.head())