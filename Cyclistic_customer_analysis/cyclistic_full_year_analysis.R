### Cyclistic_Exercise_Full_Year_Analysis ###

# Install required packages
Sys.setlocale("LC_TIME", "English")
library(tidyverse)
library(ggplot2)
library(lubridate)

#change the directory to the folder holding data (12 csv files each for a month)
getwd()
setwd("D:/resume_portfolio/cyclistic_google_case1/divvy_tripdata")  

#check data of August 2021.
m8_2021 <-read_csv('202108-divvy-tripdata.csv')  #Rows: 804352 Columns: 13
colnames(m8_2021)

# list columns name and datatype for comparing with other months data.
#[1] "ride_id"  character "rideable_type" character   "started_at" datetime  "ended_at"  datetime        
#[5] "start_station_name" char "start_station_id" char  "end_station_name" char  "end_station_id"  char   
#[9] "start_lat"  double  "start_lng" double "end_lat" double "end_lng" double      
#[13] "member_casual" character
str(m8_2021)

# Check July 2021 data
m7_2021 <-read_csv('202107-divvy-tripdata.csv')
colnames(m7_2021)  #same columns name and datatype with August data
str(m7_2021)

# Check June 2021 data
m6_2021 <-read_csv('202106-divvy-tripdata.csv')
colnames(m6_2021)  #same columns name and datatype with August data
str(m6_2021)
# Check May 2021 data
m5_2021 <-read_csv('202105-divvy-tripdata.csv')
colnames(m5_2021)  #same columns name and datatype with August data
str(m5_2021)
# Check April 2021 data
m4_2021 <-read_csv('202104-divvy-tripdata.csv')
colnames(m4_2021)  #same columns name and datatype with August data
str(m4_2021)

# Check March 2021 data
m3_2021 <-read_csv('202103-divvy-tripdata.csv')
colnames(m3_2021)  #same columns name and datatype with August data
str(m3_2021)

# Check February 2021 data
m2_2021 <-read_csv('202102-divvy-tripdata.csv')
str(m2_2021)  #same columns name and datatype with August data

# Check January 2021 data
m1_2021 <-read_csv('202101-divvy-tripdata.csv')   # end_station and id have lots of NA value
str(m1_2021)  #same columns name and datatype with August data

# Check December 2020 data
m12_2020 <-read_csv('202012-divvy-tripdata.csv')   # end_station and id have lots of NA value
str(m12_2020)  #same columns name and datatype with August 2021 data

# Check November 2020 data
m11_2020 <-read_csv('202011-divvy-tripdata.csv')   # end_station and id have lots of NA value
str(m11_2020)  #same columns name with August 2021 data
#start_station_id and end_station_id have different datatype from previous months. unite datatypes
m11_2020 <- transform(m11_2020, start_station_id=as.character(start_station_id), 
                      end_station_id=as.character(end_station_id))
str(m11_2020)

# Check October 2020 data
m10_2020 <-read_csv('202010-divvy-tripdata.csv')   # end_station and id have lots of NA value
str(m10_2020)  #same columns name with August 2021 data

#start_station_id and end_station_id have different datatype from previous months. unite datatypes
m10_2020 <- transform(m10_2020, start_station_id=as.character(start_station_id), end_station_id=as.character(end_station_id))
str(m10_2020)

# Check October 2020 data
m9_2020 <-read_csv('202009-divvy-tripdata.csv')   # end_station and id have lots of NA value
str(m9_2020)  #same columns name with August 2021 data
m9_2020 <- transform(m9_2020, start_station_id=as.character(start_station_id), end_station_id=as.character(end_station_id))
str(m9_2020)

# Stack individual month's data frames into whole year data frame. And delete unnecessary features.
trips_y <- bind_rows(m8_2021, m7_2021, m6_2021, m5_2021, m4_2021, m3_2021, m2_2021, m1_2021, 
                     m12_2020, m11_2020, m10_2020, m9_2020)
trips_y <- trips_y %>%
  select(-c(start_lat,start_lng,end_lat,end_lng))
str(trips_y)

# Inspect new table
colnames(trips_y)  #list of column names
nrow(trips_y) # get rows of the table  4.91M
dim(trips_y)
head(trips_y)
str(trips_y)
summary(trips_y)   #very good for inspecting numeric value and datetime columns

# More detailed information about character columns
length(unique(trips_y$ride_id))  #4912863
unique(trips_y$rideable_type)  #"electric_bike" "classic_bike"  "docked_bike"  
table(trips_y$member_casual)  # casual 2225089  member 2687983. Almost equal distribution.
length(unique(trips_y$start_station_name))  # 758
length(unique(trips_y$start_station_id))  #1294
length(unique(trips_y$end_station_name))  #757
length(unique(trips_y$end_station_id))  #1294

