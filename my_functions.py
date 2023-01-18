import requests
import pandas as pd
import private
import datetime
import hopsworks
import os


"""
This function will determine the start date for the GET request
to OpenWeather. Returns tuple with date parameters, (yyyy, mm, dd).
"""
def determineNewestAQIDate(fs, fg_name: str) -> tuple:
    try:
        newest_date = fs.sql(f"SELECT MAX(`datetime`) FROM `{fg_name}_1`", online=True).values[0][0]
        newest_date_id = fs.sql(f"SELECT MAX(`id`) FROM `{fg_name}_1`", online=True).values[0][0] + 1
        newest_date = pd.to_datetime(newest_date) + datetime.timedelta(hours=1)
    except:
        """
        If the above throws an exception, the feature group doesn't exist
        and so we need to create it. Therefore the start date is going
        to the be oldest date that OpenWeather has for AQI data, which
        is 2020 November 27 00:00:00.
        """
        newest_date = datetime.datetime(2020, 11, 27, 0, 0 ,0)
        newest_date_id = 0
        print(f'Feature group {fg_name} doesn\'t exist.')

    print(f'Newest feature vector date is: {newest_date} with ID: {newest_date_id}.')
    
    return (newest_date_id, newest_date)
 

"""
GET coordinates for a given zip code from OpenWeather. Returns
tuple of latitude and longitude coords, (lat, lon).
"""
def getCoords(zip_code: str) -> dict:
    geo_loc_url = f'http://api.openweathermap.org/geo/1.0/zip'
    params = {'zip': zip_code, 'appid': private.MY_API_KEY}

    geo_loc_response = requests.get(geo_loc_url, params=params)
    geo_loc_response_json = geo_loc_response.json()

    return dict(geo_loc_response_json)

"""
GET AQI data for a given date range and coordinate. Returns
Pandas DataFrame.
"""
def getAQI(start_date: datetime.datetime, end_date: datetime.datetime, lat: str, lon: str, fg_name: str, start_date_id: int=0) -> pd.DataFrame:
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
    dates = [datetime.datetime.fromtimestamp(x['dt']) for x in aqi_resp_json['list']]
    aqis = [x['main']['aqi'] for x in aqi_resp_json['list']]
    pollutants = [x['components'] for x in aqi_resp_json['list']]

    data = pd.DataFrame(pollutants)
    data['datetime'] = dates
    data['date'] = data['datetime'].dt.date
    data['lat'] = coord['lat']
    data['lon'] = coord['lon']
    data['aqi'] = aqis
    data['id'] = range(start_date_id, start_date_id+len(data['aqi']))

    return data


"""
Takes in a dataframe and cleans it according to needs. Sometimes we get
duplicate entries in the AQI data and these need to be fixed. For example, 
these two rows:
327.11,0.0,17.82,67.23,6.26,10.14,12.73,1.55,2021-11-07 01:00:00,2021-11-07,41.8798,-87.6285,2,8256
317.1,0.0,15.94,67.23,6.26,9.71,11.87,1.28,2021-11-07 01:00:00,2021-11-07,41.8798,-87.6285,1,8257
are from the same timestamp. We're dealing with thousands of data points,
so just keep the first one and discard any duplicates.
"""
def cleanData(df: pd.DataFrame, start_date_id: int) -> pd.DataFrame:
    duplicates = df[df.duplicated(subset=['datetime'])]
    print('Duplicates: ', duplicates)

    df = df.drop_duplicates(subset=['datetime'], keep='first')
    
    df = df.drop(columns=['id'])
    df['id'] = range(start_date_id, start_date_id+len(df['aqi']))

    df = df.fillna(method='ffill')

    return df