# make a dashboard to make user investment plan
# Import libraries
import pandas as pd
import dash
from dash import html, dcc, dash_table
from dash.dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
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
instructions_text = '''**Current Investments Table:**    
- Ticker Column: Fill this column out with the tickers' of all of your current investments. Be sure to put the tickers in all capitals.  
- Quantity Column: Fill this column out with the quantity of each ticker that you currently own.   
- Monthly Investment Distribution Column: Fill this column out with the percent of your monthly investment that you would like to go to each investment. \
Be sure to have the Monthly Investment Distribution Column add up to 100%.  
- Current Portfolio Distribution Column: Don't worry about filling out this column, it will auto-update based on your input.  
- Use the 'Add Row' button to add rows to the table, you can also delete rows using the 'X' on the left of the table.  

A pie chart will appear below the table, this pie chart shows your current portfilio distribution.
'''

# predicted portfolio growth markdown text
growth_text = '''**Portfolio Growth:**  
- Fill out the dollar amount you plan to invest per month and the number of years you plan to invest that amount.  
- Click the submit button once you have entered those two amounts. 

Below two amounts will appear: the total amount you invested over that time (including your initial investments from the table above) and the predicted future portfolio worth.  
A graph will also appear below that will compare the trends of these two amounts over time. 
'''

# Notes markdown text
notes_text = '''**Notes:**  
- The total amount invested is based on if your bought all of the stocks in the current investments table at the current date and time. \
    Most likely this is not the case and the worth of the stocks has changed over time, therefore this may add some error into the model.  
- The interest rate of the stock used for the growth calculation was the Average Annual Growth Rate (AAGR). This rate was calculated over the past number of years that you plan to invest. \
    For example if you plan to invest for eight years it would calculate the AAGR for the past eight years. If the amount of years you plan to invest is longer than the number of years the \
        stock has existed then the AAGR would be calculated for the max number of years the stock has existed.  
- The model was built on the assumptions that the dividends would be reinvested quarterly. The amount of dividends was taken as the average dividends that has been returned for the past number of years \
    you plan to invest, similar to the time period for the AAGR.  
- The model was built using the average cost per share of the stock for the past time period the user plans to invest, similar to time period for the AAGR.  
- This model is purely for educational purposes and is not meant to be taken as actionable investment advice. Past returns are not a gaurantee of future returns. 
'''
# starter data for the datatable
portfolio = pd.DataFrame({
    'ticker':['FXAIX','FSSNX','FSPSX','VDADX','FXNAX','VGAVX','FSRNX'],
    'quantity':[16.81,18.957,11.455,76.756,12.256,197.257,18.878],
    'future_percents':[30,25,25,5,5,5,5]
})

# global variable to keep track of clicks on the data table adding rows
n_old = 0

# markdown style
markdown_style = {'text-align':'left','color': '#373F27','font-size':20,'font_family': 'Verdana','backgroundColor': '#FFFFFF', 'padding':'5px'}
# input style
input_style = {'font-size':20,'color':'#373F27','margin': '2px','padding': '5px'}
# table style
table_style = {'font_size':20,'font_family':'Verdana','color': '#373F27', 'backgroundColor': '#FFFFFF', 'border':'1px solid #373737'}
# table style
table_style_header = {'font_size':20,'font_family':'Verdana', 'font_weight': 'bold','color': '#373F27', 'backgroundColor': '#E9E7DA','border':'1px solid #373737'}
# paragraph style
p_style ={'text-align':'left','color': '#373F27','font-size':20,'font_family': 'Verdana','backgroundColor': '#FFFFFF', 'padding':'5px'}

# create the app layout
app.layout = html.Div([
    # make title
    html.H1('Investment Strategy'),
    # instructions for dashboard
    dcc.Markdown(children = instructions_text, style = markdown_style),
    # datatable for user input
    html.Div([
        dash_table.DataTable(
            id='user-input',
            style_data = table_style,
            style_header = table_style_header,
            data = portfolio.to_dict('records'),
            columns = [
                {'id':'ticker', 'name':'Ticker', 'type':'text'},
                {'id':'quantity', 'name':'Quantity', 'type':'numeric', 'format':Format(precision=2, scheme=Scheme.fixed)},
                {'id':'future_percents', 'name':'Monthly Investment Distribution (%)', 'type':'numeric', 'format':Format(precision=2, scheme=Scheme.fixed)},
                {'id':'percent', 'name':'Current Portfolio Distribution (%)', 'type':'numeric', 'format':Format(precision=2, scheme=Scheme.fixed)},
            ],
            editable = True,
            row_deletable = True,
        ),
        html.Button('Add Row', id='editing-rows-button', n_clicks=0),
    ]),
    html.Br(),
    # Piechart of current user investment strategy
    html.Div([
        dcc.Graph(id = 'investment-distribution')
    ]),
    html.Br(),
    # input the rest of our user data
    html.Div([
        dcc.Markdown(children = growth_text, style = markdown_style),
        dbc.Row([
            dbc.Col(html.P("Amount Invested per Month:", style = p_style)),
            dbc.Col(dcc.Input(id='monthly_investment',type="number",placeholder="Monthly Investment", min=0, style=input_style)),
        ]),
        dbc.Row([
            dbc.Col(html.P("Number of Years Plan to Invest:", style = p_style)),
            dbc.Col(dcc.Input(id='years_to_invest',type="number",placeholder="Years to Invest", min=0, style=input_style)),
        ]),
        dbc.Row([
            # add a button that tracks the number of clicks
            dbc.Col(),
            dbc.Col(html.Button('Submit', id='submit-val', n_clicks=0)),
        ]),
    ]),
    html.Div([
            html.P(id='amt-invested', style = p_style),
            # print the prediction of the machine learning model
            html.P(id='growth-predictions', style = p_style),
    ]),
    # scatter plot of selection from drop down menu
    html.Div([
        dcc.Graph(id = 'predictions-graph'),
        dcc.Markdown(children = notes_text, style = markdown_style),
    ]),

])