# check missing values for each columns
for (col in names(trips_y)) {
  missing <- sum(is.na(trips_y[,col]))
  if (missing > 0) {
    print(c(col, missing))
          }
}
# "start_station_name" "450045" NA         
# "start_station_id" "450571"  NA         
# "end_station_name" "491380"  NA        
# "end_station_id" "491764" NA

# Increase columns for better presenting data. trip_duration, year, month, day, weekday
trips_y$year <- format(trips_y$started_at,"%Y")
trips_y$month <- format(trips_y$started_at,"%m")
trips_y$day <- format(trips_y$started_at,"%d")
trips_y$day_of_week <- format(trips_y$started_at,"%A")

# get the trip duration for each trip and convert data type to numeric
trips_y$trip_duration <- difftime(trips_y$ended_at, trips_y$started_at)
str(trips_y)
trips_y$trip_duration <- as.numeric(as.character(trips_y$trip_duration))

summary(trips_y)
filter(trips_y, trip_duration < 0) %>% summarize(n = n())  #5400 rows trip_duration < 0.
filter(trips_y, start_station_name == "HQ QR") %>% summarize(n = n())  #0

# delete records which hold invalid value in trip_duration column.
trips_y2 <- trips_y[trips_y$trip_duration >= 0,]
summary(trips_y2)

# Conduct descriptive analysis
summary(trips_y2$trip_duration)

trips_y2$day_of_week <- format(trips_y2$started_at,"%A")
str(trips_y2)
ordered(unique(trips_y2$day_of_week))
trips_y2$day_of_week <- ordered(trips_y2$day_of_week, 
                                levels=c("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"))

#Run the average ride time by each day for members vs casual users.
aggregate(trips_y2$trip_duration~trips_y2$member_casual+trips_y2$day_of_week, FUN=mean)


#analyze ridership data by customer type and weekday
trips_y2 %>%
  mutate(weekday = wday(trips_y2$started_at, label = TRUE)) %>%    #increase a column, get weekday
  group_by(member_casual, weekday) %>%
  summarise(number_of_rides = n(), average_duration = mean(trip_duration)) %>%  #calculates number of rides
  arrange(member_casual,weekday)

#01 Business increase during the last 12 months.
trips_y2$year_month <- format(trips_y2$started_at,"%Y-%m")
colnames(trips_y2)
trips_y2 %>%
  group_by(member_casual, year_month) %>%
  summarise(number_of_rides = n(), average_duration = mean(trip_duration)) %>%
  arrange(member_casual,year_month) %>%
  ggplot(aes(x=year_month, y=number_of_rides, fill=member_casual)) +
  geom_col(position='dodge')

# 02 Visualize the number of rides by rider type
trips_y2 %>%
  mutate(weekday = wday(trips_y2$started_at, label = TRUE)) %>%    #increase a column, get weekday
  group_by(member_casual, weekday) %>%
  summarise(number_of_rides = n(), average_duration = mean(trip_duration)) %>%  #calculates number of rides
  arrange(member_casual,weekday) %>%
  ggplot(aes(x=weekday, y=number_of_rides, fill=member_casual)) +
  geom_col(position='dodge')

# 03 Create a visualization for average duration
trips_y2 %>%
  mutate(weekday = wday(trips_y2$started_at, label = TRUE)) %>%    #increase a column, get weekday
  group_by(member_casual, weekday) %>%
  summarise(number_of_rides = n(), average_duration = mean(trip_duration)) %>%  #calculates number of rides
  arrange(member_casual,weekday) %>%
  ggplot(aes(x=weekday, y=average_duration, fill=member_casual)) +
  geom_col(position='dodge')



# 04 Comparison between number of rides and customer types
trips_y2 %>%
  filter(trip_duration > 3600) %>%
  group_by(member_casual, day_of_week) %>%
  summarise(number_of_rides = n(), average_duration = mean(trip_duration)) %>%
  arrange(member_casual,day_of_week) %>%
  ggplot(aes(x=day_of_week, y=number_of_rides, fill=member_casual)) +
  geom_col(position='dodge')
# Conclusion: almost all of long duration rides are made by casual users.  

# Export summary for future usage.
counts <- aggregate(trips_y2$trip_duration~trips_y2$member_casual+trips_y2$day_of_week, FUN = mean)
setwd('D:/resume_portfolio/cyclistic_google_case1')
write.csv(counts,file='trip.csv')
