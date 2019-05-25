# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 12:07:45 2019

@author: sjara
"""

from bokeh.plotting import figure, ColumnDataSource, curdoc, Row, show, output_file
from bokeh.models import HoverTool, CategoricalColorMapper, Select
import pandas as pd
import os

# change cwd to the location of this script
dir_script =  os.path.dirname(os.path.abspath("__file__"))
os.chdir(dir_script)

# initialize figure
viz = figure(x_axis_label = "Energy (kcal per serving)"\
             ,y_axis_label = "NRFI (nutrient density per 100 kcal)"\
             ,title="USDA Branded Food Products")

# import data
path = os.path.join(dir_script,"data.csv")
df = pd.read_csv(path, dtype=object)

# convert data types
float_cols = ["nrfi","serving_size", "household_serving_size", "energy_per_serving"]
df[float_cols] = df[float_cols].astype("float32")

####################
## 4
#
## set data source
#data_source = ColumnDataSource(df)
#
####################
## 5
#
## color by manufacturer
#mapper = CategoricalColorMapper(factors = ["Wal-Mart Stores, Inc.","Meijer, Inc.","Target Stores"]\
#                                ,palette=["blue","purple","gray"])
#
## add glyph
#viz.circle("energy_per_serving","nrfi", source=data_source\
#           ,legend="manufacturer", color=dict(field='manufacturer',transform=mapper))
#
####################
## 6
#
## define hover tool 
#hover = HoverTool(tooltips=[("long_name","@long_name")\
#                            ,("manufacturer","@manufacturer")\
#                            ,("nrfi", "@nrfi"),("energy per serving","@energy_per_serving kcal")\
#                            ,("serving size","@household_serving_size @household_serving_size_uom")])
#
## add hover tool 
#viz.add_tools(hover)
#
####################
## 7  -  !! dont forget to change show(viz) to show(layout) at the bottom of the script
#
## define Select widget
#manufacturers = list(pd.unique(df.manufacturer))
#manufacturers.append("All")
#select_widget = Select(title="Manufacturer", options=manufacturers, value="All")
#
## define layout
#layout = Row(select_widget,viz)
#
####################
## 8
#
## define callback for select_widget
#def update():
#    if select_widget.value != "All":
#        df_select = df[df.manufacturer == select_widget.value]
#        data_source.data.update(df_select)
#    else:
#        data_source.data.update(df)
#        
## call update() function when select_widget value changes        
#select_widget.on_change('value', lambda attr,old,new : update())
#
## update layout
#curdoc().add_root(layout)

## generate html file 
output_file("output_file.html")

## show visualization in browser
show(viz)                                # <------- here


