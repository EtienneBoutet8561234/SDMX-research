# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

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
    Convert csv data that has only one OBS_VALUE per CHARACTERISTIC, and one CHARACTERISTIC per REF_AREA to a dataframe
     that differentiate two characteristic while setting them into the same REF_AREA/GUID.
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


def csv2statmergeDATAFRAME(csv, differenciationHeader, valueHeader, differenciationValue1, differenciationValue2,matchingheadervalue, headerColor, nameHeaderX,
                           nameHeaderY, nameHeaderColor):
    """
      Convert csv data that has only one OBS_VALUE per CHARACTERISTIC, and one CHARACTERISTIC per REF_AREA to a dataframe
     that differentiate two characteristic while setting them into the same REF_AREA/GUID.

    :param csv:The csv file in text format your want to convert. Requests can
    be convert to text format by using csv.text
    :param differenciationHeader: (ex:CHARACTERISTIC)
    :param valueHeader: (ex: OBS_VALUE)
    :param differenciationValue1: (ex:1)
    :param differenciationValue2: (ex:2)
    :param matchingheadervalue: (ex:REF_AREA)
    :param headerColor: id of the header selected for color (ex:"REF_AREA")
    :param nameHeaderY: name of y title display on the graph
    :param nameHeaderX: name of x title display on the graph
     :param nameHeaderColor: name of color title display on the graph

    :return:text in panda dataframe format
    """
    lines = csv.split('\n')
    result = {}
    headers = lines[0].split(',')

    # set x content

    positionOfHeaderInArray = -1
    for i in range(len(headers)):
        if headers[i] == valueHeader:
            positionOfHeaderInArray = i
            break
    if positionOfHeaderInArray == -1:
        print("Header " + valueHeader + " not found")
        return None
    else:
        positionOfHeaderInArray2 = -1
        for p in range(len(headers)):
            if headers[p] == differenciationHeader:
                positionOfHeaderInArray2 = p
                break
        if positionOfHeaderInArray2 == -1:
            print("Header " + differenciationHeader + " not found")
            return None

        for o in range(len(headers)):
            if headers[o] == matchingheadervalue:
                positionOfHeaderInArray3 = o
                break
        if positionOfHeaderInArray3 == -1:
            print("Header " + matchingheadervalue + " not found")
            return None

        contentstat1 = []
        contentstat2 = []
        colorContent = []
        for j in range(1, len(lines) - 1):
            lineContent = lines[j].split(',')
            if lineContent[p] == differenciationValue1:
                try:
                    contentstat1.append(float(lineContent[i]))
                except:
                    contentstat1.append(0)
                matchvalue=lineContent[o]
                for k in range(1, len(lines) - 1):
                    lineContent = lines[k].split(',')
                    if lineContent[p] == differenciationValue2 and lineContent[o] == matchvalue:
                        try:
                            contentstat2.append(float(lineContent[i]))
                        except:
                            contentstat2.append(0)
                        colorContent.append(str(lineContent[o]))


    # set color content




    return {nameHeaderX: contentstat1, nameHeaderY: contentstat2, nameHeaderColor: colorContent}


# ----------------------------------------creating-dashboard-----------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options


# ***************************params to set manually*****************************************************************

ep = "https://api.statcan.gc.ca/census-recensement/profile/sdmx/rest/data/STC_CP,DF_CD,1.3/A5..1.57+59.1"
nameHeaderX = "nbre private houshold"
nameHeaderY = "nbre maried or living in common law"

# ********************************************************************************************************************

# fixed params

nameHeaderZ = "ref_area"

# params to set dynamicly (index_chara_1 & index_chara_2 & r_csv)

rev_ep = ep[::-1]
last_dot_index = len(ep) - rev_ep.index(".") - 1
ep_cut = ep[0:last_dot_index]
rev_ep_cut = ep_cut[::-1]
before_last_dot_index = len(ep) - rev_ep_cut.index(".") - rev_ep.index(".") - 1
chara_index = ep[before_last_dot_index:last_dot_index]
index_chara_1 = chara_index[0: chara_index.index("+")]
index_chara_2 = chara_index[chara_index.index("+")+1:]

r_csv = requests.get(ep, headers={"Accept": "text/csv"})

# getDataframe

t = csv2statmergeDATAFRAME(r_csv.text, "CHARACTERISTIC", "OBS_VALUE", index_chara_1, index_chara_2, "REF_AREA", "REF_AREA", nameHeaderX, nameHeaderY, nameHeaderZ)

# put Dataframe in a graph
df = pd.DataFrame(t)

fig = px.scatter(df, x=nameHeaderX, y=nameHeaderY, color=nameHeaderZ)
app.layout = html.Div(children=[
    html.H1(children='Python Dash SDMX tests 6'),
    html.Div(children='''
        Some nice graphs.
    '''),
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])
if __name__ == '__main__':
    app.run_server(debug=True)
