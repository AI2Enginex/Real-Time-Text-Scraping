from plotly.graph_objs import *
from plotly.offline import init_notebook_mode, iplot
import pandas as pd
import yahooquery as yq
from datetime import datetime
import yfinance as yf
import plotly.express as px
import plotly.io as pio

# Set default renderer for Plotly
pio.renderers.default = "vscode"

# Initialize Plotly for Jupyter Notebook mode
init_notebook_mode(connected=True)

class GetTickerNews:
    """
    A class to retrieve news data from a CSV file based on different criteria
    (Company name, Label, and Date).
    """
    
    @classmethod
    def get_news_by_company(cls, file_name='E:/MoneyControl Data Scraping/money_control_result.csv', feature='News', company_name=None):
        """
        Fetches news related to a specific company from a CSV file.
        """
        try:
            df = pd.read_csv(file_name)
            return df[df[feature].str.contains(company_name, case=False)]
        except Exception as e:
            return e

    @classmethod
    def get_news_by_Label(cls, file_name='E:/MoneyControl Data Scraping/money_control_result.csv', feature='Label', Label_name=None):
        """
        Fetches news based on a specific label/category.
        """
        try:
            df = pd.read_csv(file_name)
            return df[df[feature].str.contains(Label_name, case=False)]
        except Exception as e:
            return e

    @classmethod
    def get_news_by_Date(cls, file_name='E:/MoneyControl Data Scraping/money_control_result.csv', feature='Date and Time', Date=None):
        """
        Fetches news published on a specific date.
        """
        try:
            df = pd.read_csv(file_name)
            return df[df[feature].str.contains(Date, case=False)]
        except Exception as e:
            return e

    @classmethod
    def display_single_line_plot(cls, data, feature1, feature2):
        """
        Displays a single-line plot for given data.
        """
        try:
            fig = px.line(data_frame=data, x=feature1, y=feature2,
                          title="ticker's " + feature2 + " value analysis")
            fig.show()
        except Exception as e:
            print(e)

    @classmethod
    def display_scatter_plot(cls, data, feature1, feature2):
        """
        Displays a scatter plot for given data.
        """
        try:
            fig = px.scatter(data_frame=data, x=feature1, y=feature2,
                             title="ticker's " + feature2 + " value analysis")
            fig.show()
        except Exception as e:
            print(e)

class GetSymbol:
    """
    A class to fetch ticker symbols and historical stock data.
    """
    
    @classmethod
    def read_company_name(cls, company_name):
        """
        Reads and returns a list containing the company name.
        """
        try:
            return [company_name]
        except Exception as e:
            return e

    @classmethod
    def get_symbol(cls, query, preferred_exchange):
        """
        Retrieves the stock symbol for a given company and preferred exchange.
        """
        try:
            data = yq.search(query)
        except ValueError:
            print(query)
        else:
            quotes = data['quotes']
            if len(quotes) == 0:
                return 'No Symbol Found'
            
            symbol = quotes[0]['symbol']
            for quote in quotes:
                if quote['exchange'] == preferred_exchange:
                    symbol = quote['symbol']
                    break
            return symbol

    @classmethod
    def get_historical_data(cls, ticker, y1, m1, d1, y2, m2, d2):
        """
        Fetches historical stock price data for a given ticker and date range.
        """
        try:
            start = datetime(y1, m1, d1)
            end = datetime(y2, m2, d2)
            return yf.download(ticker, start=start, end=end)
        except Exception as e:
            return e

class GetTickersData:
    """
    A class to fetch stock-related news based on different filters.
    """
    
    def __init__(self, ticker=None, Label=None, Date=None):
        self.ticker = ticker
        self.label = Label
        self.date = Date

    def get_df_by_ticker(self):
        """
        Fetches news articles related to a specific ticker symbol.
        """
        try:
            return GetTickerNews().get_news_by_company(company_name=self.ticker)
        except Exception as e:
            return e

    def get_df_by_label(self):
        """
        Fetches news articles based on a specific label.
        """
        try:
            return GetTickerNews().get_news_by_company(company_name=self.label)
        except Exception as e:
            return e

    def get_df_by_date(self):
        """
        Fetches news articles published on a specific date.
        """
        try:
            return GetTickerNews().get_news_by_company(company_name=self.date)
        except Exception as e:
            return e

class GetSymbolDict:
    """
    A class to manage company symbols and retrieve historical stock prices.
    """
    
    def __init__(self, company):
        self.ticker_name = GetSymbol().read_company_name(company)
        self.df = pd.DataFrame({'Company name': self.ticker_name})
        self.company = company

    def get_historical_price(self, year1, month1, date1, year2, month2, date2):
        """
        Fetches historical stock prices based on the company's ticker symbol.
        """
        try:
            stock_name = self.company.replace(" ", "").upper() + ".NS"
            return GetSymbol().get_historical_data(ticker=stock_name, y1=year1, m1=month1, d1=date1, y2=year2, m2=month2, d2=date2)
        except Exception as e:
            return e

    def generate_dict(self, exchange_name):
        """
        Generates a dictionary mapping company names to their stock symbols.
        """
        try:
            self.df['Company symbol'] = self.df.apply(lambda x: GetSymbol().get_symbol(
                x['Company name'], preferred_exchange=exchange_name), axis=1)
            return dict(zip(self.df['Company name'].to_list(), self.df['Company symbol'].to_list()))
        except Exception as e:
            return e

if __name__ == '__main__':
    # Fetch news articles related to 'Atul Auto'
    gtd = GetTickersData(ticker='atul auto')
    print(gtd.get_df_by_ticker())
    
    # Get historical stock prices for 'Atul Auto'
    gsd = GetSymbolDict(company='Atul Auto')
    company_data = gsd.get_historical_price(
        exchange_name='NSE', year1=2023, month1=8, date1=1, year2=2023, month2=8, date2=5)

    # gsd.draw_graphs(dataframe=company_data,
    #                 column_1=company_data.index, column_2='Close', type='line')
