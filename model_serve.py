import hopsworks
import pandas as pd
from my_functions import createFeatures
import os
import sys

project = hopsworks.login()

dataset_api = project.get_dataset_api()

uploaded_file_path = dataset_api.upload("predict_example.py", "Models", overwrite=True)
predictor_script_path = os.path.join("/Projects", project.name, uploaded_file_path)

mr = project.get_model_registry()

aqi_model = mr.get_model('xgboost_aqi_model')

ms = project.get_model_serving()
try:
    deployment = ms.get_deployment("aqideployed")
except:
    deployment = aqi_model.deploy(name="aqideployed",
                                   script_file=predictor_script_path,  
                                   model_server="PYTHON", 
                                   serving_tool="KSERVE")

print("Deployment: " + deployment.name)
deployment.describe()

state = deployment.get_state()

if state.status != "Running":
    deployment.start()
    deployment.describe()
else:
    print("Deployment already running")


"""
Now that the model is deployed, we need to get the data from Hopsworks
to generate data to predict on.
"""
fs = project.get_feature_store()

# Load feature group.
zip_code = '60603'  # Chicago
country_code = 'US'
city = 'Chicago'

fg_name = f'aqi_{city}_{zip_code}'.lower()

aqi_online_fg = fs.get_feature_group(fg_name, version=1)

not_features = ['date', 'lat', 'lon']

ds_query = aqi_online_fg.select_except(not_features)

fv_name = f'{fg_name}_fv'

try:
    feature_view = fs.get_feature_view(name=fv_name, version=1)
except: 
    print('Feature view not created. Fatal error.')
    sys.exit('Quitting now...')

end_date = pd.to_datetime(fs.sql(f"SELECT MAX(`datetime`) FROM `{fg_name}_1`", online=True).values[0][0])
start_date = pd.to_datetime(fs.sql(f"SELECT MIN(`datetime`) FROM `{fg_name}_1`", online=True).values[0][0])

print('Start date, end date of historical data ', start_date, end_date)

start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

train_x, train_y = feature_view.get_training_data(1)

# check that we have the right time period for train and test
print('Min and max time in returned training set from Hopsworks:')
print(train_x['datetime'].min(), train_x['datetime'].max())

# need to convert datetime from strings
train_x.datetime = pd.to_datetime(train_x.datetime)

# data points are not in order
train_x = train_x.sort_values("datetime")
train_y = train_y.reindex(train_x.index)

# need to remove time zone information
train_x['datetime'] = train_x['datetime'].dt.tz_localize(None)

# use the datetime as index now
train_x = train_x.reset_index(drop=True)
train_x = train_x.set_index('datetime')

train_y = train_y.reset_index(drop=True)
train_y = train_y.set_index(train_x.index)
train_y['aqi'] = train_y['aqi']-1  # xgboost requires zero indexed categories for classification

# concat
df = pd.concat([train_x, train_y], axis=1)
df = df.drop(columns=['id'])

# create future data
future_start = df.index.max() + pd.Timedelta('1 hours')
future_end = future_start + pd.Timedelta('3 days') - pd.Timedelta('1 hours')

future = pd.date_range(future_start, future_end, freq='1h')
future_df = pd.DataFrame(index=future)
future_df['isFuture'] = True
df['isFuture'] = False

df_and_future = pd.concat([df, future_df])

# create all of the features needed for training
df_and_future = createFeatures(df_and_future)

# isolate historical data and future data
df = df_and_future.query('isFuture==False').copy()
df = df.drop(columns=['isFuture'])
future_w_features = df_and_future.query('isFuture').copy()
future_w_features = future_w_features.drop(columns=['isFuture'])

# predict with model
features = ['hour', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear',
           'dayofmonth', 'weekofyear', 'co_lag3d', 'no_lag3d', 'no2_lag3d',
           'o3_lag3d', 'so2_lag3d', 'pm2_5_lag3d', 'pm10_lag3d', 'nh3_lag3d',
           'aqi_lag3d', 'aqi_max_lag_3d', 'aqi_mean_lag_3d', 'aqi_std_lag_3d']
target = 'aqi'

data = {"instances" : future_w_features[features].to_json()}
res = deployment.predict(data)
print(res["predictions"])

