import requests
import pandas as pd
import private
import datetime
import hopsworks
import os
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
