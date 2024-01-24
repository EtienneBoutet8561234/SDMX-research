import pandas as pd
import requests
from io import BytesIO

from pandasdmx import Request

ecb = Request('ECB')  # ECB is built-in source for pandasdmx
data_response = ecb.data(resource_id='EXR', key='D.USD.EUR.SP00.A')

# Load the data into a pandas DataFrame
df = data_response.to_pandas()

# Write the DataFrame to an Excel file
df.to_excel('ecb_data2.xlsx')
