import pandas as pd

# Read the CSV file
df = pd.read_csv("/Users/joseguzman/Library/CloudStorage/OneDrive-nwmissouri.edu/Spring2/44630/cintel-6-custom/Electric_Vehicle_Charging_Stations.csv")

# Remove the word "POINT" from the "New Georeferenced Column"
df['New Georeferenced Column'] = df['New Georeferenced Column'].str.replace('POINT ', '')

# Remove parentheses from the beginning and end of each value
df['New Georeferenced Column'] = df['New Georeferenced Column'].str.strip('()')

# Split the values into longitude and latitude
df[['Longitude', 'Latitude']] = df['New Georeferenced Column'].str.split(expand=True)

# Drop the original column "New Georeferenced Column"
df.drop(columns=['New Georeferenced Column'], inplace=True)

# Write the DataFrame to a new CSV file
df.to_csv("/Users/joseguzman/Library/CloudStorage/OneDrive-nwmissouri.edu/Spring2/44630/cintel-6-custom/EV_Charging_Stations_LongLat.csv", index=False)

# Print the DataFrame
print(df)

