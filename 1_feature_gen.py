import requests
import pandas as pd
import private
import datetime
import hopsworks
import os

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
def determineNewestAQIDate(fg_name: str = '60603_Chicago_AQI') -> datetime.datetime:
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

"""
GET AQI data for a given date range and coordinate. Returns
Pandas DataFrame.
"""
def getAQI(start_date: datetime.datetime, end_date: datetime.datetime, lat: str, lon: str) -> pd.DataFrame:
    start_unix = int(datetime.datetime.timestamp(start_date))
    end_unix = int(datetime.datetime.timestamp(end_date))

    aqi_url = 'http://api.openweathermap.org/data/2.5/air_pollution/history'
    params = {'lat': lat, 'lon': lon, 'start': start_unix, 'end': end_unix, 'appid': private.MY_API_KEY}

    aqi_response = requests.get(aqi_url, params=params)
    aqi_resp_json = aqi_response.json()

    """
    Extract data from AQI response.
    """
    coord = aqi_resp_json['coord']  # latitude and longitude from aqi response
    dates = [datetime.datetime.fromtimestamp(d['dt']) for d in aqi_resp_json['list']]
    aqis = [x['main']['aqi'] for x in aqi_resp_json['list']]
    pollutants = [x['components'] for x in aqi_resp_json['list']]

    data = pd.DataFrame(pollutants)
    data['datetime'] = dates
    data['date'] = data['datetime'].dt.date
    data['lat'] = coord[0]
    data['lon'] = coord[1]
    data['aqi'] = aqis

    data_path = os.path.join('data', 'historical_aqi.csv')  # save data to my disk
    data.to_csv(data_path, index=False)
