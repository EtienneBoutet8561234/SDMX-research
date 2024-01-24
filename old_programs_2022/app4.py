# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import by as by
# Python dash libraries

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

# import use for datarequests

import requests
from flask import Flask, Response
from flask import request
import json
import csv


# -------------- convert format functions -----------------------------------------------------------

def csvDATAFRAME(csv, headerX, headerY, headerColor, nameHeaderX, nameHeaderY, nameHeaderColor):
    """
    Convert csv text to panda dataframe format
    :param nameHeaderColor: name of color title display on the graph
    :param nameHeaderY: name of y title display on the graph
    :param nameHeaderX: name of x title display on the graph
    :param csv:The csv file in text format your want to convert. Requests can
    be convert to text format by using csv.text
    :param headerColor: id of the header selected for color (ex:"TIME_PERIOD")
    :param headerY:  id of the header selected for y (ex: "OBS_VALUE")
    :param headerX: id of the header selected for x (ex: "REF_AREA")
    :return:text in panda dataframe format
    """
    lines = csv.split('\n')
    result = {}
    headers = lines[0].split(',')

    # set x content

    positionOfHeaderInArray = -1
    for i in range(len(headers)):
        if headers[i] == headerX:
            positionOfHeaderInArray = i
            break
    if positionOfHeaderInArray == -1:
        print("Header " + headerX + " not found")
        return None
    else:
        xContent = []
        for j in range(1, len(lines) - 1):
            lineContent = lines[j].split(',')
            xContent.append(lineContent[i])

    # set y content

    positionOfHeaderInArray = -1
    for i in range(len(headers)):
        if headers[i] == headerY:
            positionOfHeaderInArray = i
            break
    if positionOfHeaderInArray == -1:
        print("Header " + headerY + " not found")
        return None
    else:
        yContent = []
        for j in range(1, len(lines) - 1):
            lineContent = lines[j].split(',')
            yContent.append(float(lineContent[i]))

    # set color content

    positionOfHeaderInArray = -1
    for i in range(len(headers)):
        if headers[i] == headerColor:
            positionOfHeaderInArray = i
            break
    if positionOfHeaderInArray == -1:
        print("Header " + headerColor + " not found")
        return None
    else:
        colorContent = []
        for j in range(1, len(lines) - 1):
            lineContent = lines[j].split(',')
            colorContent.append(lineContent[i])

    return {nameHeaderX: xContent, nameHeaderY: yContent, nameHeaderColor: colorContent}


# ----------------------------------------creating-dashboard-----------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

# params
ep = "https://fdi-design-codr.dev.cloud.statcan.ca/rest/data/STC,DF_13100845,1.0/3+4+5+6+7+8+9+10+11+12+13.1.1.1"
header_x_id = 'DGUID'
header_x_name = 'DGUID'
header_y_id = 'OBS_VALUE'
header_y_name = 'OBS_VALUE'
header_color_id = 'TIME_PERIOD'
header_color_name = 'TIME_PERIOD'

r_csv = requests.get(ep, headers={"Accept": "text/csv"})
print(r_csv.text)
t = csvDATAFRAME(r_csv.text, header_x_id, header_y_id, header_color_id, header_x_name, header_y_name, header_color_name)
df = pd.DataFrame(t)


# ------------------------ this next part is just to test read_csv method ------------------------------------
def csvWrite(csvText, filename):
    lines = csvText.split('\n')
    print(lines[0])

    with open(filename, 'w') as csvFile:
        writer = csv.writer(csvFile)

        for i in range(len(lines) - 1):

            text = lines[i].split(',')
            print(text)
            if text != "":
                writer.writerow(text)


csvWrite(r_csv.text, 'data1.csv')
data1 = pd.read_csv('data1.csv')

# -----------------------------------------------------------------------------------------------------------------

# Syntax of DataFrame.sort_values()

print(df[header_y_name])

print(df[header_y_name])
fig = px.bar(data1, x=header_x_name, y=header_y_name, color=header_color_name, barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),
    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])
if __name__ == '__main__':
    app.run_server(debug=True)
