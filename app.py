import xgboost as xgb
import pandas as pd
import os
import sys
from my_functions import createFeatures
import gradio as gr
pd.options.plotting.backend = "plotly"
import plotly.express as px

"""
Load data, XGBoost model, then predict and present using Gradio.
"""
def get_forecast():
    zip_code = '60603'  # Chicago
    country_code = 'US'
    city = 'Chicago'

    aqi_table_name = f'aqi_{city}_{zip_code}'.lower()

    data_path = os.path.join('data', f'{aqi_table_name}.csv')

    if os.path.exists(data_path):
        df = pd.read_csv(data_path, index_col='datetime', parse_dates=True)
    else:
        sys.exit('Cannot find AQI data. Quitting now...')

    future_start = df.index.max() + pd.Timedelta('1 hours')
    future_end = future_start + pd.Timedelta('3 days') - pd.Timedelta('1 hours')

    future = pd.date_range(future_start, future_end, freq='1h')
    future_df = pd.DataFrame(index=future)
    future_df['isFuture'] = True
    df['isFuture'] = False

    df_and_future = pd.concat([df, future_df])

    df_and_future = createFeatures(df_and_future)
    df_and_future['aqi'] = df_and_future['aqi'] - 1

    df = df_and_future.query('isFuture==False').copy()
    future_w_features = df_and_future.query('isFuture').copy()
    future_w_features = future_w_features.drop(columns=['isFuture'])

    model_dir = 'aqi_model'
    if os.path.isdir(model_dir) == False:
        os.mkdir(model_dir)

    model_name = 'xgboost_aqi_model.json'
    model_path = os.path.join(model_dir, model_name)

    xgb_clf = xgb.XGBClassifier()
    xgb_clf.load_model(model_path)

    features = ['hour', 'dayofweek', 'quarter', 'month', 'year', 'dayofyear',
        'dayofmonth', 'weekofyear', 'co_lag3d', 'no_lag3d', 'no2_lag3d',
        'o3_lag3d', 'so2_lag3d', 'pm2_5_lag3d', 'pm10_lag3d', 'nh3_lag3d',
        'aqi_lag3d', 'aqi_max_lag_3d', 'aqi_mean_lag_3d', 'aqi_std_lag_3d']
    target = 'aqi'

    forecast = xgb_clf.predict(future_w_features[features])
    future_w_features['aqi'] = forecast
    future_w_features['aqi'] = future_w_features['aqi'] + 1
    df['aqi'] = df['aqi'] + 1
    
    future_w_features['isFuture'] = True
    df['isFuture'] = False
    
    history_start = future_start - pd.Timedelta('7 days')
    historical_plot = df.query('index > @history_start').copy()
    
    data = pd.concat([historical_plot, future_w_features])

    fig = px.line(data, x=data.index, y='aqi', color='isFuture', 
        labels={'index': 'Date', 'aqi': 'Air Quality Index'})
    return fig 


with gr.Blocks() as demo:
    gr.Markdown(
    """
    **Air Quality Index (AQI) Prediction 📈 with XGBoost Forecasting**: See recent air quality in Chicago and a 3-day forecast!
    """)

    gr_plt = gr.Plot()

    gr.Markdown(
    """
    **Description**: The air quality index is based on the concentration of a number of pollutants such as ozone, ammonia, and particulates. 
    I trained an XGBoostClassifier model using a little over two years' worth of historical data from OpenWeather. Then I predict the next three days
    of air quality indices at an hourly resolution. Because training an XGBoostClassifier has some degree of stochasticity, predictions for a particular
    time may change after the model is retrained. New data is downloaded roughly every three days, and the model is automatically retrained. This is my
    first machine learning project where I've gathered my own data and deployed a model. It is also the first time series forecasting project I've done.
    Unfortunately, my model doesn't have the great of performance. The log-loss baseline for the training set is about 0.68 and I wasn't
    able to get below that in cross-validation. This means that the model is no better than randomly guessing the air quality index.
    However, I think with some better feature engineering the model could perform substantially better. Nevertheless, I've learned
    so much about data science, machine learning, GitHub, Gradio, and Hugging Face Spaces with this project and that's what counts.
    """)

    demo.load(fn=get_forecast, outputs=[gr_plt], queue=False)    

demo.launch()