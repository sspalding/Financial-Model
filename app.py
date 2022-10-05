# make a dashboard to make user investment plan
# Import libraries
import pandas as pd
import numpy as np
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import gunicorn

# Create a dash application
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{"name":"viewport","content":"width=device-width, initial-scale=1.0,maximim-scale=1.2,minimum-scale=0.5"}])
app.title = 'Investment Strategy'                               # change the name of the application
server = app.server

# create the app layout
app.layout = html.Div([

])

# Run the app
if __name__ == '__main__':
    app.run_server()