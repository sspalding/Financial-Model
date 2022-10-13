# Portfolio-Growth-Model
A dashboard to take in user input of stocks they are investing in and predict the portfolio growth over time.  
Check out the [Dashboard](https://portfolio-growth-model.herokuapp.com/)  

## Methodology:  
The main purpose of this project was to demonstrate the power of compounding over time.  The model was built using the yfinance library which uses the yahoo finance API to download market data. The model assumes the user is recievind dividends quarterly and is reinvesting their dividends. The model is also assuming that the user will invest the same amount for every month for the specified time period.  

### Calculations:  
The time frame for the calculations is taken as the number of years the user plans to invest but in the past. For example if the user plans to invest for eight years it would calculate the average for the past eight years. If the amount of years the user plans to invest is longer than the number of years the stock has existed then the average would be calculated for the max number of years the stock has existed.
- Average Dividends:  
    The average historical dividends for the given time frame. 
- Average Cost Per Share:  
    The cost per share was taken as the Open value for the first day of the month. The average was calculated for the given time frame. 
- Current Stock Worth:  
    The current stock work was calculated by multiplying the most recent cost per share for the Open of the first of the month by the quantity the user input. 
- Current Worth of the Portfolio:  
    The current worth of the portfolio was taken by summing the current stock worth of each of the stocks the user has in their portfolio. 
- Interest Rate:   
    The interest rate was calculated as the Average Annual Growth Rate (AAGR) of a given stock. It is given by the formulas below.  
    AAGR = (GR<sub>1</sub> + GR<sub>2</sub> + GR<sub>3</sub> + ... + GR<sub>N</sub>)/N
    GR = (YearWorth / PreviousYearWorth) - 1
    N = Number of Years
- Investment Growth:   
    If it was a month dividends were distributed:  
    total = amt + (amt * (interest / 12)) + monthly_contribution + ((amt / avg_cost_per_share) * dividends)   
    If it was not a month dividends were distributed:  
    Total = amt + (amt * (interest / 12)) + monthly_contribution  
    amt = the worth of the previous month   
    These totals were taken for every month the user planned to invest for and for every stock the user invested in. Then the end of year value for each stock for each     was summed to make a table of the years the user planned to invest and the total portfolio worth at the end of each year. 
    
### Definitions:  
- Dividend: An amount of money that is paid regularly to an invester from a company they invest in. 
- Ticker: AKA Ticker Symbol is an abbreviation used to uniquely identify publicly traded shares of a company
- Share / Stock: Units of ownership of a company
- Portfolio: An investor's collection of stocks that they own.
- Open: The starting period of trading on the stock market

## Build Instructions:  
1. Clone the main branch of the repository
2. If you are interested in playing around with the financial model that was built outside of the dashboard run the .ipynb file
3. Run the app.py file to run the dashboard on your local machine  

## Disclaimer:
This dashboard is meant to be used for investment purposes and not as actionable investment advice. Past performance is not an indicator of future performance.  
