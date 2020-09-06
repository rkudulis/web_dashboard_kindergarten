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
    PENDING_PATH_0 = r"https://raw.githubusercontent.com/vilnius/darzeliai/master/data/laukianciuju_eileje_ataskaita.csv"
    PENDING_PATH_1 = "data/laukianciuju_eileje_ataskaita.csv"
    try:
        pending = pd.read_csv(PENDING_PATH_0, sep=";", parse_dates=[3, 5, 6])
    except:
        pending = pd.read_csv(PENDING_PATH_1, sep=";", parse_dates=[3, 5, 6])
    pending.dropna(how='all', subset=['1 pasirinktas darželis', '2 pasirinktas darželis', '3 pasirinktas darželis', '4 pasirinktas darželis', '5 pasirinktas darželis'], inplace=True)
    pending = pending[pending['Lankymo data'].dt.year >= 2020]
    pending.loc[pending['Vaiko seniunija']=="-"] = np.nan
    pending.loc[pending['Vaiko seniunija']=='visos'] = np.nan

    
    by_year_and_district = pending.groupby(['Lankymo data','Vaiko seniunija'], as_index=False).agg({"Nr." : 'count'})
    by_year_and_district['Lankymo data'] = by_year_and_district['Lankymo data'].dt.year
    
    sen = {
    'Šnipiškių':'Šnipiškės', 'Grigiškių':'Grigiškės', 'Naujamiesčio':'Naujamiestis', 'Žvėryno':'Žvėrynas', 'Senamiesčio':'Senamiestis',
       'Pašilaičių':'Pašilaičiai', 'Verkių':'Verkiai', 'Naujosios Vilnios':'Naujoji Vilnia', 'Pilaitės':'Pilaitė', 'Lazdynų':'Lazdynai',
       'Fabijoniškių':'Fabijoniškės', 'Šeškinės':'Šeškinė', 'Panerių':'Paneriai', 'Antakalnio':'Antakalnis',
       'Karoliniškių':'Karoliniškės', 'Žirmūnų':'Žirmūnai', 'Justiniškių':'Justiniškės', 'Naujininkų':'Naujininkai',
       'Viršuliškių':'Viršuliškės', 'Rasų':'Rasos', 'Vilkpėdės':'Vilkpėdė'
       }
    by_year_and_district['Vaiko seniunija'] = by_year_and_district['Vaiko seniunija'].map(sen)
    
    by_year_and_district = pd.pivot_table(by_year_and_district, index='Vaiko seniunija', columns='Lankymo data', values='Nr.', aggfunc='sum')
    by_year_and_district.sort_values(2020, 0, False, inplace=True)
    
    graph_one = []
    
    for yr in by_year_and_district.columns:
        graph_one.append(
            go.Bar(
            name=str(yr),
            x = by_year_and_district.index,
            y = by_year_and_district[yr]
            )
        )

    layout_one = dict(xaxis = dict(title = '', tickangle=-45),
                yaxis = dict(title = ''),
                barmode='stack',
                title = dict(text='Pateiktų prašymų skaičius<br>pagal metus ir seniūnijas', xanchor='center', yanchor='top')
                )
    

# second chart plots ararble land for 2015 as a bar chart
    map_data_path_0 = r'http://gis-vplanas.opendata.arcgis.com/datasets/6d5088b44dba4643a6611455d5352268_1.geojson'
    map_data_path_1 = r"data/Vilniaus_miesto_ribos.geojson"
    try:
        with urlopen(map_data_path_0) as response:
            counties = json.load(response)
    except:
        with open(map_data_path_1) as file:
            counties = json.load(file)

    graph_two = []

    visible = [True] + [False] * (len(by_year_and_district.columns) - 1)
    for i, col in enumerate(by_year_and_district.columns):
        graph_two.append(
           go.Choroplethmapbox(geojson=counties, featureidkey='properties.SENIUNIJA',
                               locations=by_year_and_district.index,
                               z=by_year_and_district[col], colorscale="Magenta",
                               zmin=by_year_and_district[col].min(),
                               zmax=by_year_and_district[col].max(),
                               marker_opacity=0.5, marker_line_width=0,
                               name=f"Metai<br>{col}",
                               visible=visible[i])
        )
    dropdown_list = []
    
    for col in by_year_and_district.columns:
        dropdown_list.append(
            dict(
                args=['visible', (by_year_and_district.columns==col).tolist()],
                label=col,
                method='restyle'
            )
        )
    
    layout_two = dict(
        updatemenus=[
            dict(
                dict(
                    buttons=list(dropdown_list)
                ),
            type='buttons',
            direction="right",
            xanchor='left',
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.08 ,
            y=1.12,
        )],
        annotations=[
            dict(text="Metai:", x=0, xref="paper", y=1.08, yref="paper",
                             align="left", showarrow=False)],
        mapbox=dict(center=dict(lat=54.687773, lon=25.269452),zoom=9,
                    style='carto-positron'),
        height=600,
        title = dict(text="Interaktyvus prašymų žemėlapis pagal metus seniūnijas")
        )
    
    
# Indicator
    CURRENT_PATH_0 = r"https://raw.githubusercontent.com/vilnius/darzeliai/master/data/lankanciu_vaiku_ataskaita_pagal_grupes.csv"
    CURRENT_PATH_1 = "data/lankanciu_vaiku_ataskaita_pagal_grupes.csv"
    try:
        current = pd.read_csv(CURRENT_PATH_0, sep=";", parse_dates=[4,5])
    except:
        current = pd.read_csv(CURRENT_PATH_1, sep=";", parse_dates=[4,5])
    current['Vaiko priėmimo į grupę data'] = pd.to_datetime(current['Vaiko priėmimo į grupę data'], errors='coerce')
    current['YEAR'] = current['Vaiko priėmimo į grupę data'].dt.year
    indicator_data = current.groupby('YEAR').agg({"Nr." : 'count'})
    graph_three = []
    graph_three.append(
        go.Indicator(
            mode = "number+delta",
            value = indicator_data.loc[2020]['Nr.'],
            title = {"text": 'Priimta vaikų 2020 m.'},
            delta = dict(reference=indicator_data.loc[2019]['Nr.'], relative=True),
            domain = dict(x=[0, 1], y=[0, 1])
            )
    )

    layout_three = dict()

    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))


    return figures
