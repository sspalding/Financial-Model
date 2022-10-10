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

# dashboard instructions markdown text
instructions_text = '''Instructions for data table and dashboard.
'''

portfolio = pd.DataFrame({
    'ticker':['FXAIX','FSSNX','FSPSX','VDADX','FXNAX','VGAVX','FSRNX'],
    'quantity':[16.81,18.957,11.455,76.756,12.256,197.257,18.878],
    'future_percents':[0.30,0.25,0.25,0.05,0.05,0.05,0.05]
})
# portfolio = inv.percents(portfolio)

# create the app layout
app.layout = html.Div([
    # make title
    html.H1('Investment Strategy'),
    # instructions for dashboard
    dcc.Markdown(children = instructions_text),
    # markdown explaining how to use the table below
    html.Div([
        dash_table.DataTable(
            id='user-input',
            data = portfolio.to_dict('records'),
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
    ]),

    # Piechart of current user investment strategy
    html.Div([
        dcc.Graph(id = 'investment-distribution')
    ]),
    # input the rest of our user data
    html.Div([
        dbc.Row([
            dbc.Col(html.P("Amount Invested per Month:")),
            dbc.Col(html.P("Number of Years Plan to Invest:"))
        ]),
        dbc.Row([
            dbc.Col(dcc.Input(id='monthly_investment',type="number",placeholder="Monthly Investment", min=0)),
            dbc.Col(dcc.Input(id='years_to_invest',type="number",placeholder="Years to Invest", min=0)),
        ]),
        dbc.Row([
            # add a button that tracks the number of clicks
            dbc.Col(html.Button('Submit', id='submit-val', n_clicks=0)),
            # print the prediction of the machine learning model
            dbc.Col(html.Div(id='growth-predictions'))
        ]),
    ]),
    # drop down menu to choose to see growth of one ticker or all tickers
    # html.Div([

    # ]),
    # scatter plot of selection from drop down menu

])
# callback and function to update the current percent column
@app.callback(Output('user-input','data'),
              Input('user-input','data_timestamp'),
              State('user-input','data'))
def update_percent(timestamp, rows):
    list = []
    for row in rows:
        list.append(row['quantity'])
    total = sum(list)
    for row in rows:
        quantity = float(row['quantity'])
        row['percent'] = (quantity/total)*100
    return rows

# # callback and function to add rows to the datatable
# @app.callback(Output('user-input', 'data'),
#               Input('editing-rows-button', 'n_clicks'),
#               State('user-input', 'data'),
#               State('user-input', 'columns'))
# def add_row(n_clicks, rows, columns):
#     if n_clicks > 0:
#         rows.append({c['id']: '' for c in columns})
#     return rows

# callback and funtion to make the pie chart of the users current investment distributions
@app.callback(Output('investment-distribution','figure'),
              Input('user-input','data'))
def pieUserInvest (rows):
    df = pd.DataFrame(rows)
    fig1 = px.pie(df, values=df['percent'], names=df['ticker'], title="User Investment Strategy")
    return fig1

# callback and function to get the predicted value of the invests, basically using our functions we made
@app.callback(Output('growth-predictions','children'),
              Input('submit-val','n_clicks'),
              State('user-input','data'),
              State('monthly_investment','value'),
              State('years_to_invest','value'))
def investmentPredictions (n_clicks, data, monthly, years):
    user_data = pd.DataFrame(data)
    prediction1 = inv.amountPeryear(user_data, monthly, years)
    prediction = prediction1.iloc[-1:]
    prediction = prediction['Amount'].values[0]
    return f'Prediction: {prediction}' 

# Run the app
if __name__ == '__main__':
    app.run_server()