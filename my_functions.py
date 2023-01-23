import requests
import pandas as pd
import private
import datetime

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
def getAQI(start_date: datetime.datetime, end_date: datetime.datetime, lat: str, lon: str, start_date_id: int=0) -> pd.DataFrame:
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


"""
Perform feature engineering on the historical data and
drop the historical features. Should have the future timestamps
in there when calling this function so you only have to do it once.
"""
def createFeatures(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    # add date features
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['quarter'] = df.index.quarter
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear
    df['dayofmonth'] = df.index.day
    df['weekofyear'] = df.index.isocalendar().week.astype('int')
    
    # add lag features
    features_to_lag = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3', 'aqi']

    for feature in features_to_lag:
        # lag feature by 3 days
        new_feature_name = feature + '_lag3d'
        df[new_feature_name] = df[feature].shift(freq='3D', axis=0)
        
        
    window = 24  # hours
    df['aqi_max_lag_3d'] = df['aqi'].rolling(window=window).agg(['max']).shift(freq='3D', axis=0)
    df['aqi_mean_lag_3d'] = df['aqi'].rolling(window=window).agg(['mean']).shift(freq='3D', axis=0)
    df['aqi_std_lag_3d'] = df['aqi'].rolling(window=window).agg(['std']).shift(freq='3D', axis=0)
    
    # drop the historical features
    df = df.drop(columns=['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3'])
    
    return df