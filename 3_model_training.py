import pandas as pd
from my_functions import createFeatures
import xgboost as xgb
import os
import sys
import logging
import logging.handlers

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

data_path = os.path.join('data', f'{aqi_table_name}.csv')

if os.path.exists(data_path):
    df = pd.read_csv(data_path, index_col='datetime', parse_dates=True)
else:
    logger.info(f'{aqi_table_name} doesn\'t exist. Quitting now...') 
    sys.exit(f'{aqi_table_name} doesn\'t exist. Quitting now...')

# create all of the features needed for training
df = createFeatures(df)
df['aqi'] = df['aqi'] - 1

# train model
features = ['hour', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear',
           'dayofmonth', 'weekofyear', 'co_lag3d', 'no_lag3d', 'no2_lag3d',
           'o3_lag3d', 'so2_lag3d', 'pm2_5_lag3d', 'pm10_lag3d', 'nh3_lag3d',
           'aqi_lag3d', 'aqi_max_lag_3d', 'aqi_mean_lag_3d', 'aqi_std_lag_3d']
target = 'aqi'

x_all = df[features]
y_all = df[target]

logger.info(f'Starting XGBoost training...') 
clf = xgb.XGBClassifier(n_estimators=1000, 
                        booster='gbtree',
                        early_stopping_rounds=50,
                        max_depth=4,
                        learning_rate=0.01
                       )

clf.fit(x_all, y_all, eval_set=[(x_all, y_all)])
logger.info(f'Done training XGBoost.') 

# Save model.
model_dir = 'aqi_model'
if os.path.isdir(model_dir) == False:
    os.mkdir(model_dir)

model_name = 'xgboost_aqi_model.json'
model_path = os.path.join(model_dir, model_name)

clf.save_model(model_path)
logger.info(f'Saved new XGBoost model.') 