# I am importing the necessary modules that I will be working with throughout the project.
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt

# Before starting the import, I will create a list of column names that I need to import.
columns = ['Name', 'Age', 'M/F', 'City', 'Country', 'Half', 'Official Time']

# I am importing CSV files with the results of the 2017 Boston Marathon as a Pandas dataframe.
marathon2017 = pd.read_csv('marathon_results_2017.csv', usecols=columns)

# I will display the first 10 rows of the new "marathon2017" dataframe to check the result, information about the
# columns, and the number of rows/columns.
print(marathon2017.head(10))
print(marathon2017.info())
print(marathon2017.shape)

# I will remove duplicates based on the primary columns. If there are any duplicates, only the records of
# unique marathon participants will remain.
marathon2017 = marathon2017.drop_duplicates(subset=['Name', 'Age', 'M/F', 'City', 'Country'])
print(marathon2017.shape)

# I will check if there are any null values in my dataframe.
print(marathon2017.isnull().sum())

# If I had any null values, I could either delete the rows containing the empty values or replace them with
# the mean or an appropriate value based on the context.

# Let's consider removing the rows containing null values in the 'Official Time' column.
# marathon2017 = marathon2017.dropna(how='all', subset='Official Time')
# I will discuss the method of replacing null values further.

# I will set the indexes and sort in descending order of age to see the oldest participants.
marathon2017_index = marathon2017.set_index(['Country', 'Age'])
print(marathon2017_index.sort_index(level='Age', ascending=False).head(20))

# To decode the names of countries that are currently listed as alpha-3 codes,
# I will create a new DataFrame using the JSON method based on Wikipedia.

# send a request to retrieve data from the JSON API.
url = 'https://restcountries.com/v3.1/all'
response = requests.get(url)

# retrieve the list of countries from the response and extract their three-letter codes and full names.
country_codes = response.json()

# will check in the source code which column names correspond to the data we need.
# print(country_codes)

# I use a list comprehension, which allows creating new lists from existing ones in a compact and efficient way.
country_data = [[country['cca3'], country['name']['common']] for country in country_codes]

# Create a DataFrame based on the list of countries and set the column names.
countries = pd.DataFrame(country_data, columns=['Country', 'Country name'])

print(countries.head())
print(countries.shape)

# I will add the full country name using merge with the "left" method because I need the main table to remain unchanged.
marathon = marathon2017.merge(countries, how='left', on='Country')
print(marathon.head())

# I will move our new column 'Country name' to a different position, after 'Country', using the pop() method
# to extract the column.
marathon = marathon.reindex(columns=['Name', 'Age', 'M/F', 'City', 'Country', 'Country name', 'Half', 'Official Time'])
print(marathon.head())

# Checking if there are any empty values in the new column
print(marathon.isnull().sum())

# I will replace the empty values with the values from the 'Country' column
marathon = marathon.fillna(method='ffill', axis=1).fillna(0)
print(marathon.isnull().sum())


# Creating a function that will help convert the time in the format "hh:mm:ss" into the total number of minutes
# of the marathon, this function will work with the help of a cycle.
def time_to_minutes(df, column_name, new_column_name):

    # I will create a new column in which new data will fall
    df[new_column_name] = 0

    # Go through each row in the column_name column using a loop and the enumerate() function
    for i, string in enumerate(df[column_name]):

        # Divide the time into hours, minutes and seconds
        time_parts = string.split(':')

        # In the 'Half' column there are several rows with the value "-", I will create a condition to skip these
        # rows and not cause a code error
        if "-" in string:
            continue

        # Convert each part of the time (hours, minutes and seconds) into the total number of minutes
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])
        total_minutes = hours * 60 + minutes + seconds / 60

        # Save the result to a new column
        df.at[i, new_column_name] = total_minutes

    return df


# Let's check the functionality of my function and convert the columns 'Half' and 'Official Time' into the total
# number of minutes of the marathon
time_to_minutes(marathon, 'Half', 'Half_dist_mins')
time_to_minutes(marathon, 'Official Time', 'Total_mins')

print(marathon.head(10))

# I will add a new column with the amount of time to overcome the marathon in hours
marathon['Total_hours'] = np.round(np.array(marathon['Total_mins']) / 60, 2)

