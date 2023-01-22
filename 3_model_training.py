import hopsworks
import datetime
import pandas as pd
from my_functions import createFeatures
import xgboost as xgb
import joblib
import os
from hsml.schema import Schema
from hsml.model_schema import ModelSchema


project = hopsworks.login()

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
    feature_view = fs.create_feature_view(
    name=fv_name,
    version=1,
    description='feature view for creating training data',
    query=ds_query,
    labels=['aqi', 'id'],  # not using ID as a label, just for keeping track of data order
)

end_date = pd.to_datetime(fs.sql(f"SELECT MAX(`datetime`) FROM `{fg_name}_1`", online=True).values[0][0])
start_date = pd.to_datetime(fs.sql(f"SELECT MIN(`datetime`) FROM `{fg_name}_1`", online=True).values[0][0])

print('Start date, end date of historical data ', start_date, end_date)

start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

# Create training datasets based event time filter
# train_d, train_d_job = feature_view.create_training_data(
#         start_time = start_date_str,
#         end_time = end_date_str,    
#         description = f'aqi data for training {start_date_str} to {end_date_str}',
#         data_format = "csv",
#         coalesce = True,
#         write_options = {'wait_for_job': False},
# )

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

# create all of the features needed for training
df = createFeatures(df)

# train model
features = ['hour', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear',
           'dayofmonth', 'weekofyear', 'co_lag3d', 'no_lag3d', 'no2_lag3d',
           'o3_lag3d', 'so2_lag3d', 'pm2_5_lag3d', 'pm10_lag3d', 'nh3_lag3d',
           'aqi_lag3d', 'aqi_max_lag_3d', 'aqi_mean_lag_3d', 'aqi_std_lag_3d']
target = 'aqi'

x_all = df[features]
y_all = df[target]

clf = xgb.XGBClassifier(n_estimators=1000, 
                        booster='gbtree',
                        early_stopping_rounds=50,
                        max_depth=4,
                        learning_rate=0.01
                       )

clf.fit(x_all, y_all, eval_set=[(x_all, y_all)])

# dump model
# The 'aqi_model' directory will be saved to the model registry
model_dir = 'aqi_model'
if os.path.isdir(model_dir) == False:
    os.mkdir(model_dir)
    
joblib.dump(clf, model_dir + '/xgboost_aqi_model.pkl')

mr = project.get_model_registry()

input_schema = Schema(future_w_features[features])
output_schema = Schema(future_w_features[target])
model_schema = ModelSchema(input_schema=input_schema, output_schema=output_schema)

model_schema.to_dict()

aqi_model = mr.python.create_model(
    name='xgboost_aqi_model', 
    model_schema=model_schema,
    input_example=future_w_features[features].sample().to_numpy(), 
    description="AQI Predictor")

aqi_model.save(model_dir)