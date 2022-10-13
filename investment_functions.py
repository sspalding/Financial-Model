# libraries
import pandas as pd
import yfinance as yf
from datetime import date
import functools

# data information
today = date.today()
month = today.month
year = today.year

# Function to connect to yahoo finance and cache the information we get
# create a cache to store the data we get from yf
@functools.cache
def connectYahooFinance (Ticker):
    # get the data for the specific ticker
    ticker_data = yf.Ticker(Ticker)
    # create a dataframe of the history of the ticker
    ticker_data = pd.DataFrame(ticker_data.history(period = 'max'))
    # correct the index for the dataframe
    ticker_data.reset_index(inplace = True)
    return ticker_data

# function to get historical monthly cost per share
def MonthlyCost (Ticker):
    # first call the connect to yahoofinance function
    ticker_data = connectYahooFinance(Ticker)
    # filter data to only include info from the first of the month
    return ticker_data[ticker_data['Date'].dt.is_month_start]

# function to get historical dividend amt per share
def quarterlyDividends (Ticker):
    # first call the conncet to yahoofinance function
    ticker_data = connectYahooFinance(Ticker)
    # filter data to only include info when dividends were distributed
    return ticker_data[ticker_data['Dividends']!=0]

# function to calcuate the average dividends for each ticker
def CalculateAvgDividend(Ticker, Years_to_invest):
    # get the historical dividends
    dividends = pd.DataFrame(quarterlyDividends(Ticker))
    # find the first year the stock existed
    first_year = dividends.iloc[0]
    first_year = first_year['Date'].year
    # determine which came first, the timespan the user plans to invest or the first year the fund existed, then determine the date of that 
    years_invest = year-min(year-first_year, Years_to_invest)
    years_invest = f'{years_invest}-01-01'
    # get all of the dividends since that date
    dividends = dividends[(dividends['Date']> years_invest)]
    # find the average of those dividends
    average_dividend = dividends['Dividends'].mean()
    return average_dividend

# function to calc avg cost per share for each ticker
def CalculateAvgCostPerShare(Years_to_invest, Monthly_cost):
    cost_per_share = pd.DataFrame(Monthly_cost)
    # find the first year the stock existed
    first_year = cost_per_share.iloc[0]
    first_year = first_year['Date'].year
    # determine which came first, the timespan the user plans to invest or the first year the fund existed, then determine the date of that 
    years_invest = year-min(year-first_year, Years_to_invest)
    years_invest = f'{years_invest}-01-01'
    # find all of the cost per shares that have occured since that date
    cost_per_share = cost_per_share[(cost_per_share['Date']>years_invest)]
    # take the average of those values
    average_cost = cost_per_share['Open'].mean()
    return average_cost

# how much is your current initial investment worth
def calcCurrentWorth (Portfolio,Ticker,Monthly_cost):
    # get the data from the portfolio of the specific ticker
    quantity = Portfolio.loc[Portfolio['ticker'] == Ticker]['quantity']
    # get the data of the start of each month for the data
    cost_per_share = pd.DataFrame(Monthly_cost)
    # find the most recent value
    cost_per_share = cost_per_share.iloc[-1:]
    # multiply that most recent value by the quantity the user owns
    current_value = cost_per_share['Open'].values[0]*quantity.values[0]
    return current_value

# calculate the average annual interest rate of the individual stocks
def interestRate(Years_to_invest,Monthly_cost):
    # get a dataframe of the monthly costs for the specific ticker
    cost_per_share = pd.DataFrame(Monthly_cost)
    # make an empty list to hold our growth rates
    GR = []
    # find one year after the first year that the stock existed
    first_year = cost_per_share.iloc[0]
    first_year = first_year['Date'].year+1
    # determine which happended first, the first year the stock existed or the number of years the user plans to invest
    Years_to_invest = min(year-first_year, Years_to_invest)
    # itereate through the number of year
    for i in range (0,Years_to_invest):
        # find the date of one year
        old_date =f'{year-i}-12-01'
        old_value = cost_per_share.loc[cost_per_share['Date']==old_date]
        m=12
        # determine if that dataframe from the first date is empty 
        while old_value['Open'].empty:
            # iterate through the months of the year till you find one with data
            m = m-1
            old_date = f'{year-i}-{m}-01'
            old_value = cost_per_share.loc[cost_per_share['Date']==old_date]
        # get the open value of that month        
        old_value = old_value['Open'].values[0]
        # find a year that is one year older than our previous year
        j = i+1
        older_date = f'{year-j}-m-01'
        older_value = cost_per_share.loc[cost_per_share['Date']==older_date]
        # determine if that dataframe is empty
        while older_value['Open'].empty:
            # iterate through the months of year till you find one with data
            older_date = f'{year-j}-{m}-01'
            older_value = cost_per_share.loc[cost_per_share['Date']==older_date]
            m = m-1
        # get the open value of that month
        older_value = older_value['Open'].values[0]
        # calculate the growth rate of that year
        GR_i = (old_value/older_value)-1
        # add the growth rate to our list
        GR.append(GR_i)
    # add all of the growth rates
    sum_GR = sum(GR)
    # divded that sum by the number of years
    AAGR = sum_GR/Years_to_invest
    return AAGR

