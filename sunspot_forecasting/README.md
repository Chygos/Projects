
# FORECASTING MONTHLY SUN SPOTS

## Overview
The sun is composed of a moving electrically charged hot gas that generates a powerful magnetic field that goes through a cycle called the solar cycle. A solar cycle is a cycle that the sun's magnetic field makes at approximately every 11 years. At every 11 years or so, this magnetic field flips completely with the north pole switching places with the south pole of the sun. In another 11 years, they switch back places to their original state. Solar cycle affects the activity on the Sun's surface, one of which is the sunspots which are caused by the sun's magnetic fields. As the magnetic fields change, the amount of activity on the Sun's surface does the same.

To track the solar cycle, one way is to count the number of sunspots. At the beginning of a solar cycle is the solar minimum when the sun has the least sunspots. Overtime, the solar activity as well as the number of sunspots increases. At the middle of the cycle is the solar maximum where the number of sunspots are the highest and as the cycle ends, the number of sunspots fades back to the solar minimum and then a new cycle begins. Apart from the number of sunspots, other solar activities such as giant eruptions of the sun such as solar flares and coronal mass ejections also increase during the solar cycle, releasing powerful bursts of energy and material into space.

The Earth can also be affected by solar activities. For example, lights in the sky called aurora, impact on radio communications, and electricity grids. It can also cause a huge effect on satellite electronics and limit their lifespan and as well, can affect astronauts that work in International Space Stations. Some cycles can have minimums with lots of sunspots and activity while other cycles can have very few subspots and little activity. As a result of the effects of solar activity on Earth, it is important to predict the strength and duration of solar cycles. This will enable scientists forecast these solar conditions (space weather) and help them to protect radio communications on Earth, help keep satellites of space stations (eg. NASA) and keep astronauts safe by delaying their spacewalks.

In this project, we will forecast the monthly average number of sunspots for 2023. We will also forecast the average yearly sunspots for the next 11 years.


## Dataset
The dataset contains daily sunspots observed from Jan. 1818 till Dec. 2022. There are days when no sunspots were recorded; these were replaced with -1 indicating missing values.


## Data Visualisation and Analysis
### Research Questions
- What is the average yearly sunspots over time (1818-2022)?
- What is the summary statistics of monthly sunspots recorded between 1818-2022?
- What month of the year did we have the least and highest number of sunspots?
- Are there months in the year when sunspots are more?
- Is there any difference in the monthly sunspots recorded in the last 50 years?
- Forecasting average monthly sunspots for the next 12 months in 2023
- Forecasting average yearly sunspots to be observed for the next 11 years (2023-2033)

## Model Development
- An Auto-Regressive Integrated Moving Average (ARIMA) time series model was used to 
  a) forecast average monthly sun spots for 2023 and 
  b) forecast average sunspots to be observed for the next 11 years (2023-2033)

- For both forecasting tasks, datasets were split into train and test sets. The training data was used to develop a time-series model and performance was evaluated on the test sets using the root mean squared error (RMSE) and the mean absolute error (MAE). For task (a), sunspots observed in the months of the year 2022 were used for testing while for task (b), sunspots observed past 10 years were used as the test data.

### Results (On Test set)

Optimal p,d,q values for both tasks a and b were 3,0,2 respectively.

Task | RMSE | MAE
----|-----|-----
A | 15.9218 | 12.9170
B | 18.0323 | 14.9751


![Figure 1: Monthly sunspot for 2022](https://user-images.githubusercontent.com/46559140/213817852-5e4233e0-09b1-4056-aa3f-4014617ea6d3.png)

_Figure 1: Monthly sunspot for 2022_


![Figure 2: Yearly sunspot predictions for 2013-2022](https://user-images.githubusercontent.com/46559140/213822776-2027a5fc-f84d-4098-8a0b-74e95df304a0.png)

_Figure 2: Yearly sunspot forcast for 2013-2022_

## Forecasting

For task a, the average number of sunspots to be observed in all the months in 2023 were forecasted. 

![Figure 3: Forecast for January to December, 2023](https://user-images.githubusercontent.com/46559140/213821640-8e493465-2df7-42bc-8063-e4ab4b297a93.png)

_Figure 3: Forecast for January to December, 2023_

![Figure 4: Forecast for 2023-2033](https://user-images.githubusercontent.com/46559140/213818508-07a0855e-323e-499d-9e5c-e4b3683e5f6e.png)

_Figure 4: Forecast for 2023-2033_

## Summary
- Evidence exists that Solar cycle lasts about 11 years
- Between Dec. 1818 till Dec. 2022, 18 solar cycles have occurred.
- The highest average number of sunspots per cycle observed between 1954-1964, with a over 240 sunspots seen at its solar maximum (1957) around that time.
- Since the last three cycles, the solar maximum have decreased.
- The average total sunspots per year is 28,730 while the average number of sunspots observed per month of every year is 83
-  There is no statistical evidence to conclude that there's a difference in means between the number of sunspots observed the last 50 years (pvalue (0.78) > 0.05)
-  Optimal p,d,q order values for both tasks a and b were 3,0,2 respectively
-  For both tasks, the model seem to have modelled the cyclical pattern of sunspots per year.
-  Model's confidence for the monthly predictions seems to get worse from the 3rd/4th month in 2023 while its confidence for the yearly forecasts is higher.
-  Model forecasts that the next solar cycle will peak at its maximum height in 2024, with the cycle completing between 2029 and 2030

### Resources
Hyndman, R.J., & Athanasopoulos, G. (2018) Forecasting: principles and practice, 2nd edition, OTexts: Melbourne, Australia. OTexts.com/fpp2. Accessed on 20th January, 2023.
