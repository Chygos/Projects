![page_image](images/page_design.png)

# [Forecasting Household Hourly Electricity Consumption Rate](https://www.kaggle.com/competitions/predict-electricity-consumption)

## Description

This repository contains a group project for the Introduction to Data Science course of the University of Tartu.
Project will be undertaken by 

- Wei-Chieh Wang
- Patricia Kika Obinwanne
- Chigozie Nkwocha

## Introduction

Since the Russian invasion on Ukraine, energy, rent and food costs have skyrocketed. World economies are now faced with record high losses in revenue. Workers are now being laid off because their employers are no longer capable of paying their salaries in a bid to cut costs. Small businesses as well, are now forced to close due to huge operational costs. As a result, electricity consumers around the world are now seeking for better ways of reducing electricity costs and conserving energy.

Similarly, the excessive use of electricity causes an increase in the environmental carbon footprint. Enefit, one of the largest energy companies in the Baltic countries is strategizing on a better approach to help their customers achieve their goal while preserving the environment from excess release of carbon. One possible strategy is to forecast energy consumption for a household and optimise its energy usage by controlling smart devices in such a way that they minimise energy cost and the environmental footprint of consumption. Another is the use of solar panels and other forms of cheaper electricity.

## Aim
In this project, we aim to develop a predictive model capable of forecasting electricity consumption for a household for the next 7 days. We intend that this project will enable consumers understand their electricity usage and identify the hour(s) of the day when usage is high or least. 

## Objectives
- Use Data visualisation to understand electricity consumption of household
- Develop at least two machine learning models to predict electricity consumption
- Compare classical time series model (ARIMA) with machine learning model
- Forecast electricity consumption for the next 7 days

## Data
To accomplish this, we will use a historical dataset containing a household's hourly electricity consumption used between Sept 1st, 2021 to 24th August, 2022. A holdout test set is kept to be used for forecasting. The historical data contains 8,592 hourly electricity consumption, with 168 hourly consumption as test set [[link]](https://www.kaggle.com/competitions/predict-electricity-consumption/data).

### Variables

Variable Name | Definition
--------------|-------------
time |definition of example_id
temp | Air Temperature (°C)
dwpt | The dew point in °C
rhum | The relative humidity in percent (%)
prcp | The one hour precipitation total in mm
snow | The snow depth in mm
wdir | The wind direction in degrees (°)
wspd | The average wind speed in km/h
wpgt | The peak wind gust in km/h
pres | The sea-level air pressure in hPa
coco | The weather [condition code](https://dev.meteostat.net/formats.html#weather-condition-codes)
el_price | the electricity price in Estonia on that hour (€/kWh)
consumption | the electricity consumption (kWh)


## Data Cleaning and Feature Engineering

- Missing values were treated by using a forward fill method, where a missing value was replaced with the data preceding it (since this was a time series), with the assumption that the measurement for the next hour is the same as the previous hour. For prcp and snow, missing values were filled with zero. This is because at those times of the hour, there are no precipitation or snow recorded.
- Lagged features and time-related (week, month, hour etc) features were created.

## Data Visualisation
### Research Questions
- What is the distribution of hourly consumption?
- How does electricity consumption and price vary in the hours of the year?
- What's the average hourly consumption rate for the household and the price set for that hour?
- What time of the day is electricity consumption the highest or least
- Does consumption depend on the atmospheric temperature at that hour?

To answer this question, data visualisation was done to further understand.

### Insights
From our visualisation, we found the following insights,

- Hourly electricity consumption for the household is right-skewed, with most of the consumptions between 0-1 kilowatts (kw). Consumptions of 4-11kw were recorded too. These were outliers

- By investigating the electricity consumption and price for the year under review, we see that electricity consumption for the household increased from August 2021 to Dec 2021, but this soon began to decline at the onset of the Russian war. Similarly, electricity prices are high (0.1-0.3 cents) from December and January but currently the prices have gone up to about 0.5 cents from April 2022 till August 2022.
To test the hypothesis that the reduction in electricity consumption and the rise in energy bills could be as a result of the Russian Invasion on Ukraine, a t-test statistical test at 5% significance level was conducted. From the result, the pvalue was far lower than the 5% significance level, hence we conclude that the decrease in electricity consumption and the rise in energy bills could be as a result of the invasion of Russia on Ukraine.

- Moving further down to the total monthly electricity consumption, it was discovered that the total electricity consumption begin to rise during the Fall season till Winter seasons and begin to decline in the Spring and Summer seasons. Highest levels were recorded between December 2021 and February 2022, with consumption rates of over 1000 kw.

- Moving over to the hourly consumption rates, it was discovered that electricity consumption are the highest between 5-8 PM, with lower levels in the Afternoons between 11 am and 2 PM.

- To determine the relationship between temperature and consumption, a pearson's correlation coefficient was used, and from the coefficient (-0.25), temperature has a weak negative relationship with electricity consumption.


## Model Development Approach
- Classical time series model: AutoRegressive Integrated Moving Average (ARIMA)
- Machine learning models (Random forest and Gradient Boosting algorithms) by creating lagged features.

To train the ARIMA model, the features: temp, dwpt, rhum, prcp, snow, wdir, wspd, wpgt, pres and el_price were used as covariates. These covariates were scaled using the z-score method where the mean of each covariate was subtracted from their values and scaled by their standard deviation. Also, to reduce the effect of outliers, the dependent variable was transformed by multiplying each value by 10 and taking a natural logarithm transformation of values which were shifted by 1. The predicted values were transformed back to the original values. For random forests and lightGBM algorithms, lagged features of the dependent variable were created.


### Data Splitting and Hyperparameter Tuning
Dataset was split into two: train and heldout set with the heldout set containing electricity consumption last 7days. To get the optimal p,d,q values of the ARIMA model, the _auto_arima_ function from _pmdarima_ package was used. 
For the two machine learning algorithms used, hyperparameter tuning was performed using a 5-fold cross validation strategy where the _TimeSeries_ split function from _Scikit-learn_ was used to maintain the time series structure. During each iteration, the hourly consumption for the last 7 days was used for validation.


### Model Evaluation
Main metric will be Mean Absolute error (MAE). The root mean squared error (RMSE) will be used also

## Results (Heldout data)
Model | MAE | RMSE|
------|-----|------
ARIMA | 0.4359 | 0.6099
Random forest| 0.3307 | 0.4480
LightGBM| 0.3272 | 0.4754

- From the result, random forest and gradient boosting (LightGBM) performed better than the classical ARIMA model, with MAE scores between 0.32 and 0.34, and RMSE values between 0.44 and 0.48 respectively which were better than the result from ARIMA
