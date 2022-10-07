# make a dashboard to make user investment plan
# Import libraries
import pandas as pd
import numpy as np
import dash
from dash import html, dcc, dash_table, html
from dash.dash_table.Format import Format, Scheme, Trim
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import gunicorn
import investment_functions as inv

# Create a dash application
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{"name":"viewport","content":"width=device-width, initial-scale=1.0,maximim-scale=1.2,minimum-scale=0.5"}])
app.title = 'Investment Strategy'                               # change the name of the application
server = app.server

portfolio = pd.DataFrame({
    'ticker':['FXAIX','FSSNX','FSPSX','VDADX','FXNAX','VGAVX','FSRNX'],
    'quantity':[16.81,18.957,11.455,76.756,12.256,197.257,18.878],
    'future_percents':[0.30,0.25,0.25,0.05,0.05,0.05,0.05]
})
portfolio = inv.percents(portfolio)

# create the app layout
app.layout = html.Div([
    # make title
    html.H1('Investment Strategy'),

    html.Div([
        dash_table.DataTable(
            id='user-input',
            data = portfolio.to_dict(),
            columns = [
                {'id':'ticker', 'name':'Ticker', 'type':'text'},
                {'id':'quantity', 'name':'Quantity', 'type':'numeric', 'format':Format(precision=2, scheme=Scheme.fixed)},
                {'id':'future_percents', 'name':'Percents (future)', 'type':'numeric', 'format':Format(precision=2, scheme=Scheme.fixed)},
                {'id':'percent', 'name':'Percents (current)', 'type':'numeric', 'format':Format(precision=2, scheme=Scheme.fixed)},
                ],
            editable = True,
            row_deletable = True,
        ),
        html.Button('Add Row', id='editing-rows-button', n_clicks=0),

    ])


])

@app.callback(
    Output('user-input', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('user-input', 'data'),
    State('user-input', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

# Run the app
if __name__ == '__main__':
    app.run_server()