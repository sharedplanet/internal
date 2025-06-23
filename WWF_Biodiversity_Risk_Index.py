#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 18:33:10 2025

@author: manickamvalliappan
"""

import pandas as pd
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import ipywidgets as widgets


file_path = "BRF_2024_CountryProfiles_Download.xlsx"  
xls = pd.ExcelFile(file_path)


sheet_name = xls.sheet_names[1]
df = pd.read_excel(xls, sheet_name=sheet_name)


world = gpd.read_file("ne_110m_admin_0_countries.shp")


world = world.merge(df, left_on="NAME", right_on="Country", how="left")


dropdown = widgets.Dropdown(
    options=df.columns[2:],  
    value=df.columns[2],  
    description='Variable:',
    disabled=False,
)


output = widgets.Output()


def update_map(change):
    with output:
        clear_output(wait=True)  

        selected_column = dropdown.value
        

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        world.plot(column=selected_column, cmap="OrRd", legend=True, ax=ax, missing_kwds={"color": "lightgrey"})
        plt.title(f"Choropleth Map of {selected_column}")


        m = folium.Map(location=[20, 0], zoom_start=2)
        folium.Choropleth(
            geo_data=world.__geo_interface__,
            data=df,
            columns=["Country", selected_column],
            key_on="feature.properties.NAME",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=selected_column,
        ).add_to(m)
        
        



        folium.LayerControl().add_to(m)

        display(m)


dropdown.observe(update_map, names='value')


display(dropdown, output)


update_map(None)