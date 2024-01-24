import pandas as pd
from pandasdmx import Request

# Initialize a Request for the specific agency, here we use 'ESTAT'
estat = Request('ESTAT')

# Define your Dataflow and the codes
dataflow = 'ILC_PW06'  # an example dataflow
key = {'freq': 'A', 'unit': 'PC', 'isced11': 'TOTAL', 'sex': 'T+F+M', 'age':'Y16-24', 'geo':'FR', 'TIME_PERIOD': '2013'}  

#params = {'startPeriod': '2013', 'endPeriod': '2015'}  # an example time period

# Request the data
data_response = estat.data(resource_id=dataflow, key=key)#in case param is neede it would go here

# Convert the data to a pandas DataFrame
df = data_response.to_pandas()

# Write the DataFrame to an Excel file
df.to_excel('sdmx_data4.xlsx', engine='openpyxl')