# calculate current portfolio worth 
def currentPortfolioWorth(Portfolio):
    # make an empty list for each of our tickers current values to go into
    current_value = []
    # iterate through all of the tickers in our portfolio
    for ticker in Portfolio['ticker']:
        # find the monthly cost of that ticker
        monthly_cost = MonthlyCost(ticker)
        # calculate the current worth of that ticker
        ticker_value = calcCurrentWorth(Portfolio,ticker,monthly_cost)
        # add that current worth to our list
        current_value.append(ticker_value)
    # sum all of the values in our list
    portfolio_current_value = sum(current_value)
    return portfolio_current_value

# make a function to predicted the growth of the portfolio
def totalInvestmentPrediction (Portfolio,Monthly_investments,Years_to_invest):
    # make a dataframe to hold the results for each of the tickers
    results = pd.DataFrame(columns = ['Month', 'Amount','Ticker'])
    # itereate through each of the tickers and their respective percents in the portfolio
    for ticker, percent in zip(Portfolio['ticker'], Portfolio['future_percents']):
        monthly_cost = MonthlyCost(ticker)                                  # find the monthly cost for each ticker
        percents = percent/100                                              # divided the percents by 100 to get them on the correct scale
        principal = calcCurrentWorth(Portfolio,ticker,monthly_cost)         # find the current worth of the stock
        interest = interestRate(Years_to_invest,monthly_cost)        # find the growth rate of the stock
        compounding_period = 12                                             # assign how often the interest will compound, 12 = monthly
        months = Years_to_invest*compounding_period                         # assign how lond the user plans to invest for
        monthly_contribution = percents*Monthly_investments                 # assign how much the user plans to invest in this stock per month
        dividends = CalculateAvgDividend(ticker,Years_to_invest)                            # calculate the average dividends returned
        dividends_compounding = 3                                           # the dividends compound quarterly
        avg_cost_per_share = CalculateAvgCostPerShare(Years_to_invest,monthly_cost)  # calculate the average cost per share of the stock
        # add the pricipal as the month one investment
        results =  results.append({'Month': 1, 'Amount': principal, 'Ticker':ticker}, ignore_index = True)
        # iterate through the months the user plans to invest for
        for i in range(2,months+1):
            # find the worth of the previous month
            amt = results.iloc[-1:]
            amt = amt['Amount'].values[0]
            # determine if it is a month that dividends are reinvested or not
            if (i%dividends_compounding)==0:
                    total = amt+(amt*(interest/12))+monthly_contribution+((amt/avg_cost_per_share)*dividends)
                    results =  results.append({'Month': i, 'Amount': total, 'Ticker':ticker}, ignore_index = True)
            else:
                    total = amt+(amt*(interest/12))+monthly_contribution
                    results =  results.append({'Month': i, 'Amount': total, 'Ticker':ticker}, ignore_index = True)
    return results

# now we need to add up all of the rows that have the same years
def amountPeryear(Portfolio,Monthly_investments,Years_to_invest):
    # calculate the total portfolio growth
    total_portfolio = totalInvestmentPrediction(Portfolio,Monthly_investments,Years_to_invest)
    # make a new dataframe to hold the year and amount that will be calculated
    sum_portfolio = pd.DataFrame(columns = ['Year', 'Amount'])
    # find the initail amount that the portfolio is worth
    initial_invest = currentPortfolioWorth(Portfolio)
    # append that amount to year 0 of the portfolio we created
    sum_portfolio = sum_portfolio.append({'Year':0,'Amount':initial_invest},ignore_index=True)
    # itereate throught the number of years to the user plans to invest
    for i in range(1,Years_to_invest+1):
        # find the sum of all of the months that are evenly divisible by 12, this is grouping our months
        per_year = total_portfolio[total_portfolio['Month']==i*12]['Amount'].sum()
        # append that amount to the portfolio with the number of years
        sum_portfolio =  sum_portfolio.append({'Year': i, 'Amount': per_year}, ignore_index = True)
    return sum_portfolio

# add a column of what money we put in to the portfolio dataframe
def compareInvestedtoGrowth(Total_investment, Portfolio, Monthly_investment, Years_to_invest):
    # calculate what the user invests per year
    yearly_investment = Monthly_investment*12
    # find the current worth of the user's portfolio
    portfolio_worth = currentPortfolioWorth(Portfolio)
    # create a empty list to hold the amount invested per year
    money_inv = []
    # insert the worth at time 0 into the list
    money_inv.insert(0,portfolio_worth)
    # insert the worth at year 1 into the portfolio
    money_inv.insert(1,portfolio_worth+yearly_investment)
    # iterate through the number of years the user plans to invest
    for i in range(2,Years_to_invest+1):
        # create a new variable that holds the amount invested last year
        last_year_amt = money_inv[i-1]
        # add the last year investment to the yearly investment to determine the total amount invested at the end of this year
        this_year_amt = last_year_amt + yearly_investment
        # insert that value into the correct year
        money_inv.insert(i,this_year_amt)
    # add the list we created with all of the yearly investments to the total investments dataframe
    Total_investment.insert(2,'Money_Invested',money_inv,True)
    return Total_investment