---
title: Chicago Air Quality Index Prediction with XGBoost
emoji: 🌇
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 3.16.2
app_file: app.py
pinned: false
---
^ Ignore this as this is required for my Hugging Face Space, which you can access 
here: [🤗](https://huggingface.co/spaces/giorgiolatour/aqiprediction) (click on the emoji).

## Introduction

In this repo is my Air Quality Index (AQI) for Chicago machine learning project. 

### Technologies Used
---
1. Python
2. XGBoost Classification
3. OpenWeatherAPI for air quality index data
4. Gradio and HuggingFace Spaces to deploy the model
5. GitHub for hosting the repository

Alright, so what even is an AQI? An AQI is a measure of the levels of specific pollutants in the air. 
There is a table here [Wikipedia](https://en.wikipedia.org/wiki/Air_quality_index#CAQI) that
shows the concentration thresholds for each AQI index.

The objective was to train a machine learning model on historical time series AQI data for a given city (I chose Chicago) 
and then produce a 3-day hourly forecast of the AQI for the city. New data is downloaded twice a week, and an XGBoost Classifier 
is retrained automatically using GitHub actions!

The AQI data is downloaded from OpenWeather using their API. They discretize the AQI as 1-5, with 5 being the worst air quality, 
rather than the sub-index shown in the table above. 

In this project I learned a ton about data science and machine learning. More specifically, I did time series feature engineering,
learned about XGBoost classification, GitHub (Actions and Secrets!), as well as how to host my Gradio app that shows a week of 
data and a three day forecast on Hugging Face Spaces! Go to the link at the top of the README to check it out!

This project was born from an idea I found on [Twitter](https://datamachines.xyz/2022/11/22/build-a-prediction-service-with-machine-learning-step-by-step/) 
by Pau Labarta Bajo. He suggests using a feature store called Hopsworks, and I relentlessly tried to do so. 
Near the end of this project, I had had so many headaches caused by trying to use Hopsworks that 
I abandoned it. I think it added an extra layer of complexity that wasn't really needed here.
