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
Below is a table I copied from [Wikipedia](https://en.wikipedia.org/wiki/Air_quality_index#CAQI) that
shows the thresholds for each AQI index.

<tbody><tr>
<th>Qualitative name</th>
<th>Index or sub-index</th>
<th colspan="4">Pollutant (hourly) concentration
</th></tr>
<tr>
<th colspan="2"></th>
<th>NO<sub>2</sub> μg/m<sup>3</sup></th>
<th>PM<sub>10</sub> μg/m<sup>3</sup></th>
<th>O<sub>3</sub> μg/m<sup>3</sup></th>
<th>PM<sub>2.5</sub> (optional) μg/m<sup>3</sup>
</th></tr>
<tr>
<td>Very low</td>
<td style="background:#79bc6a;">0–25</td>
<td>0–50</td>
<td>0–25</td>
<td>0–60</td>
<td>0–15
</td></tr>
<tr>
<td>Low</td>
<td style="background:#bbcf4c;">25–50</td>
<td>50–100</td>
<td>25–50</td>
<td>60–120</td>
<td>15–30
</td></tr>
<tr>
<td>Medium</td>
<td style="background:#eec20b;">50–75</td>
<td>100–200</td>
<td>50–90</td>
<td>120–180</td>
<td>30–55
</td></tr>
<tr>
<td>High</td>
<td style="background:#f29305;">75–100</td>
<td>200–400</td>
<td>90–180</td>
<td>180–240</td>
<td>55–110
</td></tr>
<tr>
<td>Very high</td>
<td style="background:#e8416f;">&gt;100</td>
<td>&gt;400</td>
<td>&gt;180</td>
<td>&gt;240</td>
<td>&gt;110
</td></tr>
</tbody>

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
