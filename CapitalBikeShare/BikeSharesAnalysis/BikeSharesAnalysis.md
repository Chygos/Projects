## Introduction

A Bike sharing system is a shared transport service where bicycles are available for shared use by individuals at low cost. It allows individuals borrow a bicycle from a station, ride it to a specific destination and then return it to any station within the system. Bike sharing presents benefits such as convenience, affordability, eco-friendly and it is a great way for bikers to get some exercise and fresh air.

In this notebook, we analyse the total hourly demand of bikes in all stations in Washington DC. This bike service is provided by [Capital bikeshare](https://capitalbikeshare.com/) where an individual can unlock a bike by scanning its QR code using an app, ride on it and then park it at the nearest docking station in their destination. Two types of bikes are provided - electric (E-bikes) and classic bikes- and an individual can rent them on short-term option by renting a single ride, obtain a day pass or monthly membership and long-term by an annual membership option.

## Dataset Description

Dataset includes hourly bike rides made by registered and casual users for each bike type. It also includes the total distance travelled and the average duration of the trip in seconds.

Variable | Description
---------| -----------
rideable_type | Type of bike (E-bike or classic bike)
pickup hour   | Date and time (in hour of day) of pickup
member_casual | Indicates if user is a registered member or casual user.<br>A member is one who is an annual member, 30-day member of day key member.<br>A casual ride includes single trips, 1, 3, or 5-day Pass
num_rides     | Total number of bike rides
duration_secs | Average duration of trips in seconds
distance_km   | Total distance travelled in kilometres
duration_mins | The average duration in minutes

## Analysis Plan

In this analysis, we will investigate the hourly demand for bikes by residents of Washington DC between Jan 2022 and June 2024. We want to understand

-   The performance of bike sharing in Washington DC
-   The acceptance of bike sharing system by Washington DC residents
-   The bike type preference of residents
-   Bike demands at specific hours of the day, day of the week, or month or season of the year for better service.

## Data Exploration

In this section, we load our libraries and dataset, check for data quality issues, and do some preliminary data exploration and summary statistics

### Loading libraries and dataset


```R
# load libraries
library(tidyverse)
library(lubridate)
library(ggthemes)
library(ggpubr)
```

    Warning message:
    "package 'ggplot2' was built under R version 4.3.3"
    ── [1mAttaching core tidyverse packages[22m ──────────────────────── tidyverse 2.0.0 ──
    [32m✔[39m [34mdplyr    [39m 1.1.4     [32m✔[39m [34mreadr    [39m 2.1.5
    [32m✔[39m [34mforcats  [39m 1.0.0     [32m✔[39m [34mstringr  [39m 1.5.1
    [32m✔[39m [34mggplot2  [39m 3.5.1     [32m✔[39m [34mtibble   [39m 3.2.1
    [32m✔[39m [34mlubridate[39m 1.9.3     [32m✔[39m [34mtidyr    [39m 1.3.1
    [32m✔[39m [34mpurrr    [39m 1.0.2     
    ── [1mConflicts[22m ────────────────────────────────────────── tidyverse_conflicts() ──
    [31m✖[39m [34mdplyr[39m::[32mfilter()[39m masks [34mstats[39m::filter()
    [31m✖[39m [34mdplyr[39m::[32mlag()[39m    masks [34mstats[39m::lag()
    [36mℹ[39m Use the conflicted package ([3m[34m<http://conflicted.r-lib.org/>[39m[23m) to force all conflicts to become errors
    Warning message:
    "package 'ggthemes' was built under R version 4.3.3"
    

    ── [1mAttaching core tidyverse packages[22m ──────────────────────── tidyverse 2.0.0 ──
    [32m✔[39m [34mdplyr    [39m 1.1.4     [32m✔[39m [34mreadr    [39m 2.1.5
    [32m✔[39m [34mforcats  [39m 1.0.0     [32m✔[39m [34mstringr  [39m 1.5.1
    [32m✔[39m [34mggplot2  [39m 3.5.1     [32m✔[39m [34mtibble   [39m 3.2.1
    [32m✔[39m [34mlubridate[39m 1.9.3     [32m✔[39m [34mtidyr    [39m 1.3.1
    [32m✔[39m [34mpurrr    [39m 1.0.2     
    ── [1mConflicts[22m ────────────────────────────────────────── tidyverse_conflicts() ──
    [31m✖[39m [34mdplyr[39m::[32mfilter()[39m masks [34mstats[39m::filter()
    [31m✖[39m [34mdplyr[39m::[32mlag()[39m    masks [34mstats[39m::lag()
    [36mℹ[39m Use the conflicted package ([3m[34m<http://conflicted.r-lib.org/>[39m[23m) to force all conflicts to become errors
    Warning message:
    "package 'ggthemes' was built under R version 4.3.3"
    


```R
# read dataset
bike_shares <- read_csv('../data/bike_shares.csv', show_col_types=FALSE)

head(bike_shares)
```


<table class="dataframe">
<caption>A tibble: 6 × 7</caption>
<thead>
	<tr><th scope=col>rideable_type</th><th scope=col>pickup_hour</th><th scope=col>member_casual</th><th scope=col>num_rides</th><th scope=col>duration_secs</th><th scope=col>distance_km</th><th scope=col>duration_mins</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dttm&gt;</th><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>classic</td><td>2022-01-01 00:00:00</td><td>casual</td><td>74</td><td>1423.2838</td><td>83.63551</td><td>23.72</td></tr>
	<tr><td>classic</td><td>2022-01-01 00:00:00</td><td>member</td><td>46</td><td> 824.1304</td><td>48.37800</td><td>13.74</td></tr>
	<tr><td>classic</td><td>2022-01-01 01:00:00</td><td>casual</td><td>62</td><td>5765.0323</td><td>68.64153</td><td>96.08</td></tr>
	<tr><td>classic</td><td>2022-01-01 01:00:00</td><td>member</td><td>52</td><td>2460.0192</td><td>48.85865</td><td>41.00</td></tr>
	<tr><td>classic</td><td>2022-01-01 02:00:00</td><td>casual</td><td>53</td><td>1260.0943</td><td>61.43929</td><td>21.00</td></tr>
	<tr><td>classic</td><td>2022-01-01 02:00:00</td><td>member</td><td>40</td><td>1332.9750</td><td>32.81891</td><td>22.22</td></tr>
</tbody>
</table>



### Data Quality checks


```R
# checking for missing values and duplicate rows
anyDuplicated(bike_shares)
anyNA(bike_shares)

# No duplicate rows or missing values
```


0



FALSE


### Descriptive statistics


```R
# skimr::skim(bike_shares)
```


```R
ggpubr::get_summary_stats(bike_shares)
```


<table class="dataframe">
<caption>A tibble: 4 × 13</caption>
<thead>
	<tr><th scope=col>variable</th><th scope=col>n</th><th scope=col>min</th><th scope=col>max</th><th scope=col>median</th><th scope=col>q1</th><th scope=col>q3</th><th scope=col>iqr</th><th scope=col>mad</th><th scope=col>mean</th><th scope=col>sd</th><th scope=col>se</th><th scope=col>ci</th></tr>
	<tr><th scope=col>&lt;fct&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>num_rides    </td><td>86624</td><td>1.00</td><td>    1054.00</td><td> 61.000</td><td> 19.000</td><td> 171.000</td><td>152.000</td><td> 78.578</td><td> 117.639</td><td>  138.921</td><td>  0.472</td><td>  0.925</td></tr>
	<tr><td>duration_secs</td><td>86624</td><td>2.00</td><td>12416775.64</td><td>816.960</td><td>669.260</td><td>1138.663</td><td>469.403</td><td>283.410</td><td>1306.695</td><td>43991.862</td><td>149.470</td><td>292.959</td></tr>
	<tr><td>distance_km  </td><td>86624</td><td>0.00</td><td>   16526.46</td><td> 60.956</td><td> 18.756</td><td> 156.844</td><td>138.088</td><td> 76.401</td><td> 110.560</td><td>  148.942</td><td>  0.506</td><td>  0.992</td></tr>
	<tr><td>duration_mins</td><td>86624</td><td>0.03</td><td>  206946.26</td><td> 13.620</td><td> 11.150</td><td>  18.980</td><td>  7.830</td><td>  4.729</td><td>  21.778</td><td>  733.198</td><td>  2.491</td><td>  4.883</td></tr>
</tbody>
</table>




```R
unique(bike_shares$rideable_type)

unique(bike_shares$member_casual)
```


<style>
.list-inline {list-style: none; margin:0; padding: 0}
.list-inline>li {display: inline-block}
.list-inline>li:not(:last-child)::after {content: "\00b7"; padding: 0 .5ex}
</style>
<ol class=list-inline><li>'classic'</li><li>'electric'</li></ol>




<style>
.list-inline {list-style: none; margin:0; padding: 0}
.list-inline>li {display: inline-block}
.list-inline>li:not(:last-child)::after {content: "\00b7"; padding: 0 .5ex}
</style>
<ol class=list-inline><li>'casual'</li><li>'member'</li></ol>



### Preliminary Data Exploration

- Here, we will look at the distribution of the variables. For the numerical variables, we will use the histogram, density plots and boxplots while the categorical variables we will use the frequency distribution


```R
# wrapper for figure size
fig.size <- function(width, height){
    options(repr.plot.width = width, repr.plot.height = height)
}
```


```R
plot_frequency <- function(data, colname=NULL, title=NULL){
      df <- data |>
      group_by(.data[[colname]]) |>
      count() |>
      ungroup() |>
      mutate(perc = 100*n/sum(n))
    
      ggplot(data=df, aes(x=.data[[colname]], y=n)) +
      geom_col(fill='steelblue') +
      geom_text(aes(x=.data[[colname]], y=n, label=paste0(round(perc,2),'%')), 
                  vjust=1.4, fontface='bold', color='white', size=5) +
      theme_bw() +
      theme(plot.title=element_text(face='bold', size=16),
            text = element_text(size=16.5), 
            panel.grid=element_blank()) +
      labs(title=title, x=colname, y = 'Frequency') +
      scale_y_continuous(breaks=seq(0, 44000, 7500), 
                        labels=scales::label_number(scale = 1e-3, suffix = 'K'))
}
```


```R
plot_distribution <- function(data, colname=NULL, fill=NULL, title=NULL){
    if (is.null(fill)) {
        box <- ggboxplot(data, y=colname, width=0.4, fill='steelblue', title=title, repel=T) + 
        theme_bw() +
        theme(plot.title=element_text(face='bold', size=16),
              text = element_text(size=16.5),
              panel.grid=element_blank())
        
        hist_ <- gghistogram(data, x=colname, fill='steelblue', bins=40, repel=T, title='') + 
        theme_bw() +
        theme(plot.title=element_text(face='bold', size=16),
              text = element_text(size=16.5),
              panel.grid=element_blank())
        
        ggarrange(box, hist_, ncol=2) 
    } else{
        box <- ggboxplot(data, x=fill, y=colname, width=0.4, fill=fill, title=title, repel=T) + 
        theme_bw() +
        theme(plot.title=element_text(face='bold', size=16), 
              text = element_text(size=16.5),
              legend.position = 'top',
              panel.grid=element_blank())
        
        hist_ <- gghistogram(data, x=colname, fill=fill, alpha=0.6, bins=40, repel=T, title='') + 
        theme_bw() +
        theme(plot.title=element_text(face='bold', size=16),
              text = element_text(size=16.5),
              legend.position = 'top',
              panel.grid=element_blank())
        
        ggarrange(box, hist_, ncol=2, common.legend=T, legend='bottom')
    }
}
```


```R
# categorical variables
fig.size(12,7)
a = plot_frequency(bike_shares, 'member_casual', title='Frequency Distribution for User type')
b = plot_frequency(bike_shares, 'rideable_type', title='Frequency Distribution for Bike Type')

ggarrange(a, b, ncol=2)
```


    
![png](output_17_0.png)
    



```R
# numerical variables
fig.size(12,7)
plot_distribution(bike_shares, 'num_rides', title='Number of Bikes Distribution')
```


    
![png](output_18_0.png)
    



```R
fig.size(12,7)
plot_distribution(bike_shares, 'duration_secs', title='Trip Duration Distribution')
```


    
![png](output_19_0.png)
    



```R
fig.size(12,7)
plot_distribution(bike_shares, 'distance_km', title='Trip Distance Distribution')
```


    
![png](output_20_0.png)
    


There are some strange data points in the distance and duration variables. We will clean them.


```R
# bivariate
fig.size(12,7)
plot_distribution(bike_shares, 'num_rides', fill='member_casual',
                  title='Bike demand by membership type')
```


    
![png](output_22_0.png)
    



```R
fig.size(12,7)
plot_distribution(bike_shares, 'distance_km', fill='member_casual', 
                  title='Trip Distance by membership type')
```


    
![png](output_23_0.png)
    



```R
fig.size(12,7)
plot_distribution(bike_shares, 'duration_mins', fill='member_casual', 
                  title='Trip Duration by membership type')
```


    
![png](output_24_0.png)
    



### Data cleaning

Here, we will remove the extreme values from the duration and distance variables. For the duration, we will bin values above 24 hours (1440 mins or 86400 secs) to 24 hours in minutes or seconds. For distance, we will replace values above 1500km to 1500km


```R
# clean data
bike_shares <- bike_shares %>%
    # binning
    mutate(distance_km = ifelse(distance_km > 1500, 1500, distance_km),
           duration_secs = ifelse(duration_secs > 24*3600, 24*3600, duration_secs),
           duration_mins = ifelse(duration_mins > 24*60, 24*60, duration_mins)) %>%
    # convert to factor variables
    mutate(across(where(is.character), as.factor))
```

## Analysis

### Questions

##### What is the average number of bikes shared in all stations in an hour? What is the average distance and duration travelled by users?


```R
options(scipen = 999)
data.frame(`Total_Rides` = sum(bike_shares$num_rides),
           `Average_Hourly_Demand` = mean(bike_shares$num_rides),
           `Average_Distance_km` = mean(bike_shares$distance_km/bike_shares$num_rides),
           `Average_Duration_mins` = mean(bike_shares$duration_mins)) %>%
    t() %>%
    data.frame(Values=.) %>%
    mutate(Values = round(Values, 2)) %>%
    rownames_to_column('Name')
```


<table class="dataframe">
<caption>A data.frame: 4 × 2</caption>
<thead>
	<tr><th scope=col>Name</th><th scope=col>Values</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>Total_Rides          </td><td>10190395.00</td></tr>
	<tr><td>Average_Hourly_Demand</td><td>     117.64</td></tr>
	<tr><td>Average_Distance_km  </td><td>       1.00</td></tr>
	<tr><td>Average_Duration_mins</td><td>      18.71</td></tr>
</tbody>
</table>



##### How do the metrics above compare by bike type and membership type?


```R
# by membership type
bike_shares %>%
    reframe(Average_Hourly_demand = round(mean(num_rides),2), 
            Average_Distance_km = round(mean(distance_km/num_rides),2),
            Average_Duration_mins = round(mean(duration_mins),2), 
            .by=member_casual) %>%
    pivot_longer(cols = -member_casual) %>%
    pivot_wider(id_cols = name, names_from=member_casual, values_from=value)
```


<table class="dataframe">
<caption>A tibble: 3 × 3</caption>
<thead>
	<tr><th scope=col>name</th><th scope=col>casual</th><th scope=col>member</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>Average_Hourly_demand</td><td>84.18</td><td>150.76</td></tr>
	<tr><td>Average_Distance_km  </td><td> 1.04</td><td>  0.96</td></tr>
	<tr><td>Average_Duration_mins</td><td>23.81</td><td> 13.67</td></tr>
</tbody>
</table>




```R
# by bike type
bike_shares |>
    reframe(Average_Hourly_demand = round(mean(num_rides),2), 
            Average_Distance_km = round(mean(distance_km/num_rides),2),
            Average_Duration_mins = round(mean(duration_mins),2), 
            .by=rideable_type) |>
    pivot_longer(cols = -rideable_type) |>
    pivot_wider(id_cols = name, names_from=rideable_type, values_from=value)

```


<table class="dataframe">
<caption>A tibble: 3 × 3</caption>
<thead>
	<tr><th scope=col>name</th><th scope=col>classic</th><th scope=col>electric</th></tr>
	<tr><th scope=col>&lt;chr&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>Average_Hourly_demand</td><td>161.84</td><td>73.42</td></tr>
	<tr><td>Average_Distance_km  </td><td>  0.87</td><td> 1.12</td></tr>
	<tr><td>Average_Duration_mins</td><td> 23.37</td><td>14.06</td></tr>
</tbody>
</table>



##### What is the percentage of rides by membership type and bike type?


```R
# function that aggregates a numerical variable based on a given group
aggregate_data <- function(data, column, groups, return_perc=T, func=sum){
    select_cols = c(column, groups)
    
    df <- data[,select_cols] %>%
    group_by(across(all_of(groups))) %>%
    summarize(total = func(.data[[column]])) %>%
    mutate(perc = total/sum(total))
    if (return_perc){
        return(df)
    } else {
        return(df %>% select(-perc))
    }
}
```

-   Bike Type


```R
fig.size(10,7)
aggregate_data(bike_shares, 'num_rides', 'rideable_type') |>
    ggplot(aes(x=rideable_type, y=perc)) +
    geom_col(fill='steelblue', alpha=0.8) +
    geom_text(aes(label=paste(round(total/1e6,2),'M')), vjust=2, 
              fontface='bold', color='white', size=5) +
    theme_bw() +
    theme(legend.position='none',
          plot.title=element_text(face='bold'),
          text = element_text(size=16.5)) + 
    labs(title='Percentage of rides by bike type', x='Bike Type', y='Percentage\n') +
    scale_y_continuous(labels=scales::label_percent(suffix='%'), breaks=seq(0,1,.1)) +
    scale_x_discrete(labels=c('Classic', 'Electric'))
```


    
![png](output_36_0.png)
    


-   Membership Type


```R
fig.size(10,7)
aggregate_data(bike_shares, 'num_rides', 'member_casual') |>
    ggplot(aes(x=member_casual, y=perc)) +
    geom_col(fill='steelblue', alpha=0.8) +
    geom_text(aes(label=paste(round(total/1e6,2),'M')), vjust=2, 
              fontface='bold', color='white', size=5) +
    theme_bw() +
    theme(legend.position='none',
          plot.title=element_text(face='bold'),
          text = element_text(size=16.5)) + 
    labs(title='Percentage of rides by Membership status', 
         x='Membership type', y='Percentage') +
    scale_y_continuous(labels=scales::label_percent(suffix='%'), breaks=seq(0,1,.1)) +
    scale_x_discrete(labels=c('Casual', 'Member'))
```


    
![png](output_38_0.png)
    


-   Membership type vs Bike Type


```R
aggregate_data(bike_shares, 'num_rides', c('member_casual', 'rideable_type')) %>%
    inner_join(
        aggregate_data(bike_shares, 'num_rides', c('rideable_type', 'member_casual')), 
        by=c('rideable_type', 'member_casual', 'total'), 
        suffix=c('_member_vs_bike_type', '_bike_vs_member_type')) %>%
    mutate(across(contains('perc'), \(x) 100*x)) %>%
    ungroup()
```

    [1m[22m`summarise()` has grouped output by 'member_casual'. You can override using the
    `.groups` argument.
    [1m[22m`summarise()` has grouped output by 'rideable_type'. You can override using the
    `.groups` argument.
    


<table class="dataframe">
<caption>A tibble: 4 × 5</caption>
<thead>
	<tr><th scope=col>member_casual</th><th scope=col>rideable_type</th><th scope=col>total</th><th scope=col>perc_member_vs_bike_type</th><th scope=col>perc_bike_vs_member_type</th></tr>
	<tr><th scope=col>&lt;fct&gt;</th><th scope=col>&lt;fct&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th><th scope=col>&lt;dbl&gt;</th></tr>
</thead>
<tbody>
	<tr><td>casual</td><td>classic </td><td>2482521</td><td>68.44137</td><td>35.41030</td></tr>
	<tr><td>casual</td><td>electric</td><td>1144702</td><td>31.55863</td><td>36.00073</td></tr>
	<tr><td>member</td><td>classic </td><td>4528211</td><td>68.99425</td><td>64.58970</td></tr>
	<tr><td>member</td><td>electric</td><td>2034961</td><td>31.00575</td><td>63.99927</td></tr>
</tbody>
</table>



From the results above, we see that classic bikes are the most rented bike types than electric bikes while most of the rents came from registered users than unregistered users. Out of the over 10 million rides between January 2022 and June 2024, about 69% of them were rides from classic bikes while 31% of them were rides from an electric bike. On the other hand, 64% of all the rides were made by registered users while about 36% by casual users.

Drilling down, 35.4% of all rides from a classic bike and 36% from an electric bike were made by non-members. This means that about 64.6% and 64% of all the rides from a classic or electric bike were made by registered members of Capital Bikeshare. Similarly, out of all the unregistered users, 68.4% of them rented classic bikes against the about 69% of registered users, indicating that 31.6% and 31% of unregistered and registered users rented electric bikes, respectively.

##### What is the acceptance rate of bike sharing system Washington DC residents?

To determine the acceptance rate of bike sharing system, we will look at the percentage change of demand per day, week, month and year. This is enable us determine the growth rate at these timeframes


```R
# adding time features
bike_shares <- bike_shares %>%
mutate(year=year(pickup_hour),
       month = month(pickup_hour),
       hour = hour(pickup_hour),
       week = week(pickup_hour),
       dow_num = wday(pickup_hour), # sun
       dow = wday(pickup_hour, label = T, abbr=T), # Sun
       day = day(pickup_hour))
```


```R
# acceptance of bike rides
pct_change <- c()
for (i in c('hour', 'week', 'month', 'day')){
    res <- aggregate_data(bike_shares %>% mutate(date=floor_date(pickup_hour, i[1])), 
                          'num_rides', 'date') %>%
    mutate(pct = 100*(total-lag(total))/lag(total)) %>%
    reframe(avg_change = mean(pct, na.rm=T)) %>%
    pull(avg_change)
  pct_change <- append(pct_change, res)
}

names(pct_change) <- c('hour', 'week', 'month', 'day')
```


```R
# visualise
fig.size(12,8)
data.frame(pct_change) |> 
  rownames_to_column('name') |> 
  ggplot(aes(name, pct_change)) +
  geom_col(fill='cornflowerblue', alpha=0.8) +
  geom_text(aes(label=paste(round(pct_change,2),'%')), vjust=1.5, 
            color='white', fontface='bold', size=5) + 
  theme_bw() +
  theme(panel.grid=element_blank(), 
        text = element_text(size=16.5),
        axis.text.y = element_blank(),
        axis.ticks.y=element_blank(),
        plot.title=element_text(face='bold')) + 
  labs(title='Bike Acceptance Rate by Residents', 
       x='Timeframe', y='Percentage Change\n')
```


    
![png](output_45_0.png)
    


-   There's a positive acceptance of bike sharing by residents of Washington DC. By investigating the percentage change in bike demand at different time frames, we see that per hour of the day, the demand rate for bike sharing increases by about 18.7% on average, about 5.7% per day, 6.3% per week and about 8.1% per month of the year.

Next, we want to look at the rate at which residents demand each bike type per hour, day, week and month. This will be extended to the change in demand for bike rides by non-members and members and the demand for each bike type by non-members and members. With this, we want to understand at what time these groups have a higher demand for city bikes.


```R
# acceptance by bike type
results <- data.frame(row.names=c('hour', 'week', 'month', 'day'),
                      classic=numeric(4), ebikes=numeric(4))

for (i in 1:2){
    bike_type <- c('classic', 'electric')[i]

    pct_change <- c()
    for (j in rownames(results)) {
        res <- aggregate_data(data = bike_shares %>% 
                                     filter(rideable_type == bike_type) %>% 
                                     mutate(date=floor_date(pickup_hour, j[1])), 
        column = 'num_rides', groups = 'date') %>%
        mutate(pct = 100*(total-lag(total))/lag(total)) %>%
        reframe(avg_change = mean(pct, na.rm=T)) %>%
        pull(avg_change)
        pct_change <- append(pct_change, res)
    }
    results[i] <- pct_change
}
```


```R
# visualise
fig.size(12,8)
results |> 
    rownames_to_column('name') |> 
    pivot_longer(-name, names_to='bike_type', values_to='pct_change') |>
    ggplot(aes(name, pct_change, fill=bike_type)) +
    geom_col(alpha=0.8, position=position_stack(vjust=0.7)) +
    geom_text(aes(label=paste(round(pct_change,2),'%')), vjust=1.5, size=5,
              color='white', fontface='bold', position=position_stack(vjust=0.7)) + 
    theme_bw() +
    theme(panel.grid=element_blank(), 
          axis.text.y = element_blank(),
          axis.ticks.y=element_blank(),
          text = element_text(size=16.5),
          legend.position = 'inside',
          legend.position.inside = c(0.93,.9),
          plot.title=element_text(face='bold')) + 
    labs(title='Bike Type Acceptance Rate by Residents', 
         x='Timeframe', y='Percentage Change\n', fill='Bike Type') +
    scale_fill_manual(values=c('coral', 'cornflowerblue'), labels=c('Classic', 'Electric'))
```


    
![png](output_48_0.png)
    


-   When we look at bike demands by bike type, we see that the classic bike type is demanded more than electric bikes per hour and per day. The percentage change in demand per is slightly the same but per month, the demand for electric bikes is higher than for classic bikes. This could indicate that there are some parts of the month when the demand for electric bikes is higher than for classic bikes.


```R
# acceptance by membership status
results <- data.frame(row.names=c('hour', 'week', 'month', 'day'),
                      casual=numeric(4), members=numeric(4))

for (i in 1:2){
    member_type <- c('casual', 'member')[i]

    pct_change <- c()
    for (j in rownames(results)){
        res <- aggregate_data(bike_shares %>% 
                              filter(member_casual == member_type) %>%
                              mutate(date=floor_date(pickup_hour, j[1])), 
                              'num_rides', 'date') %>%
        mutate(pct = 100*(total-lag(total))/lag(total)) %>%
        reframe(avg_change = mean(pct, na.rm=T)) %>%
        pull(avg_change)
        pct_change <- append(pct_change, res)
    }
    results[i] = pct_change
}
```


```R
# visualise
fig.size(12,8)
results |> 
    rownames_to_column('name') |> 
    pivot_longer(-name, names_to='member_type', values_to='pct_change') |>
    ggplot(aes(name, pct_change, fill=member_type)) +
    geom_col(alpha=0.8, position=position_stack(vjust=0.7)) +
    geom_text(aes(label=paste(round(pct_change,2),'%')), vjust=1.5, size=5,
              color='white', fontface='bold', position=position_stack(vjust=0.7)) + 
    theme_bw() +
    theme(panel.grid=element_blank(), 
          axis.text.y = element_blank(),
          text = element_text(size=16.5),
          axis.ticks.y=element_blank(),
          legend.position = 'inside',
          legend.position.inside = c(0.91,.9),
          plot.title=element_text(face='bold')) + 
    labs(title='Acceptance Rate by non-members and members', 
         x='Timeframe', y='Percentage Change\n', fill='Membership Type') +
    scale_fill_manual(values=c('coral', 'cornflowerblue'), labels=c('Casual', 'Member'))

```


    
![png](output_51_0.png)
    


- There's an equal hourly demand rate for casual and registered users
- This is rather different per day where there's a 10.4% increase in bike demand by casual members against the 4.8% by members. This could indicate that there are some parts of the week when bikes are used by casual members
- This is also the same per month and per week of the month, there's a relatively equal demand.


```R
# acceptance by bike type by membership status
results <- data.frame()

for (i in 1:2){
    member_type <- c('casual', 'member')[i]

    pct_change <- data.frame()
    for (j in c('hour', 'week', 'month', 'day')){
        res <- aggregate_data(bike_shares %>% 
                              filter(member_casual == member_type) %>%
                              mutate(date=floor_date(pickup_hour, j[1])), 
        column='num_rides', groups=c('date', 'rideable_type')) %>%
        pivot_wider(id_cols = date, names_from=rideable_type, values_from=total) %>% 
        ungroup() %>%
        mutate(across(where(is.numeric), function(x) 100*(x-lag(x))/lag(x))) %>%
        reframe(across(where(is.numeric), \(x) mean(x, na.rm=T))) %>% unlist()
        pct_change <- rbind(pct_change, c(j, member_type, res))
        names(pct_change) <- c('name', 'member_type', 'classic', 'electric')
        pct_change[, c(3,4)] <- sapply(pct_change[, c(3,4)], as.numeric)
    }
    results <- rbind(results, pct_change)
}
```

    [1m[22m`summarise()` has grouped output by 'date'. You can override using the
    `.groups` argument.
    [1m[22m`summarise()` has grouped output by 'date'. You can override using the
    `.groups` argument.
    [1m[22m`summarise()` has grouped output by 'date'. You can override using the
    `.groups` argument.
    [1m[22m`summarise()` has grouped output by 'date'. You can override using the
    `.groups` argument.
    [1m[22m`summarise()` has grouped output by 'date'. You can override using the
    `.groups` argument.
    [1m[22m`summarise()` has grouped output by 'date'. You can override using the
    `.groups` argument.
    [1m[22m`summarise()` has grouped output by 'date'. You can override using the
    `.groups` argument.
    [1m[22m`summarise()` has grouped output by 'date'. You can override using the
    `.groups` argument.
    


```R
fig.size(12,8)
results |> 
    as.data.frame() |>
    pivot_longer(cols=where(is.numeric), names_to = 'bike_type', values_to='pct_change') |>
    ggplot(aes(name, pct_change, fill=member_type)) +
    geom_col(alpha=0.8, position=position_stack(vjust=0.9), width=0.9) +
    facet_wrap(~bike_type, ncol=2, 
               labeller = as_labeller(c(`electric`='Electric', `classic`='Classic'))) +
    geom_text(aes(label=paste0(round(pct_change,2),'%')), vjust=1., size=5,
              color='white', fontface='bold', position=position_stack(vjust=0.9)) + 
    theme_bw() +
    theme(panel.grid=element_blank(), 
          text = element_text(size=16.5),
          strip.background=element_rect(fill='gray'),
          strip.text = element_text(face='bold'),
          axis.text.y = element_blank(),
          legend.position = 'inside',
          legend.position.inside = c(0.91,.9),
          axis.ticks.y=element_blank(),
          plot.title=element_text(face='bold')) + 
    labs(title='Acceptance Rate by non-members and members', 
         x='Timeframe', y='Percentage Change', fill='Membership Type') +
    scale_fill_manual(values=c('coral', 'cornflowerblue'), labels=c('Casual', 'Member'))
```


    
![png](output_54_0.png)
    


- Generally, classic bikes are demanded by both members and non-members alike than for electric bikes
- On average, there's a 27-29% change in hourly demand by members and non-members for the classic bikes against the 20% for electric bikes.
- Although members use more bikes than non-members, their daily demand for classic bikes is relatively stable at about 5.5% per day against about 14% by non-members. On the other hand, the demand for electric bikes for each membership group is relatively stable, between 3-6% on average.
- A similar demand is seen per month, where casual members are likely to have a 13% increase in classic bikes. This is twice more than that demanded by members.
- On a weekly basis, both classic and electric bikes are demanded almost equally by registered and casual members.

__Comparison of percentage change in demand by weather seasons, month and yearly__

__Seasonal variation__


```R
season <- function(x){
  if (x > 12) stop('x is not a valid number')
  if (x %in% c(12,1,2)) 'Winter'
  else if (x %in% 3:5) 'Spring'
  else if (x %in% 6:8)'Summer'
  else 'Autumn'
}
```


```R
monthly_rides <- aggregate_data(bike_shares %>% 
mutate(date=floor_date(pickup_hour, 'm')), 
column = 'num_rides', groups = 'date', return_perc = F, func=sum) %>%
mutate(season= sapply(month(date),season), 
       month=month(date), year=factor(year(date)))
```


```R
fig.size(12,8)
monthly_rides %>%
select(year, season, total) %>%
reframe(total=sum(total),.by = c(season, year)) %>%
pivot_wider(id_cols = year, names_from = season, values_from = total) %>%
mutate(across(where(is.numeric), function(x) 100*(x-lag(x))/lag(x))) %>%
pivot_longer(-year, names_to = 'season', values_to = 'pct_change') %>% 
mutate(up=ifelse(pct_change > 0, 'up', 
ifelse(pct_change < 0, 'down', 'no'))) %>%
mutate(up = factor(up, levels=c('up', 'down', 'no'))) %>%
drop_na() %>%
ggplot(aes(year, pct_change, fill=up)) +
geom_col(width=0.7) + 
geom_text(aes(label=paste0(round(pct_change,2),'%')), size=5, vjust=0.2,
          check_overlap = T, color='#222225', fontface='bold', 
          position=position_dodge2(width=0.3)) +
geom_hline(yintercept = 0, linetype='dashed') +
facet_wrap(~season) +
theme_bw() +
theme(panel.grid=element_blank(), 
      text = element_text(size=16.5),
      strip.background=element_rect(fill='#272525'),
      strip.text = element_text(face='bold', color='white'),
      axis.text.y = element_blank(),
      legend.position = 'none',
      axis.ticks.y=element_blank(),
      plot.title=element_text(face='bold')) + 
labs(title='Seasonal growth in bike patronage', 
        x='Year', y='Percentage Change\n') +
scale_fill_manual(values=c('#5e9e5e', '#e09479'))

```


    
![png](output_60_0.png)
    


By comparing the total seasonal bike patronage year over year, we can deduce the following
- There's an increase in patronage between 2022 to 2023 for all seasons
- There was a 39.2% increase in patronage in 2023 during autumn, ~29% in 2023 and a further 6% increase (35.5%) in 2024 during the spring season, 23.2% in Summer and 58.9% in winter. The high increase could be because of favourable weather conditions in 2023 than in 2022.
- The decrease in patronage in 2024 in Summer and Winter seasons is because as at the time of analysis, complete data for Summer and Winter seasons weren't available.

__Monthly variation__


```R
fig.size(16,9)
monthly_rides %>%
select(year, month, total) %>%
pivot_wider(id_cols = year, names_from = month, values_from = total) %>%
mutate(across(where(is.numeric), function(x) 100*(x-lag(x))/lag(x))) %>%
pivot_longer(-year, names_to = 'month', values_to = 'pct_change') %>% 
mutate(up=ifelse(pct_change > 0, 'up',
          ifelse(pct_change < 0, 'down', 'no')),
       date = as_date(str_c(year, month, '01', sep='-'))) %>%
mutate(month_name = month(date, label = T, abbr = F),
       up = factor(up, levels=c('up', 'down', 'no'))) %>%
drop_na() %>%
ggplot(aes(year, pct_change, fill=up)) +
geom_col(width=0.7) + 
geom_text(aes(label=paste0(round(pct_change,2),'%')), size=5, vjust=1.1, 
          check_overlap = T, color='#222225', fontface='bold', 
          position=position_dodge2(width=0.3)) +
geom_hline(yintercept = 0, linetype='dashed') + 
facet_wrap(~month_name, ncol = 6) +
theme_bw() +
theme(panel.grid=element_blank(), 
      text = element_text(size=16.5),
      strip.background=element_rect(fill='#212125'),
      strip.text = element_text(face='bold', color='white'),
      axis.text.y = element_blank(),
      legend.position = 'none',
      axis.ticks.y=element_blank(),
      plot.title=element_text(face='bold')) + 
labs(title='Monthly growth in bike patronage', 
        x='Year', y='Percentage Change\n') +
scale_fill_manual(values=c('#5e9e5e', '#e09479'))

```


    
![png](output_63_0.png)
    


By comparing the monthly patronage year over year, we see that there's an increased usage of bike rides by Washington DC residents in all the months of the year.
- A whooping 85% increase was recorded between Jan 2023 and Jan 2024, and in the year 2024, the fold increase was reduced compared to the previous year amounting to a 21% increase in Jan 2024.
- There was further increased patronage in Feb-Mar and June 2024 compared to bike patronage in previous years.

__Yearly variation__


```R
fig.size(12,8)
monthly_rides %>%
select(year, total) %>%
reframe(total=sum(total),.by = year) %>%
mutate(pct_change = 100*(total-lag(total))/lag(total)) %>%
mutate(up=ifelse(pct_change > 0, 'up', 
ifelse(pct_change < 0, 'down', 'no'))) %>%
mutate(up = factor(up, levels=c('up', 'down', 'no'))) %>%
drop_na() %>%
ggplot(aes(year, pct_change, fill=up)) +
geom_col(width=0.7) + 
geom_text(aes(label=paste0(round(pct_change,2),'%')), size=5, vjust=1.1, 
          check_overlap = T, color='#222225', fontface='bold', 
          position=position_dodge2(width=0.3)) +
geom_hline(yintercept = 0, linetype='dashed') +
theme_bw() +
theme(panel.grid=element_blank(), 
      text = element_text(size=16.5),
      axis.text.y = element_blank(),
      legend.position = 'none',
      axis.ticks.y=element_blank(),
      plot.title=element_text(face='bold')) + 
labs(title='Monthly growth in bike patronage', 
        x='Year', y='Percentage Change\n', fill='Membership Type') +
scale_fill_manual(values=c('#5e9e5e', '#e09479'))
```


    
![png](output_66_0.png)
    


- By year over year patronage, an about 34% increase in patronage and acceptance was recorded between 2022 and 2023. Currently, the patronage is about 41% lower than what was recorded last year (probably, it could turn green since it is still 2024 as at the time of the analysis). 

__Hourly Variation__


```R
fig.size(16,9)
aggregate_data(bike_shares, column = 'num_rides', 
groups = c('hour', 'year'), return_perc = F, func=mean) %>%
pivot_wider(id_cols = year, names_from = hour, values_from = total) %>%
mutate(year=factor(year),
      across(where(is.numeric), function(x) 100*(x-lag(x))/lag(x))) %>%
pivot_longer(-year, names_to = 'hour', 
             names_transform = list(hour=as.integer),
             values_to = 'pct_change') %>%
mutate(up=ifelse(pct_change > 0, 'up', 
          ifelse(pct_change < 0, 'down', 'no'))) %>%
mutate(up = factor(up, levels=c('up', 'down', 'no')),
       year_hour = str_pad(str_c(hour, year,sep = '-'), 
                   width = 7, pad='0',side = 'left')) %>%
drop_na() %>%
mutate(id= factor(ifelse(hour < 12, 'EM-Noon', 'Noon-MN'))) %>%
ggplot(aes(year, pct_change, fill=up)) +
geom_col(width=0.7) + 
geom_text(aes(label=paste0(round(pct_change,2),'%')), size=4.5, vjust=1.2, 
          check_overlap = T, color='#222225', fontface='bold', 
          position=position_dodge2(width=0.3)) +
geom_hline(yintercept = 0, linetype='dashed') +
facet_wrap(~hour,nrow = 4, labeller='label_both') +
theme_bw() +
theme(panel.grid=element_blank(), 
      text = element_text(size=16.5),
      axis.text.y = element_blank(),
      strip.background=element_rect(fill='#212124'),
      strip.text = element_text(face='bold', color='white'),
      legend.position = 'none',
      axis.ticks.y=element_blank(),
      plot.title=element_text(face='bold')) + 
labs(title='Average Hourly growth in bike patronage', 
        x='Year', y='Percentage Change\n') +
scale_fill_manual(values=c('#5e9e5e', '#e09479'))
```

    [1m[22m`summarise()` has grouped output by 'hour'. You can override using the
    `.groups` argument.
    


    
![png](output_69_1.png)
    


To compare the hourly percentage change in bike patronage, the hourly bike rides for each year was averaged and used to compare with the average hourly bike rides in other years.

As we saw in seasonal, monthly and yearly variations, there's a positive patronage in the average hourly patronage per year.

All the results above indicate that residents have inculcated bike-sharing into their daily activities.

#### What is the temporal variation of bike rides at each time of the year

To do this, we want to look at the number of bikes at each time of the year. Firstly, we will look at the average hourly bike demand over time from Jan 2020 to June 2024. We will aggregate this using a 28-Day window


```R
moving_average <- function(df, n, date_id){
    date <- df[, date_id]
    cols <- names(df)
    n_col = length(cols)
    other_cols <- cols[!grepl(cols[date_id], cols)]
    
    # convert to moving average
    res <- zoo::rollmean(df[,-date_id], n) %>% as.data.frame()
    g <- bind_cols(date[n:nrow(df),], res)
    names(g)[2:n_col] <- other_cols
    g %>% mutate(date = as_date(date))
}
```


```R
hourly <- aggregate_data(bike_shares %>% mutate(date=floor_date(pickup_hour, 'd')), 
               column='num_rides', group='date', return_perc=F, func=mean) %>% 
    moving_average(28, 1) |>
    ggplot(aes(date, total)) +
    geom_line(color='steelblue', linewidth=0.8) +
    geom_smooth(formula = 'y~x',se = F,method = 'lm', 
                linetype='dashed', linewidth=0.1,color='black')+
    theme_tufte() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          axis.title.x=element_blank(),
          axis.ticks.x=element_blank(),
          axis.text.x=element_blank(),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    labs(y='Number of Bikes', x='') +
    scale_x_date(date_breaks='2 month', date_labels='%b\n%Y', 
                 limits=c(as.Date('2022-01-01'), NA)) +
    scale_y_continuous(breaks=seq(0,200,50))

daily <- aggregate_data(bike_shares %>% mutate(date=floor_date(pickup_hour, 'd')), 
               column='num_rides', groups='date', return_perc=F, func=sum) %>%
    moving_average(28, 1) |>
    ggplot(aes(date, total)) +
    geom_line(color='red', alpha=0.6, linewidth=0.8) +
    geom_smooth(formula = 'y~x',se = F,method = 'lm', 
                linetype='dashed', linewidth=0.1, color='black') +
    theme_tufte() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          axis.text.x=element_text(size=13),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    labs( y='Number of Bikes', x='') +
    scale_x_date(date_breaks='2 month', date_labels='%b\n%Y', 
                 limits=c(as.Date('2022-01-01'), NA)) +
    scale_y_continuous(breaks=seq(0,20000,5000))
```


```R
fig.size(12,8)
ggarrange(hourly, daily, nrow = 2,
          labels=c('Hourly Bike Demand (28-Day Moving Average)', 
                   'Daily Bike Demand (28-Day Moving Average)'))
```


    
![png](output_74_0.png)
    


- We see a linear growth in the number of bike rides in Washington DC (dashed line)
- There is a seasonal effect of bike demand.
- Demand peak in the Summer seasons and declines in the winter season (towards the end of the year).

##### Hourly demand


```R
# hourly demand
a <- aggregate_data(bike_shares, column='num_rides', group=c('hour'), return_perc=F, func=mean) %>% 
    ggline(x='hour', y='total', title = 'Average Hourly Demand', 
           plot_type = 'l' , color='darkgreen', line_type='-', size=.8) +
    theme_tufte() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          axis.text.x=element_blank(),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    labs(x='', y='') +
    scale_y_continuous(breaks=seq(0,300,50)) +
    scale_x_continuous(breaks=seq(0,23,3))
```


```R
b <- # hourly demand
aggregate_data(bike_shares, column='num_rides', group=c('hour', 'year'), return_perc=F, func=mean) %>% 
    mutate(year=factor(year)) %>%
    ggline(x='hour', y='total', color = 'year', plot_type = 'l', size=0.8) +
    theme_tufte() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          axis.text.x=element_text(size=13),
          axis.text.y=element_text(size=13),
          legend.position='top',
          plot.title=element_text(face='bold', size=16)) +
    labs(title='Hourly demand per year', x='Hour of day', y='') +
    scale_y_continuous(breaks=seq(0,400,50)) +
    scale_x_continuous(breaks=seq(0,23,3))
```

    [1m[22m`summarise()` has grouped output by 'hour'. You can override using the
    `.groups` argument.
    


```R
fig.size(12,8)
ggarrange(a,b, ncol=1)
```


    
![png](output_79_0.png)
    



```R
# weekday demand
a <- aggregate_data(bike_shares, column='num_rides', group=c('dow'), return_perc=F, func=mean) %>% 
    ggbarplot(x='dow', y='total', title = 'Average Demand per weekday', 
              fill='cornflowerblue', alpha=0.9) +
    theme_bw() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          axis.text.x=element_text(size=13),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    scale_y_continuous(breaks=seq(0,120,20)) + 
    labs(x='Day of week', y='Bike rides') 
```


```R
# hourly demand
# average monthly demand
b <- aggregate_data(bike_shares %>% 
               mutate(month_name = month(pickup_hour, label = T, abbr = T)), column='num_rides', 
               group=c('month_name'), 
               return_perc=F, func=mean) %>%
    ggbarplot(x='month_name', y='total', plot_type = 'l',
           size = .8, fill='steelblue', alpha=0.7) +
    theme_bw() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          strip.text=element_text(face='bold'),
          axis.text.x=element_text(size=13),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    scale_y_continuous(breaks=seq(0,200,20)) + 
    labs(x='Hour', y='', title='Average Monthly Demand') 
```


```R
fig.size(14,7)
ggarrange(a, b)
```


    
![png](output_82_0.png)
    


- Bike rentage mainly depends on the hour of the day and the month of the year
- Many People demand bikes during the rush hours (8AM and 6PM) of the day and mostly during spring and summer seasons (Apr-Aug).
- An almost equal amount of bike is rented by resident in all days of the week (at least 100 on average).

#### When are electric and classic bikes mostly rented? 


```R
fig.size(14,7)
aggregate_data(bike_shares, column='num_rides', 
               group=c('hour', 'member_casual', 'rideable_type'), 
               return_perc=F, func=mean) %>%
    ggline(x='hour', y='total', plot_type = 'l', facet.by = 'rideable_type',
           size = .8, color='member_casual', alpha=0.7) +
    theme_bw() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          strip.text=element_text(face='bold'),
          axis.text.x=element_text(size=13),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    scale_y_continuous(breaks=seq(0,500,100)) + 
    labs(x='Hour', y='Bike rides\n', title='Average Hourly Demand') +
    guides(color=guide_legend(title = 'Membership', position='top')) +
    scale_color_manual(values=c('coral', 'cornflowerblue'))
```

    [1m[22m`summarise()` has grouped output by 'hour', 'member_casual'. You can override
    using the `.groups` argument.
    


    
![png](output_85_1.png)
    



```R
fig.size(14,7)
aggregate_data(bike_shares, column='num_rides', 
               group=c('month', 'member_casual', 'rideable_type'), 
               return_perc=F, func=mean) %>%
    ggline(x='month', y='total', plot_type = 'l', facet.by = 'rideable_type',
           size = .8, color='member_casual', alpha=0.7) +
    theme_bw() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          strip.text=element_text(face='bold'),
          axis.text.x=element_text(size=13),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    scale_y_continuous(breaks=seq(0,500,50)) + 
    labs(x='Month', y='Bike Rides\n', title='Average Monthly Demand') +
    guides(color=guide_legend(title = 'Membership', position='top')) +
    scale_color_manual(values=c('coral', 'cornflowerblue'))
```

    [1m[22m`summarise()` has grouped output by 'month', 'member_casual'. You can override
    using the `.groups` argument.
    


    
![png](output_86_1.png)
    



```R
fig.size(14,7)
aggregate_data(bike_shares, column='num_rides', 
               group=c('dow', 'member_casual', 'rideable_type'), 
               return_perc=F, func=mean) %>%
    ggline(x='dow', y='total', plot_type = 'l', facet.by = 'rideable_type',
           size = .8, color='member_casual', alpha=0.7) +
    theme_bw() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          strip.text=element_text(face='bold'),
          axis.text.x=element_text(size=13),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    scale_y_continuous(breaks=seq(0,250,40)) + 
    labs(x='Weekday', y='Bike rides\n', title='Average Weekly Demand') +
    guides(color=guide_legend(title = 'Membership', position='top')) +
    scale_color_manual(values=c('coral', 'cornflowerblue'))
```

    [1m[22m`summarise()` has grouped output by 'dow', 'member_casual'. You can override
    using the `.groups` argument.
    


    
![png](output_87_1.png)
    


- The hourly demand for classic and electric bikes by a member or non-member depends on the hour of the day. However, the amount is greater for classic bikes than for electric bikes
- The monthly demand for either bikes by any membership type is affected by the month of the year. For classic bikes, the demand increases from the beginning of the year, peaks at the middle of the year and then declines toward the end of the year. For electric bikes, the decline starts early (July).
- On the other hand, the weekday demands for both casual and registered members are completely different and opposite. There are more bike demands/usage from casual users toward the end of the week while for registered users, it peaks toward the middle of the week and declines toward the end of the week. This may indicate that most casual users are users who use city bikes for weekend activities while registered members could be users who use the city bikes for day-to-day activities like commuting to work, school or any office-related activity.

#### Do members and non-members use classic or electric bikes for long or short distances? 


```R
fig.size(14,7)

aggregate_data(bike_shares %>% 
               mutate(av_dist = distance_km/num_rides), 
               column='duration_mins', group=c('hour', 'rideable_type', 'member_casual'), 
               return_perc=F, func=mean) %>% 
    ggline(x='hour', y='total', title = 'Average Hourly Demand', facet.by = 'rideable_type',
           plot_type = 'l' , color='member_casual', line_type='-', size=.8) +
    theme_bw() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          strip.text=element_text(face='bold'),
          axis.text.x=element_text(size=13),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    # scale_y_continuous(breaks=seq(0,200,20)) + 
    labs(x='Hour', title='Average Hourly Duration of bike rides', y='Duration (in mins)\n') +
    guides(color=guide_legend(title = 'Membership', position = 'top')) +
    scale_color_manual(values=c('coral', 'cornflowerblue'))
```

    [1m[22m`summarise()` has grouped output by 'hour', 'rideable_type'. You can override
    using the `.groups` argument.
    


    
![png](output_90_1.png)
    



```R
fig.size(14,7)
aggregate_data(bike_shares %>% 
               mutate(av_dist = distance_km/num_rides), 
               column='av_dist', group=c('hour', 'rideable_type', 'member_casual'), 
               return_perc=F, func=mean) %>% 
    ggline(x='hour', y='total', title = 'Average Hourly Demand', facet.by = 'rideable_type',
           plot_type = 'l' , color='member_casual', line_type='-', size=.8) +
    theme_bw() +
    theme(text=element_text(size=16.5), 
          panel.grid=element_blank(),
          strip.text=element_text(face='bold'),
          axis.text.x=element_text(size=13),
          axis.text.y=element_text(size=13),
          plot.title=element_text(face='bold', size=16)) +
    # scale_y_continuous(breaks=seq(0,200,20)) + 
    labs(x='Hour', title='Average Hourly Distance of bike rides', y='Distance (in km)\n') +
    guides(color=guide_legend(title = 'Membership', position = 'top')) +
    scale_color_manual(values=c('coral', 'cornflowerblue'))
```

    [1m[22m`summarise()` has grouped output by 'hour', 'rideable_type'. You can override
    using the `.groups` argument.
    


    
![png](output_91_1.png)
    

