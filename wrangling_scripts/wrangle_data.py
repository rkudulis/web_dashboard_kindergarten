import pandas as pd
import numpy as np

from urllib.request import urlopen
import json
import plotly.express as px

import plotly.graph_objs as go

# Use this file to read in your data and prepare the plotly visualizations. The path to the data files are in
# `data/file_name.csv`

def return_figures():
    """Creates four plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the four plotly visualizations

    """

    # first chart plots arable land from 1990 to 2015 in top 10 economies 
    # as a line chart
    pending = pd.read_csv("data/laukianciuju_eileje_ataskaita.csv", sep=";", parse_dates=[3, 5, 6])
    pending.dropna(how='all', subset=['1 pasirinktas darželis', '2 pasirinktas darželis', '3 pasirinktas darželis', '4 pasirinktas darželis', '5 pasirinktas darželis'], inplace=True)
    pending = pending[pending['Lankymo data'].dt.year >= 2020]
    pending.loc[pending['Vaiko seniunija']=="-"] = np.nan
    pending.loc[pending['Vaiko seniunija']=='visos'] = np.nan

 
    by_year_and_district = pending.groupby(['Lankymo data','Vaiko seniunija'], as_index=False).agg({"Nr." : 'count'}).sort_values("Nr.", 0, False)
    by_year_and_district['Lankymo data'] = by_year_and_district['Lankymo data'].dt.year
    sen = {
    'Šnipiškių':'Šnipiškės', 'Grigiškių':'Grigiškės', 'Naujamiesčio':'Naujamiestis', 'Žvėryno':'Žvėrynas', 'Senamiesčio':'Senamiestis',
       'Pašilaičių':'Pašilaičiai', 'Verkių':'Verkiai', 'Naujosios Vilnios':'Naujoji Vilnia', 'Pilaitės':'Pilaitė', 'Lazdynų':'Lazdynai',
       'Fabijoniškių':'Fabijoniškės', 'Šeškinės':'Šeškinė', 'Panerių':'Paneriai', 'Antakalnio':'Antakalnis',
       'Karoliniškių':'Karoliniškės', 'Žirmūnų':'Žirmūnai', 'Justiniškių':'Justiniškės', 'Naujininkų':'Naujininkai',
       'Viršuliškių':'Viršuliškės', 'Rasų':'Rasos', 'Vilkpėdės':'Vilkpėdė'
       }
    by_year_and_district['Vaiko seniunija'] = by_year_and_district['Vaiko seniunija'].map(sen)

    graph_one = []
    for yr in by_year_and_district['Lankymo data'].unique():    
        graph_one.append(
            go.Bar(
            name=str(yr),
            x = by_year_and_district.query("`Lankymo data`==@yr")['Vaiko seniunija'],
            y = by_year_and_district.query("`Lankymo data`==@yr")['Nr.'],
      )
    )

    layout_one = dict(xaxis = dict(title = '', tickangle=-45),
                yaxis = dict(title = ''),
                barmode='stack',
                title = dict(text='Prašymų skaičius pagal metus ir seniūnijas', xanchor='center', yanchor='top'),
                # xaxis_tickfont_size=14,
                automargin=True
                # margin=dict(l=30, r=0, t=0, b=100)
                )
    

# second chart plots ararble land for 2015 as a bar chart 

    with urlopen('http://gis-vplanas.opendata.arcgis.com/datasets/6d5088b44dba4643a6611455d5352268_1.geojson') as response:
        counties = json.load(response)
         
    graph_two = []

    by_district = by_year_and_district.groupby('Vaiko seniunija', as_index=False)['Nr.'].sum()

    graph_two.append(
           go.Choroplethmapbox(geojson=counties, featureidkey='properties.SENIUNIJA', locations=by_district['Vaiko seniunija'],
                               z=by_district['Nr.'], colorscale="Magenta", zmin=by_district['Nr.'].min(), zmax=by_district['Nr.'].max(),
                               marker_opacity=0.5, marker_line_width=0, )
    )
    layout_two = dict(mapbox=dict(center=dict(lat=54.687773, lon=25.269452), zoom=9, style='carto-positron'), width=800, height=900, 
                    #   automargin=True
                    #   margin=dict(l=0, r=0, t=0, b=100)
                    title = dict(text="Interaktyvus prašymų žemėlapis pagal seniūnijas")
                    )
    
# Indicator
    current = pd.read_csv("data/lankanciu_vaiku_ataskaita_pagal_grupes.csv", sep=";",
                     parse_dates=[4,5])
    current['Vaiko priėmimo į grupę data'] = pd.to_datetime(current['Vaiko priėmimo į grupę data'], errors='coerce')
    current['YEAR'] = current['Vaiko priėmimo į grupę data'].dt.year
    indicator_data = current.groupby('YEAR').agg({"Nr." : 'count'})
    graph_three = []
    graph_three.append(
        go.Indicator(
            mode = "number+delta",
            value = indicator_data.loc[2020]['Nr.'],
            title = {"text": "Lankančiųjų skaičius 2020 m.<br><span style='font-size:0.8em;color:gray'>* Grupių formavimas nuo rugsėjo mėn.</span><br>"},
            delta = dict(reference=indicator_data.loc[2019]['Nr.'], relative=True),
            domain = dict(x=[0, 1], y=[0, 1])
            )
    )

    layout_three = dict()#width=200, height=200)

    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))


    return figures
