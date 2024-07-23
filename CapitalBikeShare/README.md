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

A Bike sharing system is a shared transport service where bicycles are available for shared use by individuals at low cost. It allows individuals borrow a bicycle from a station, ride it to a specific destination and then return it to any station within the system. Bike sharing presents benefits such as convenience, affordability, eco-friendly and it is a great way for bikers to get some exercise and fresh air.

In this notebook, we analyse the total hourly demand of bikes in all stations in Washington DC. This bike service is provided by [Capital bikeshare](https://capitalbikeshare.com/) where an individual can unlock a bike by scanning its QR code using an app, ride on it and then park it at the nearest docking station in their destination. Two types of bikes are provided - electric (E-bikes) and classic bikes- and an individual can rent them on short-term option by renting a single ride, obtain a day pass or monthly membership and long-term by an annual membership option.

## Analysis Plan

In this analysis, we will be investigating the hourly demand of bikes by residents of Washington DC between Jan 2022 and June 2024. We want to understand 

- The performance of bike sharing in Washington DC
- The acceptance of bike sharing system by Washington DC residents
- The bike type preference of residents
- The demand of bikes at specific hours of the day, day of the week, or month or season of the year for better service.
- The user base: casual or members


## Dataset Description

Variable | Description
-------- | -----------
rideable_type | Type of bike (E-bike or classic bike)
pickup hour | Date and time (in hour of day) of pickup 
member_casual | Indicates if user is a registered member or casual user.<br>A member is one who is an annual member, 30-day member of day key member.<br>A casual ride includes single trips, 1, 3, or 5-day Pass
num_rides | Total number of bike rides
duration_secs | Average duration of trips in seconds
distance_km | Total distance travelled in kilometres
duration_mins | Average duration in minutes



