from ast import List
import copy
import dash
from dash.dependencies import Input, Output
from dash import html

import dash_pivottable

import requests
from flask import Flask, Response
from flask import request
import json
import csv

#import re
import pyparsing as pp



#One and only variable for this program

#ep_data = "https://fdi-design-codr.dev.cloud.statcan.ca/rest/data/STC,DF_13100845,1.0/3+4+5+6+7+8+9+10+11+12+13.1.1.1"
ep_data="https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_PR,1.3/A5..1.2.1"

#-----------------saving data from request into a python array--------------

r_csv = requests.get(ep_data, headers={"Accept": "application/vnd.sdmx.data+csv; labels=both; timeformat=original"})

csvText=r_csv.text

def separate(string) -> pp.List[str]:
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
                    comma_separated_list.append(chunk)
                    chunk = ''

                elif character == '"':
                    in_quotes = False if in_quotes else True

                else:
                    chunk += character

            comma_separated_list.append(chunk)
            return comma_separated_list

def saveInPyData(csvText):
    lines = csvText.split('\n')
    array=[]
    for i in range (0,len(lines)):
       
        #change here so that dsnt thake  inside ""   

        line=separate(lines[i]) 
            
        array.append(line)
       
    return array

data1234=saveInPyData(csvText)

print(data1234[4][4])
# ----------saved data without thigs that are before ":"

    
data1234_copy=copy.deepcopy(data1234)
for i in range(0,len(data1234_copy)):
    for j in range (0,len(data1234_copy[i])):
        if ":" in data1234_copy[i][j]:
            temp=data1234_copy[i][j][str(data1234_copy[i][j]).find(":")+1:]
            data1234_copy[i][j]=temp
print("init:"+data1234[4][4])
print(data1234_copy[4][4])

#----------get column and row arr for headers--------------------------------------------------------------------------------------------
#----------get adress request for dataflow from the the adress of the data request-------------------------

#ex: https://fdi-design-codr.dev.cloud.statcan.ca/rest/data/STC,DF_13100845,1.0/3+4+5+6+7+8+9+10+11+12+13.1.1.1------------>https://fdi-design-codr.dev.cloud.statcan.ca/rest/dataflow/STC/DF_13100845/1.0
temp=ep_data
if(ep_data[len(ep_data)-1]=="/"):
    temp=ep_data[:len(ep_data)-2]
lastin=temp.rfind("/")
temp=temp[:lastin]

#remove all , and replace with /
indexcomma= temp.find(',')
while(indexcomma!=-1):
    temp=temp.replace(',','/')
    indexcomma= temp.find(',')

temp=temp.replace("data","dataflow")
#print("temp:"+temp)
ep_dataflow=temp
#-----------------get-table-params----------------------------------------------------------------------------------

# json request 

r = requests.get(ep_dataflow, headers={"Accept": "application/vnd.sdmx.structure+json;version=1.0"})
data2 = r.json()
# title_uncut=str(data2['data']['dataflows'][0]['names'])

# title_cut1=title_uncut[title_uncut.find("'en': '")+7:len(title_uncut)]
# title_cut2=title_cut1[0:title_cut1.find("'")]
# title=title_cut2
name=str(data2['data']['dataflows'][0]['name'])

def return_layout_column():
    i=0
    while i<len(data2['data']['dataflows'][0]['annotations']):
        type=data2['data']['dataflows'][0]['annotations'][i]['type']
        
        if(type=="LAYOUT_COLUMN"):
            return data2['data']['dataflows'][0]['annotations'][i]['title']
        i=i+1
    return

def return_layout_row():
    i=0
    while i<len(data2['data']['dataflows'][0]['annotations']):
        type=data2['data']['dataflows'][0]['annotations'][i]['type']
        
        if(type=="LAYOUT_ROW"):
            return data2['data']['dataflows'][0]['annotations'][i]['title']
        i=i+1
    return 

columnList=str(return_layout_column()).split(',')
rowList=str(return_layout_row()).split(',')

#select the wright headers(headers with description) according to the dataflow headers (no description)

columActualList=[]
for i in range (0,len(columnList)):
    for j in range(0,len(data1234[0])):
        if (columnList[i] in data1234[0][j]):
            temp=data1234[0][j]
            if ":" in temp:
                temp=temp[str(temp).find(":")+1:]
            columActualList.append(temp)



rowActualList=[]
for i in range (0,len(rowList)):
    for j in range (0,len(data1234[0])):
        if (rowList[i] in data1234[0][j]):
            temp=data1234[0][j]
            if ":" in temp:
                temp=temp[str(temp).find(":")+1:]
            rowActualList.append(temp)

# print("Original columns:  ")
# print(columnList)
# print("Selected columns:  ")
# print(columActualList) 
# print("Original rows:  ")
# print(rowList)
# print("Selected rows:  ")
# print(rowActualList)

#-----------------------------------------------------
app = dash.Dash(__name__)
app.title = 'My Dash example'

app.layout = html.Div([
    dash_pivottable.PivotTable(
        id='table',
        data=data1234_copy,
        cols=columActualList,
        colOrder="key_a_to_z",
        rows=rowActualList,
        rowOrder="key_a_to_z",
        rendererName="Table",
        aggregatorName="Average",
        vals=['OBS_VALUE'],
        #valueFilter={'Day of Week': {'Thursday': False}}
    ),
   
])


# @app.callback(Output('output', 'children'),
#               [Input('table', 'cols'),
#                Input('table', 'rows'),
#                Input('table', 'rowOrder'),
#                Input('table', 'colOrder'),
#                Input('table', 'aggregatorName'),
#                Input('table', 'rendererName')])
# def display_props(cols, rows, row_order, col_order, aggregator, renderer):
#     return [
#         html.P(str(cols), id='columns'),
#         html.P(str(rows), id='rows'),
#         html.P(str(row_order), id='row_order'),
#         html.P(str(col_order), id='col_order'),
#         html.P(str(aggregator), id='aggregator'),
#         html.P(str(renderer), id='renderer'),
#     ]


if __name__ == '__main__':
    app.run_server(debug=True)