# callback and function to add rows to the datatable and to update the quantity column
@app.callback(Output('user-input', 'data'),
              Input('user-input','data_timestamp'),
              Input('editing-rows-button', 'n_clicks'),
              State('user-input', 'data'))
def update_row(timestamp, n_clicks, rows):
    global n_old
    if n_clicks > 0 and n_clicks>n_old:
        rows.append({'ticker':'','quantity':0,'future_percents':0,'percent':0,'editable':True,'deletable':True})
        n_old = n_old+1
    try:
        list = []
        for row in rows:
            list.append(row['quantity'])
        total = sum(list)
        for row in rows:
            quantity = float(row['quantity'])
            row['percent'] = (quantity/total)*100 
    except:
        print('Error')
    return rows

# callback and funtion to make the pie chart of the users current investment distributions
@app.callback(Output('investment-distribution','figure'),
              Input('user-input','data'))
def pieUserInvest (rows):
    df = pd.DataFrame(rows)
    fig1 = px.pie(df, values=df['percent'], names=df['ticker'], color_discrete_sequence=px.colors.sequential.speed)
    fig1.update_layout(plot_bgcolor = '#D5D5D5')
    fig1.update_layout(title="User Investment Strategy",title_font=dict(size=20, color='#373F27', family = 'Verdana'))
    fig1.update_traces(marker=dict(line=dict(color='#373737', width=1)))
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
    return f'Predicted Future Portfolio Worth: ${prediction.round(2)}' 

# callback and function to get the dollar amount invested over the years not including initial investment
@app.callback(Output('amt-invested','children'),
              Input('submit-val','n_clicks'),
              State('user-input','data'),
              State('monthly_investment','value'),
              State('years_to_invest','value'))
def investmentPredictions (n_clicks, data, monthly, years):
    user_data = pd.DataFrame(data)
    current_portfolio_worth = inv.currentPortfolioWorth(user_data)
    amount_invested = ((monthly*12)*years)+current_portfolio_worth
    return f'Total Amount Invested: ${amount_invested.round(2)}' 

# callback function to make a graph of the predictions we just performed
@app.callback(Output('predictions-graph','figure'),
              Input('submit-val','n_clicks'),
              State('user-input','data'),
              State('monthly_investment','value'),
              State('years_to_invest','value'))
def investmentPredictions (n_clicks, data, monthly, years):
    user_data = pd.DataFrame(data)
    prediction = inv.amountPeryear(user_data, monthly, years)
    pred_with_investments = inv.compareInvestedtoGrowth(prediction,user_data,monthly,years)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x = pred_with_investments['Year'], y = pred_with_investments['Amount'], name = 'Predicted Investments Worth',
                              line = dict(color='#636B46')))
    fig2.add_trace(go.Scatter(x = pred_with_investments['Year'], y = pred_with_investments['Money_Invested'], name ='Amount Invested',
                              line = dict(color='#949494', dash='dash')))
    fig2.update_layout(legend_title_text = 'Legend',legend = dict(font=dict(size=15, color='#373F27', family = 'Verdana')))
    fig2.update_layout(title = 'Predicted Portfolio Growth',title_font=dict(size=20, color='#373F27', family = 'Verdana'))
    fig2.update_xaxes(title = 'Year', title_font=dict(size=15, color='#373F27', family = 'Verdana'))
    fig2.update_yaxes(title = 'Portfolio Worth (USD)', title_font=dict(size=15, color='#373F27', family = 'Verdana'))
    fig2.update_layout(plot_bgcolor = '#E9E7DA')
    return fig2

# Run the app
if __name__ == '__main__':
    app.run_server()