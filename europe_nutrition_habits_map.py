#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 11:48:49 2025

@author: manickamvalliappan
"""

import pandas as pd
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import ipywidgets as widgets
import matplotlib.colors as mcolors


file_path = "estat_hlth_ehis_fv3i_filtered_en.csv"  
df = pd.read_csv(file_path)


world = gpd.read_file("ne_110m_admin_0_countries.shp")

world = world[world["CONTINENT"] == "Europe"]


world = world.merge(df, left_on="NAME", right_on="geo", how="left")


dropdown = widgets.Dropdown(
    options=df["quant_inc"].unique(),  
    value=df["quant_inc"][0],  
    description='Variable:',
    disabled=False,
)

output = widgets.Output()




def update_map(change):
    with output:
        clear_output(wait=True)  

        selected_column = dropdown.value
        
       
        df1 = world.loc[(world["quant_inc"] == selected_column) & (world["n_portion"] == "5 portions or more")]
        blue_cmap = mcolors.LinearSegmentedColormap.from_list(
            "blue_gradient", ["#e0f7ff", "#4f97a3", "#003366"], N=256
        )

       
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        ax.set_xlim(-30, 50)  
        ax.set_ylim(35, 72)  
        ax.set_axis_off()

 
        df1.plot(column="OBS_VALUE", cmap=blue_cmap, legend=True, ax=ax,
                 missing_kwds={"color": "lightgrey"}, vmin=0, vmax=40)
        
        
        
        plt.show()  

        
        m = folium.Map(location=[50, 10], zoom_start=4)  
        
        
        folium.Choropleth(
            geo_data=world.__geo_interface__,
            data=df.loc[df["quant_inc"] == selected_column],
            columns=["geo", "OBS_VALUE"],
            key_on="feature.properties.NAME",
            fill_color="BuGn",
            tooltip=folium.GeoJsonTooltip(fields=["geo", "OBS_VALUE"]),
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=selected_column,
        ).add_to(m)

        
        folium.LayerControl().add_to(m)
        display(m)  


dropdown.observe(update_map, names='value')


display(dropdown, output)


update_map(None)