# I will create a new column answering the question whether the participant ran the second half faster than the first
marathon['Is_second_part_faster'] = np.where(marathon['Half_dist_mins'] * 2 > marathon['Total_mins'], 'yes', 'no')
print(marathon.head())

# *************** - Analyse - ******************

# I will group the data using Groupby to determine how many marathon participants managed to run the second half
# of the distance faster than the first, whether it is real and what level of training these participants have
print(marathon.groupby(['Is_second_part_faster', 'M/F'])['Total_hours'].agg(['min', 'max', 'mean', 'count']))

# I will count the number of participants by gender in quantitative terms
gender_count = marathon['M/F'].value_counts(sort=True)
print(gender_count)

# And now the number of participants as a percentage
gender_props = marathon['M/F'].value_counts(sort=True, normalize=True)
print(gender_props)

# Creating a pie chart by the number of participants depending on gender
# plt.pie(gender_count, labels=gender_count.index, autopct='%1.1f%%')
# plt.title('Number of participants by gender')
# plt.show()

# I will analyze the top 10 countries by the number of marathon participants
# country_count = marathon['Country name'].value_counts()
# country_count = country_count.sort_values(ascending=False)
# top_10_countries = country_count[:10]
# top_10_countries.plot(kind='barh', title='Top 10 countries by the number of marathon participants')
# plt.show()

# I will analyze the number of participants by age in another way of plotting
# ages = marathon['Age'].value_counts()
# fig, ax = plt.subplots()
# ax.bar(ages.index, ages.values)
# ax.set_xticks(ages.index)
# ax.tick_params(axis='x', labelsize=5)
# plt.ylabel('Number of Participants')
# plt.xlabel('Age')
# plt.title('Number of participants by age')
# plt.bar_label(ax.bar(ages.index, ages.values), labels=ages.values, fontsize=6)
# plt.show()

# I will create a new dataframe to see from which countries, what age and gender the fastest runners are
grupping = marathon.groupby(['Country name', 'M/F', 'Age'])['Total_hours'].agg(['min', 'mean', 'count'])
grupping = grupping.reset_index()
grupping = grupping.sort_values('min')
print(grupping.head(10))

# let's see how age affects the time to overcome the marathon distance
age_group = marathon.groupby('Age')['Total_hours'].agg(['min', 'max', 'mean', 'count'])
age_group = age_group.reset_index()

# I will plot the corresponding graph to see how the results depend on age
fig, ax = plt.subplots()

ax2 = ax.twinx()

ax2.plot(age_group['Age'], age_group['min'], color='g', marker='.', label='The fastest time')
ax2.plot(age_group['Age'], age_group['mean'], color='b', marker='.', label='Average time')
ax.bar(age_group['Age'], age_group['count'], color='grey', alpha=0.3)

ax.set(title='Time to overcome the marathon by age',
       xlabel='Age',
       ylabel='Time. hours',
       xticks=age_group['Age'])

ax.tick_params(axis='x', labelsize=5)

ax2.set(ylabel='Number of Participants')
plt.legend()
plt.show()

# Add a new column, which will be the identifier for connecting the new table
marathon['id2016_2017'] = marathon['Name'] + marathon['M/F'] + marathon['City'] + marathon['Country']
print(marathon.head())

# Create a new dataset with the results of the 2016 marathon
marathon2016 = pd.read_csv('marathon_results_2016.csv')
print(marathon2016.head())

# Сreate a new column that will serve as the id for the merge
marathon2016['id2016_2017'] = marathon2016['Name'] + marathon2016['M/F'] + marathon2016['City'] + marathon2016[
    'Country']
print(marathon2016.head())

# Create a dataframe that will contain participants who ran the Boston Marathon two years in a row in 2016 and 2017
twice = marathon.merge(marathon2016, how='inner', on='id2016_2017', suffixes=('_2017', '_2016'))

# Print result
print('The total number of participants in 2016 was ' + str(len(marathon2016)) + ' participants. In 2017: ' + str(
    len(marathon2017)) + ' participants. The number of participants who ran the Boston Marathon two years in a row was '
      + str(len(twice)) + ' participants.')
