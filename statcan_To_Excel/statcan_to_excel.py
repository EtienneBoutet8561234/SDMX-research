from typing import List
import requests
import pyparsing as pp
import pandas as pd

# URL
ep_data="https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_PR,1.3/A5..1.2.1"

# Get CSV data from URL
r_csv = requests.get(ep_data, headers={"Accept": "application/vnd.sdmx.data+csv; labels=both; timeformat=original"})
csvText=r_csv.text

def separate(string: str) -> List[str]:
    """
    Split a comma separated string into a List of strings.

    Resulting list elements are trimmed of double quotes.
    Comma's inside double quotes are ignored.

    :param string: A string to be split into chunks
    :return: A list of strings, one element for every chunk
    """
    comma_separated_list: List[str] = []

    chunk: str = ''
    in_quotes: bool = False

    for character in string:
        if character == ',' and not in_quotes:
            comma_separated_list.append(chunk.strip())
            chunk = ''

        elif character == '"':
            in_quotes = False if in_quotes else True

        else:
            chunk += character

    comma_separated_list.append(chunk.strip())
    return comma_separated_list


def saveInPyData(csvText):
    lines = csvText.split('\n')
    data=[]
    for i in range (0,len(lines)):

        #change here so that dsnt thake  inside ""   

        line=separate(lines[i]) 

        data.append(line)

    df = pd.DataFrame(data[1:], columns=data[0])  
    return df

data1234=saveInPyData(csvText)

# Same code for fetching and processing data

# Create a pandas dataframe
df = pd.DataFrame(data1234)

# Save it to excel file
df.to_excel('output3.xlsx', index=False)

print("Excel file has been created")
