import requests
import pandas as pd
import private
import datetime
import os
import hopsworks
import typing

"""
Retreive air pollution data from OpenWeather API, generate features,
upload it to Hopsworks feature store.
"""

# may change this later
zip_code = '60603'  # Chicago
country_code = 'US'
city = 'Chicago'

"""
This function will determine the start date for the GET request
to OpenWeather. Returns tuple with date parameters, (yyyy, mm, dd).
"""
def determineNewestAQIDate(fg_name: str = '60603_Chicago_AQI') -> datetime:
    fg_exists = False

    try:
        project = hopsworks.login()
        fs = project.get_feature_store()
        fg = fs.get_feature_group(name=fg_name)

        newest_date = fg['datetime'].max()
        
        return newest_date
    except:
        print(f'Feature view {fg_name} doesn\'t exist.')

    """
    If the above throws an exception, the feature group doesn't exist
    and so we need to create it. Therefore the start date is going
    to the be oldest date that OpenWeather has for AQI data, which
    is 2020 November 27 00:00:00.
    """
    newest_date = datetime.datetime(2020, 11, 27, 0, 0 ,0)

    return newest_date
 

"""
GET coordinates for a given zip code from OpenWeather. Returns
tuple of latitude and longitude coords, (lat, lon).
"""
def getCoords(zip: str = '60603,US') -> tuple(str, str):
    geo_loc_url = f'http://api.openweathermap.org/geo/1.0/zip'
    params = {'zip': zip_code, 'appid': private.MY_API_KEY}

    geo_loc_response = requests.get(geo_loc_url, params=params)
    geo_loc_response_json = geo_loc_response.json()

    lat = geo_loc_response_json['lat']
    lon = geo_loc_response_json['lon']

    return (lat, lon)   