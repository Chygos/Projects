# Capital BikeShare

This repository contains analysis performed on bike rides rented by residents of Washington DC. Bike sharing service is provided by Capital Bikeshare. Dataset was downloaded [here](https://s3.amazonaws.com/capitalbikeshare-data/index.html) and contains hourly bike rides between January 2022 and June 2024. Dataset was collected using an API, the original format was preprocessed, aggregated and stored as a Comma Separated Values (csv) file.

Variables include

Name | Description
---- | -----------
Rideable Type | Type of bike (E-bike or classic)
Duration | Duration of trip
Start Date | Start date and time
End Date | End date and time
Start Station | Starting station name and number
End Station | Ending station name and number
Bike Number | ID number of bike used for the trip
Member Type | Indicates if a user is a registered user or a casual user.
Start and End coordinates | Latitude and longitude points of start and end stations


## Introduction 

A Bike sharing system is a shared transport service where bicycles are available for shared use by individuals at low cost. It allows individuals to borrow a bicycle from a station, ride it to a specific destination and then return it to any station within the system. Bike sharing presents benefits such as convenience, affordability, eco-friendly and it is a great way for bikers to get some exercise and fresh air.

In this notebook, we analyse the total hourly demand for bikes in all stations in Washington DC. This bike service is provided by [Capital Bikeshare](https://capitalbikeshare.com/) where an individual can unlock a bike by scanning its QR code using an app, ride on it and then park it at the nearest docking station at their destination. Two types of bikes are provided - electric (E-bikes) and classic bikes- and an individual can rent them on the short-term option by renting a single ride, obtaining a day pass or monthly membership and long-term by an annual membership option.

## Analysis Plan

In this analysis, we investigated the hourly demand for bikes (bicycles) by residents of Washington DC between Jan 2022 and June 2024. We wanted to understand 

- The performance of bike sharing in Washington DC
- The acceptance of the bike sharing system by Washington DC residents (users).
- The bike type preference of residents
- The demand for bikes at specific hours of the day, day of the week, or month or season of the year for better service.

To understand the performance of bike sharing in Washington DC, performance was measured based on key performance indicators, such as the total number of bike rides made between Jan 2022 and Jun 2024, the average hourly rides, the average distance travelled and the duration of bike trips. These metrics were extended to the bike types and membership status of users.

Citybikeshare offers two types of bikes (classic and E-bikes) for residents who are registered members and those who use them for casual use. To understand user preference, the percentage of rides made by registered or unregistered members and the percentage of rides made using classic or electric bikes were investigated. This was extended to preference between and within bike type and membership status. For instance, by finding the percentage of rides made by non-members or members using either bike type and the percentage of members or non-members who used either classic or bike types.

In 2020, the world was hit by the global COVID-19 pandemic. This event disrupted business, social and human activities. To understand the resumption of human and social activities, bike ride acceptance by Washington DC residents was investigated. This was done by estimating the average demand rate (percentage change) at specific time frames (hour, daily, and monthly). Acceptance was further investigated by comparing the average demand rate by bike type and comparing the year-over-year percentage change at these time frames (hourly, monthly, seasonally and yearly).

It is assumed that bike demand is affected by time. To answer this, we looked at the temporal variations of bike rides from Jan 2022 and Jun 2024, smoothened by a 28-day moving average. Next, the demand was divided into smaller groups (hourly, weekday, and monthly demands). This was extended by examining the demand for classic and electric bikes by users (members and non-members) at these time points.

## Dataset Description

Variable | Description
-------- | -----------
rideable_type | Type of bike (E-bike or classic bike)
pickup hour | Date and time (in hour of day) of pickup 
member_casual | Indicates if user is a registered member or casual user.<br>A member is an annual member, 30-day member or day key member.<br>A casual ride includes single trips, 1, 3, or 5-day Pass
num_rides | Total number of bike rides
duration_secs | Average duration of trips in seconds
distance_km | Total distance travelled in kilometres
duration_mins | Average duration in minutes

## Analysis Findings

### Bike Performance

__Table 1: Bike Ride Performance__

|Name                  |Values        |
|:---------------------|-------------:|
|Total_Rides           | 10,190,395.00|
|Average_Hourly_Demand |        117.64|
|Average_Distance_km   |          1.00|
|Average_Duration_mins |         18.71|

Over 10.1 million bike rides were made between Jan 2022 and June 2024. This is about 117 rides per hour on average, with each user travelling at least 1 km in an average time of 19 minutes.

__Table 2: Performance by Membership Type__

|Name                  | Non-members| Members|
|:---------------------|-----------:|-------:|
|Average_Hourly_demand |       84.18|  150.76|
|Average_Distance_km   |        1.04|    0.96|
|Average_Duration_mins |       23.81|   13.67|

Registered members on the bike-sharing platform use more bikes than casual users. On average, a total of 84 bikes are requested by casual users while about 150 by registered members. Non-members use bikes mostly for long trips. Each trip embarked on by a casual user lasts at least 1 km on average in about 24 minutes while it is about 0.96 km in about 14 minutes for members.

__Table 3: Performance by Bike Type__

|Name                  | Classic| Electric|
|:---------------------|-------:|--------:|
|Average_Hourly_demand |  161.84|    73.42|
|Average_Distance_km   |    0.87|     1.12|
|Average_Duration_mins |   23.37|    14.06|

On the other hand, classic bikes are rented more than electric bikes. About 162 bikes are requested by users on average while it is about 73 for electric bikes. Electric bikes are mostly used for longer trips by users while classic bikes are used for shorter trips. A distance of 1.12 km was covered using electric bikes in a shorter time of about 14 minutes, while a distance of 870 m was covered by classic bike users in about 23 minutes on average. This is quite relatable due to the speed and convenience of electric bikes where so much efforts are needed to ride them, unlike the manual classic bikes.

![Percentage of rides by bike type](BikeSharesAnalysis/output_36_0.png)




