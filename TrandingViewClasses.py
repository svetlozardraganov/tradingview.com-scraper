
#01 IMPORT LIBRARIES
from timeit import default_timer as timer
start = timer()

import pandas as pd
import matplotlib.pyplot as plt

import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import iplot
from plotly.subplots import make_subplots

import requests
import logging
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import sqlite3

import xlwings as xw
from pathlib import Path

import concurrent.futures

logging.getLogger().setLevel(logging.ERROR)

class DataBase():
    
    database_file = 'tradingview_database.db'
    # database_file = 'database_test.db'

    @classmethod
    def Start(cls): #Connect to Database
        cls.conn = sqlite3.connect(cls.database_file) #connect to sqlite3-database
        cls.cursor = cls.conn.cursor()
        logging.info('DataBase Connected')

    @classmethod
    def Stop(cls): #Disconnect/Commit to Database
        cls.conn.commit() # Commit your changes in the database
        cls.conn.close() #Closing the connection
        logging.info('DataBase Disconnected')
    
    @classmethod
    def AddToDatabase(cls, data): #method that innitiates the write-to-database method with the needed parameters
        """
        data = Instance of ScrapeTrendingView() Class
        """
        
        cls.StoreInDatabase(data=data.income_statement, table_name=(data.company_url + '/Income-Statement'))
        cls.StoreInDatabase(data=data.balanse_sheet, table_name=(data.company_url + '/Balance-Sheet'))
        cls.StoreInDatabase(data=data.cashflow_statement, table_name=(data.company_url + '/Cashflow-Statement'))
        cls.StoreInDatabase(data=data.statistics, table_name=(data.company_url + '/Ratios'))
        if data.dividents is not None:
            cls.StoreInDatabase(data=data.dividents, table_name=(data.company_url + '/Dividents'))
        cls.StoreInDatabase(data=data.company_data, table_name=(data.company_url + '/Company-Data'))

    @classmethod
    def StoreInDatabase(cls, data, table_name): #method that writes the data into the database
        """data = ScrapeTrendingView().income_statement \n
        data = ScrapeTrendingView().balanse_sheet \n
        data = ScrapeTrendingView().cashflow_statement \n
        data = ScrapeTrendingView().statistics \n
        data = ScrapeTrendingView().company_data \n\n

        table_name = Exchange-Ticker/Statement-Type \n
        Examples: \n
        table_name = NASDAQ-AAPL/Income-Statement \n
        table_name = NASDAQ-AAPL/Balance-Sheet \n
        table_name = NASDAQ-AAPL/Cashflow-Statement \n
        table_name = NASDAQ-AAPL/Ratios \n
        table_name = NASDAQ-AAPL/Company-Data \n
        """

        logging.info(f'Storring {table_name} in {cls.database_file}')
        data.to_sql(name=table_name, con=cls.conn, if_exists='replace',  index=True) #store dataframe to sqlite-database

    @classmethod
    def ReadFromDatabase(cls, table_name): #read data from Database, if available return the data if not return None
        """
        table_name = Exchange-Ticker/Statement-Type \n
        Examples: \n
        table_name = NASDAQ-AAPL/Income-Statement \n
        table_name = NASDAQ-AAPL/Balance-Sheet \n
        table_name = NASDAQ-AAPL/Cashflow-Statement \n
        table_name = NASDAQ-AAPL/Ratios \n
        table_name = NASDAQ-AAPL/Company-Data \n
        """

        try: #get the data from database and put it in pandas-dataframe
            output = pd.read_sql_query(f"SELECT * from '{table_name}'", cls.conn, index_col='index') 
            logging.info(f"Load {table_name} from DataBase")
            
        except : #if data not available, return None
            logging.error(f'ERROR: {table_name}, not found in {cls.database_file}')
            return None

        return output

    @classmethod
    def DropTable(cls, table_name_prefix): 
        """table_name=NASDAQ-AAPL"""

        table_name_suffix = ['/Income-Statement', '/Balance-Sheet', '/Cashflow-Statement', '/Ratios', '/Company-Data']
        #Connecting to sqlite

        #Droping  table if already exists
        for i in range(0,len(table_name_suffix)):
            try:
                cls.cursor.execute(f"DROP TABLE '{table_name_prefix + table_name_suffix[i]}'")
                logging.info(f"Table {table_name_prefix + table_name_suffix[i]} dropped... ")
            except sqlite3.OperationalError:
                logging.error(f' Error removing {table_name_prefix + table_name_suffix[i]}. Table is probably not availabe in the database!')

    @classmethod
    def ListAllTables(cls):
        cls.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        output_temp = cls.cursor.fetchall()
        output = []
        for item in output_temp:
            output.append(item[0])

        return(output)
    
    @classmethod
    def ListTableRows(cls, table_name):
        cls.cursor.execute(f"SELECT * FROM '{table_name}'")
        output = cls.cursor.fetchall()
        return output

    @classmethod
    def ListRowByName(cls, row_name, table_name):
        cls.cursor.execute(f'SELECT * FROM "{table_name}" WHERE "index"="{row_name}"')
        output = cls.cursor.fetchone()
        return output

    @classmethod
    def ListByColumnName(cls, column_name, table_name):
        cls.cursor.execute(f'SELECT "{column_name}" FROM "{table_name}"')
        output = cls.cursor.fetchall()
        return output

    @classmethod
    def ListIndexColumn(cls, table_name):
        output = cls.ListByColumnName(column_name="index", table_name=table_name)
        return output

    @classmethod
    def GetTableShema(cls,table_name):
        cls.cursor.execute(f'PRAGMA table_info("{table_name}")')
        output = cls.cursor.fetchall()
        return output

    @classmethod
    def RenameColumn(cls, col_old_name, col_new_name, table_name):
        cls.cursor.execute(f'ALTER TABLE "{table_name}" RENAME COLUMN "{col_old_name}" TO "{col_new_name}"')

    @classmethod
    def RenameTable(cls, table_name_old, table_name_new):
        cls.cursor.execute(f'ALTER TABLE "{table_name_old}" RENAME TO "{table_name_new}"')

    @classmethod
    def UpdateValue(cls,table_name, col_to_update, new_value, search_col, search_value):
        cls.cursor.execute(f'UPDATE "{table_name}" SET "{col_to_update}"="{new_value}" WHERE "{search_col}"="{search_value}"')
        #UPDATE "ARCA-BATL/Company-Data" SET "value"="1234567" WHERE "index" = "company_data_url"

    @classmethod
    def DeleteAllRowsFromTable(cls,table_name):        
        cls.cursor.execute(f'DELETE FROM "{table_name}"')

    @classmethod
    def InsertRows(cls, table_name, columns_tuple, values_tuple):
        cls.cursor.execute(f'INSERT INTO "{table_name}" {columns_tuple} VALUES {values_tuple}')
        # INSERT INTO "ARCA-BATL/Company-Data" ("index", "value") VALUES ("1", "2")
    
    @classmethod
    def Test(cls):
        print("DataBase class is working")

    def GetFromDataBase(self, company_url):
        #get financial data from DataBase
        self.income_statement = __class__.ReadFromDatabase(table_name= company_url + "/Income-Statement") #attempt to get the data from database
        self.balanse_sheet = __class__.ReadFromDatabase(table_name= company_url + "/Balance-Sheet") #attempt to get the data from database
        self.cashflow_statement = __class__.ReadFromDatabase(table_name= company_url + "/Cashflow-Statement") #attempt to get the data from database
        self.statistics = __class__.ReadFromDatabase(table_name= company_url + "/Ratios") #attempt to get the data from database
        self.dividents = __class__.ReadFromDatabase(table_name= company_url + "/Dividents") #attempt to get the data from database
        self.company_data = __class__.ReadFromDatabase(table_name= company_url + "/Company-Data") #attempt to get the data from database

        if self.company_data is not None:
            self.company_name = self.company_data.loc['company_name'][0]
            self.company_ticker = self.company_data.loc['company_ticker'][0]
            self.company_url = self.company_data.loc['company_url'][0]
            
class Excel(): #static class for exporting Excel files 
    
    #class variables
    wb = None #excel workbook 
    sht = None #excel sheet
    height = None #height of the inserted visual
    width = None #width of the inserted visual

    insert_row = None #cell-row where visual will be inserted, ex, 1,2,3,4
    insert_col = None #cell-col when visual will be inserted, ex. A,B,C,D

    @classmethod
    def start(cls, name="Income Statement", height=375, width=550, insert_row=1, insert_col='A'): #innitite class
        # Create an empty workbook & rename sheet
        cls.wb = xw.Book() #start Excel
        cls.sht = cls.wb.sheets[0] #crete sheet 
        cls.sht.name = name #set sheet name

        cls.height = height #height of the inserted visual
        cls.width = width #width of the inserted visual

        cls.insert_row = insert_row #default insert cell-row
        cls.insert_col = insert_col #default insert cell-column

        # Create output directory
        OUTPUT_DIR = Path.cwd() / 'Output'
        OUTPUT_DIR.mkdir(exist_ok=True)

    # Helper function to insert 'Headings' into Excel cells
    @classmethod
    def insert_heading(cls, cell_row, cell_col, text):
        
        cell = cell_row + cell_col
        rng = cls.sht.range(cell)
        rng.value = text
        rng.font.bold = True
        rng.font.size = 24
        rng.font.color = (0, 0, 139)

    @classmethod
    def insert_visual(cls, fig, name):

        cell = cls.insert_col + str(cls.insert_row) #calculate the cell where the visual will be inserted
        logging.info(cell)

        cls.sht.pictures.add(fig,
                                name = name,
                                update = True,
                                left = cls.sht.range(cell).left,
                                top = cls.sht.range(cell).top,
                                height = cls.height,
                                width = cls.width)

        cls.insert_row = cls.insert_row + 25 #increase row-number to offset the next visual
        logging.info(cls.insert_row)
    
    @classmethod
    def close(cls):
        cls.wb.save(cls.OUTPUT_DIR / "PythonCharts.xlsx")
        if len(cls.wb.app.books) == 1:
            cls.wb.app.quit()
        else:
            cls.wb.close()

class Helper():

    def generateClassVariables(self, company_statement):
        """ Generate Income Statement / Balance Sheet / Cashflow Statement / Statistics variables """

        self.items = company_statement.transpose()
        # self.item_keys = []

        for item in self.items:
            item_temp = item
            item_temp = item_temp.lower()
            item_temp = item_temp.replace(' - ', '_')
            item_temp = item_temp.replace(' – ', '_')
            item_temp = item_temp.replace('-', '_')
            item_temp = item_temp.replace(' ', '_')
            item_temp = item_temp.replace("'", '')
            item_temp = item_temp.replace('"', '')
            item_temp = item_temp.replace('(', '')
            item_temp = item_temp.replace(')', '')
            item_temp = item_temp.replace('&', 'and')
            item_temp = item_temp.replace('.', '')
            item_temp = item_temp.replace(',', '')
            item_temp = item_temp.replace('/', '_')
            item_temp = item_temp.replace('%', 'percent')
            print(f'self.{item_temp}_str = "{item}"')
            # self.item_keys.append(item_temp)

        # self.res = {}
        # for key in self.item_keys:
        #     for value in self.items:
        #         self.res[key] = value
        #         self.items.remove(value)
        #         break


        # print(self.res)
    # helper = Helper()
    # helper.generateClassVariables(companies[0].statistics)

class ScrapeTrendingView():

    maximum_number_of_colapsed_rows = 50

    def __init__(self, company_url):
        """
        company_url = Exchange-Ticker \n
        company_url = NASDAQ-AAPL \n
        """

        # innitialize and set chrome-webdriver options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        # self.chrome_options.add_argument("--window-size=1000,1080")
        # chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome("G:\My Drive\Investing\Programming\chromedriver.exe", options=chrome_options)
        self.driver.implicitly_wait(2)
        self.time_sleep = 2
        # self.driver.maximize_window()

        # self.scrapeIncomeStatement(company_url=company_url) #start Income-Statement scraping
        # self.scrapeBalanceSheet(company_url=company_url) #start Balance-Sheet scraping
        # self.scrapeCashFlow(company_url=company_url) #start Cashflow-Statement scraping
        # self.scrapeStatistics(company_url=company_url) #start Ratios scraping
        self.scrapeDividents(company_url=company_url) #start Dividents scraping
        # self.scrapeCompanyData(company_url = company_url) #start Company-Data scraping

        #add additional data to dataframe
        # self.companyData_to_dataframe()

        self.driver.close()

    def scrapeIncomeStatement(self, company_url):

        self.income_statement_url = "https://www.tradingview.com/symbols/" + \
            company_url + "/financials-income-statement/?selected="

        self.driver.get(self.income_statement_url)
        time.sleep(self.time_sleep)

        self.switch_annual_data()
        self.close_cookies_popup()
        self.wait_page_to_load()

        # expand income-statement collapsed rows
        i = 0
        while True:
            i = i+1
            if i > __class__.maximum_number_of_colapsed_rows:
                logging.error(f'Break While loop i={i}')
                break
            try:
                expand_arrow_xpath = "//span[@class='arrow-_PBNXQ7k']"
                expand_arrow_element = self.driver.find_element_by_xpath(
                    expand_arrow_xpath)
                # self.driver.execute_script("arguments[0].scrollIntoView();", expand_arrow_element) #scroll view to element

                expand_arrow_element.click()
                # print(expand_arrow_element.if_exists)

            except:
                break

        # scrape the data
        output = self.scrape_the_data()

        self.income_statement = self.scraped_data_to_dataframe(output=output)

    def scrapeBalanceSheet(self, company_url):
        logging.info('Start Balance Sheet Scrape')
        self.balanse_sheet_url = "https://www.tradingview.com/symbols/" + \
            company_url + "/financials-balance-sheet/?selected="
        self.driver.get(self.balanse_sheet_url)
        time.sleep(self.time_sleep)

        self.switch_annual_data()
        self.wait_page_to_load()
        # self.close_cookies_popup()

        # expand balance-sheet collapsed-rows level-1
        i = 0
        while True:
            # logging.info('Start Expanding Balance Sheet Rows Level-1')
            i = i+1
            if i > __class__.maximum_number_of_colapsed_rows:
                logging.error(f'Break While loop i={i}')
                break
            try:
                # expand_arrow_xpath = "//span[@class='arrow-_PBNXQ7k']"
                expand_arrow_xpath = "//span[@class='arrow-_PBNXQ7k hasChanges-_PBNXQ7k']"
                expand_arrow_element = self.driver.find_element_by_xpath(
                    expand_arrow_xpath)
                # self.driver.execute_script("arguments[0].scrollIntoView();", expand_arrow_element) #scroll view to element

                expand_arrow_element.click()
                # print(expand_arrow_element.if_exists)

            except:
                # logging.info('End Expanding Balance Sheet Rows Level-1')
                break

         # expand balance-sheet collapsed-rows level-2
        i = 0
        while True:
            # logging.info('Start Expanding Balance Sheet Rows Level-2')
            i = i+1
            if i >  __class__.maximum_number_of_colapsed_rows:
                logging.error(f'Break While loop i={i}')
                break
            try:
                expand_arrow_xpath = "//span[@class='arrow-_PBNXQ7k']"
                expand_arrow_element = self.driver.find_element_by_xpath(
                    expand_arrow_xpath)
                # self.driver.execute_script("arguments[0].scrollIntoView();", expand_arrow_element) #scroll view to element

                expand_arrow_element.click()
                # print(expand_arrow_element.if_exists)

            except:
                # logging.info('End Expanding Balance Sheet Rows Level-2')
                break

        # scrape the data
        output = self.scrape_the_data()
        self.balanse_sheet = self.scraped_data_to_dataframe(output=output)

    def scrapeCashFlow(self, company_url):

        logging.info('Start CashFlow Scrape')
        self.cashflow_url = "https://www.tradingview.com/symbols/" + \
            company_url + "/financials-cash-flow/?selected="

        self.driver.get(self.cashflow_url)
        time.sleep(self.time_sleep)

        self.switch_annual_data()
        self.wait_page_to_load()
        # self.close_cookies_popup()

        # expand cash-flow collapsed-rows level-1
        i = 0
        while True:
            # logging.info('Start Expanding CashFlow Rows Level-1')
            i = i+1
            if i > 20:
                logging.info(f'Break While loop i={i}')
                break
            try:
                # expand_arrow_xpath = "//span[@class='arrow-_PBNXQ7k']"
                expand_arrow_xpath = "//span[@class='arrow-_PBNXQ7k hasChanges-_PBNXQ7k']"
                expand_arrow_element = self.driver.find_element_by_xpath(
                    expand_arrow_xpath)
                # self.driver.execute_script("arguments[0].scrollIntoView();", expand_arrow_element) #scroll view to element

                expand_arrow_element.click()
                # print(expand_arrow_element.if_exists)

            except:
                # logging.info('End Expanding CashFlow Rows Level-1')
                break

        # expand cash-flow collapsed-rows level-2
        i = 0
        while True:
            # logging.info('Start Expanding CashFlow Rows Level-2')
            i = i+1
            if i > 20:
                logging.info(f'Break While loop i={i}')
                break
            try:
                expand_arrow_xpath = "//span[@class='arrow-_PBNXQ7k']"
                expand_arrow_element = self.driver.find_element_by_xpath(
                    expand_arrow_xpath)
                # self.driver.execute_script("arguments[0].scrollIntoView();", expand_arrow_element) #scroll view to element

                expand_arrow_element.click()
                # print(expand_arrow_element.if_exists)

            except:
                # logging.info('End Expanding CashFlow Rows Level-2')
                break

        # scrape the data
        output = self.scrape_the_data()
        self.cashflow_statement = self.scraped_data_to_dataframe(output=output)

    def scrapeStatistics(self, company_url):
        logging.info('Start Statistics Scrape')
        self.statistics_url = "https://www.tradingview.com/symbols/" + company_url + "/financials-statistics-and-ratios/?selected="
        self.driver.get(self.statistics_url)
        time.sleep(self.time_sleep)

        # self.close_cookies_popup()
        self.switch_annual_data()
        self.wait_page_to_load()

        statistics_table_xpath = "//div[@class='container-YOfamMRP']/div"
        statistics_table_rows = self.driver.find_elements_by_xpath(
            statistics_table_xpath)

        # for item in financial_table[1]:
        #     print(item)

        # print(self.financial_table.text)
        # print(len(statistics_table_rows))
        output = []

        for item in statistics_table_rows:
            item_list = item.text.splitlines()
            output_temp = []

            # skip non-data items like Key stats, Profitability ratios, Liquidity ratios, Solvency ratios
            if len(item_list) == 1:
                continue
            else:
                for i in range(len(item_list)):

                    output_temp.append(item_list[i].replace(
                        '\u202a', '').replace('\u202c', ''))
                    # print(temp[i])

                # print(type(temp), len(temp))
                # print(temp)
                output.append(output_temp)

        # for item in output:
        #     print(len(item),item)
        #     pass

        self.statistics = self.scraped_data_to_dataframe(output=output)

    def scrapeDividents(self,company_url):
        logging.info('Start Dividents Scrape')
        self.dividents_url = "https://www.tradingview.com/symbols/" + company_url + "/financials-dividends/?selected="
        self.driver.get(self.dividents_url)
        time.sleep(self.time_sleep)

        # self.close_cookies_popup()
        self.wait_page_to_load()

        # scrape dividents
        try: #if dividents exists
            output = self.scrape_the_data()
            self.dividents = self.scraped_data_to_dataframe(output=output)

        except: #if dividents not exists, return none
             self.dividents = None

        print(self.dividents)
        

    def scrapeCompanyData(self, company_url):
        # self.company_data_url = "https://www.tradingview.com/symbols/" + company_url + "/forecast/"
        self.company_data_url = "https://www.tradingview.com/symbols/" + company_url + "/technicals/"

        self.driver.get(self.company_data_url)
        time.sleep(self.time_sleep)
        self.wait_page_to_load()

        self.company_url = company_url

        company_name_css = "h2[class='tv-symbol-header__first-line']"
        company_name_element = self.driver.find_element(By.CSS_SELECTOR, company_name_css)
        self.company_name = company_name_element.text
        # print(self.company_name)

        # company_ticker_css = "span[class='tv-symbol-header__second-line tv-symbol-header__second-line--with-hover js-symbol-dropdown'] span[class='tv-symbol-header__second-line--text']"
        company_ticker_css = '.tv-symbol-header__second-line--text'
        company_ticker_element = self.driver.find_element(By.CSS_SELECTOR, company_ticker_css)
        self.company_ticker = company_ticker_element.text
        # print(self.company_ticker)

        # exchage_css = "span[class='tv-symbol-header__second-line tv-symbol-header__second-line--with-hover js-symbol-dropdown'] span[class='tv-symbol-header__exchange']" #NASDAQ/NYSE
        # exchage_css = ".tv-symbol-header__exchange" #NASDAQ/NYSE
        # exchage_element = self.driver.find_element(By.CSS_SELECTOR, exchage_css)
        exchange_xpath = "//span[@class='tv-symbol-header__second-line tv-symbol-header__second-line--with-hover js-symbol-dropdown']/span[2]"
        exchage_element = self.driver.find_element(By.XPATH, exchange_xpath)
        self.exchange = exchage_element.text

    def companyData_to_dataframe(self):

        data = {'company_url':self.company_url,
                'income_statement_url': self.income_statement_url,
                'balanse_sheet_url': self.balanse_sheet_url,
                'cashflow_url': self.cashflow_url,
                'statistics_url': self.statistics_url,
                'company_data_url': self.company_data_url,
                'company_name':self.company_name,
                'company_ticker': self.company_ticker,
                "exchange": self.exchange}

        self.company_data = pd.DataFrame.from_dict(data, orient='index', columns=['value'])
        
    
    def close_cookies_popup(self):
        cookie_button_xpath = "//button[@class='acceptAll-WvyPjcpY button-OvB35Th_ size-xsmall-OvB35Th_ color-brand-OvB35Th_ variant-primary-OvB35Th_']"
        cookie_button_element = self.driver.find_element_by_xpath(
            cookie_button_xpath)
        cookie_button_element.click()

    def switch_annual_data(self):
        annual_button_xpath = "//button[@id='FY']"
        annual_button_element = self.driver.find_element_by_xpath(
            annual_button_xpath)
        annual_button_element.click()

    def scraped_data_to_dataframe(self, output):
        output_index = []
        output_values = []
        output_colums = output[0][1:]
        self.currency = output[0][0].replace('Currency: ', '')
        # print(self.currency)

        for i in range(1, len(output)):
            output_index.append(output[i][0])
            output_values.append(output[i][1:])

        # apply neccessery correction to fix the values-data
        output_values = self.fix_data_values(input_data=output_values)
        df = pd.DataFrame(output_values, columns=output_colums,
                          index=output_index)  # add scraped data to dataframe
        return df

    def scrape_the_data(self):

        # financial_table_xpath = "//div[@class='container-YOfamMRP']"
        financial_table_xpath = "//div[@class='container-YOfamMRP']/div"
        financial_table_rows = self.driver.find_elements_by_xpath(
            financial_table_xpath)
        # print(len(financial_table_rows))

        output = []
        number_of_periods = len(financial_table_rows[0].text.splitlines())

        for item in financial_table_rows:
            item_list = item.text.splitlines()
            output_temp = []

            if len(item_list) == number_of_periods:  # rows without YOY-grow

                for i in range(len(item_list)):
                    output_temp.append(item_list[i].replace(
                        '\u202a', '').replace('\u202c', ''))
            else:  # rows with YOY-grow
                if 'YoY growth' in item_list:  # Quarterly
                    for i in range(0, len(item_list), 2):  # skip YOY-grow row
                        output_temp.append(item_list[i].replace(
                            '\u202a', '').replace('\u202c', ''))
                else:  # Anual report
                    output_temp.append(item_list[0])
                    for i in range(1, len(item_list), 2):  # skip YOY-grow row
                        output_temp.append(item_list[i].replace(
                            '\u202a', '').replace('\u202c', ''))

            output.append(output_temp)

        return output


    def fix_data_values(self, input_data):
        output = []

        for row in input_data:
            output_row = []
            for item in row:
                # print(f'item={item}')

                if '−' in item:  # convert minus sign to real minus, for some reason the sign is not recognized as minus
                    item = item.replace('−', '-')

                if 'T' in item:  # convert Trillion-values to numeric
                    item = item.replace('T', '')
                    item = float(item)
                    item = item*1000000000000
                    # item = int(item)

                elif 'B' in item:  # convert Billion-values to numeric
                    item = item.replace('B', '')
                    item = float(item)
                    item = item*1000000000
                    # item = int(item)

                elif 'M' in item:  # convert Milion-values to numeric
                    item = item.replace('M', '')
                    item = float(item)
                    item = item*1000000
                    # item = int(item)

                elif 'K' in item:  # convert Thousants-values to numeric
                    item = item.replace('K', '')
                    item = float(item)
                    item = item*1000
                    # item = int(item)

                if isinstance(item, str):  # if item is not integer (0.00, ---, -)

                    if '—' in item:  # set value to None
                        item = None

                    elif '.' in item:  # convert value to float
                        item = float(item)

                if self.currency != 'USD':  # convert values to USD

                    if self.currency == 'KRW':
                        self.multiplier = 0.000700680009950

                    # check if item is int or float
                    if isinstance(item, float) or isinstance(item, int):
                        item = item*self.multiplier

                output_row.append(item)

            output.append(output_row)

        return output

    def wait_page_to_load(self):
        """wait the page to be fully loaded before proceeding with the scraping procedures"""

        price_css = "div[class='tv-symbol-price-quote__value js-symbol-last']"
        price_element = self.driver.find_element(By.CSS_SELECTOR, price_css)

        currency_symbol_css = ".tv-symbol-price-quote__currency.js-symbol-currency"
        currency_symbol_element = self.driver.find_element(By.CSS_SELECTOR, currency_symbol_css)

        prince_increase_css = ".js-symbol-change.tv-symbol-price-quote__change-value"
        prince_increase_element = self.driver.find_element(By.CSS_SELECTOR, prince_increase_css)

        prince_increase_percent_css = ".js-symbol-change-pt.tv-symbol-price-quote__change-value"
        prince_increase_percent_element = self.driver.find_element(By.CSS_SELECTOR, prince_increase_percent_css)

class GetCompanyData():
    """ Get company data first from DataBase and if not available Scrape it from website """
    companies = []

    @classmethod
    def get_data(cls, companies_urls):
        DataBase.Start() #Connect to DataBase 
        urls_not_in_database = [] #collect urls not found in database
        cls.companies = [] #reset companies variable 

        #run get-company-data process on separate threads
        for url in companies_urls:
            #get the data from DataBase
            company_data = DataBase()
            company_data.GetFromDataBase(company_url=url)

            #if data is not loaded from Database
            if company_data.income_statement is None or \
                company_data.balanse_sheet is None or \
                company_data.cashflow_statement is None or \
                company_data.statistics is None or \
                company_data.company_data is None:
                
                #collect companies that needs to be scraped for the website
                urls_not_in_database.append(url)
            
            #if data loaded from DataBase
            else:
                cls.companies.append(company_data)
        
        #get the data from the website
        if urls_not_in_database: #if not empty

            #start website scraping in separate threads 
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = [executor.submit(cls.run_in_separate_thread, url) for url in urls_not_in_database ]
                
                #when webscraping is completed
                for item in concurrent.futures.as_completed(results):
                    company_data = item.result()
                    print(">"*50, type(company_data))
                    cls.companies.append(company_data)
                    DataBase.AddToDatabase(data=company_data)

        
        DataBase.Stop() #Disconnect Database 
        return cls.companies #return company-data

    @classmethod
    def run_in_separate_thread(cls, url):
        company_data = ScrapeTrendingView(company_url=url)
        return(company_data)


class IncomeStatementVisualizer():
    
    def __init__(self, company_data):

        self.company_name = company_data.company_data.loc['company_name'][0] #get company_name from the dataframe
        self.df_income_statement = company_data.income_statement.transpose()
        self.income_statement_vars()
    
    def income_statement_vars(self):

        self.total_revenue_str = "Total revenue"
        self.cost_of_goods_sold_str = "Cost of goods sold"
        self.deprecation_and_amortization_str = "Deprecation and amortization"
        self.depreciation_str = "Depreciation"
        self.amortization_of_intangibles_str = "Amortization of intangibles"
        self.amortization_of_deferred_charges_str = "Amortization of deferred charges"
        self.other_cost_of_goods_sold_str = "Other cost of goods sold"
        self.gross_profit_str = "Gross profit"
        self.operating_expenses_excl_cogs_str = "Operating expenses (excl. COGS)"
        self.selling_general_admin_expenses_total_str = "Selling/general/admin expenses, total"
        self.research_and_development_str = "Research & development"
        self.selling_general_admin_expenses_other_str = "Selling/general/admin expenses, other"
        self.other_operating_expenses_total_str = "Other operating expenses, total"
        self.operating_income_str = "Operating income"
        self.non_operating_income_total_str = "Non-operating income, total"
        self.interest_expense_net_of_interest_capitalized_str = "Interest expense, net of interest capitalized"
        self.interest_expense_on_debt_str = "Interest expense on debt"
        self.interest_capitalized_str = "Interest capitalized"
        self.non_operating_income_excl_interest_expenses_str = "Non-operating income, excl. interest expenses"
        self.non_operating_interest_income_str = "Non-operating interest income"
        self.pretax_equity_in_earnings_str = "Pretax equity in earnings"
        self.miscellaneous_non_operating_expense_str = "Miscellaneous non-operating expense"
        self.unusual_income_expense_str = "Unusual income/expense"
        self.impairments_str = "Impairments"
        self.restructuring_charge_str = "Restructuring charge"
        self.legal_claim_expense_str = "Legal claim expense"
        self.unrealized_gain_loss_str = "Unrealized gain/loss"
        self.other_exceptional_charges_str = "Other exceptional charges"
        self.pretax_income_str = "Pretax income"
        self.equity_in_earnings_str = "Equity in earnings"
        self.taxes_str = "Taxes"
        self.income_tax_current_str = "Income tax, current"
        self.income_tax_current_domestic_str = "Income tax, current - domestic"
        self.income_tax_current_foreign_str = "Income Tax, current - foreign"
        self.income_tax_deferred_str = "Income tax, deferred"
        self.income_tax_deferred_domestic_str = "Income tax, deferred - domestic"
        self.income_tax_deferred_foreign_str = "Income tax, deferred - foreign"
        self.income_tax_credits_str = "Income Tax Credits"
        self.non_controlling_minority_interest_str = "Non-controlling/minority interest"
        self.after_tax_other_income_expense_str = "After tax other income/expense"
        self.net_income_before_discontinued_operations_str = "Net income before discontinued operations"
        self.discontinued_operations_str = "Discontinued operations"
        self.net_income_str = "Net income"
        self.dilution_adjustment_str = "Dilution adjustment"
        self.preferred_dividends_str = "Preferred dividends"
        self.diluted_net_income_available_to_common_stockholders_str = "Diluted net income available to common stockholders"
        self.basic_earnings_per_share_basic_eps_str = "Basic earnings per share (Basic EPS)"
        self.diluted_earnings_per_share_diluted_eps_str = "Diluted earnings per share (Diluted EPS)"
        self.average_basic_shares_outstanding_str = "Average basic shares outstanding"
        self.diluted_shares_outstanding_str = "Diluted shares outstanding"
        self.ebitda_str = "EBITDA"
        self.ebit_str = "EBIT"
        self.total_operating_expenses_str = "Total operating expenses"

    def show_all_visuals(self):
        self.revenue()
        self.operating_income()
        self.pretax_income()
        self.discontinued_operations()
        self.net_income()
        self.diluted_net_income()
        self.eps()
        self.shares()
        self.ebit()
        self.operating_expenses()

    def revenue(self):
        params = ['Total revenue', 'Cost of goods sold', 'Gross profit']
        title = 'Total Revenue - Cost Of Goods Sold = Gross Profit'
        self.graph_template(y_axis_data=params, graph_title=title)

    def operating_income(self):
        params = ['Operating expenses (excl. COGS)', 'Operating income', 'Gross profit']
        title = 'Gross Profit - Operating Expenses = Operating Income'
        self.graph_template(y_axis_data=params, graph_title=title)

    def pretax_income(self):
        params = ['Operating income', 'Non-operating income, total', 'Pretax income']
        title = 'Operating Income + Non Operating Income = Pretax Income'
        self.graph_template(y_axis_data=params, graph_title=title)

    def discontinued_operations(self):
        params = ['Non-controlling/minority interest', 'After tax other income/expense', 'Net income before discontinued operations', 'Discontinued operations']
        title = 'Net income before discontinued operations'
        self.graph_template(y_axis_data=params, graph_title=title)

    def net_income(self):
        params = ['Pretax income', 'Taxes', 'Net income']
        title = 'Pretax Income - Taxes = Net Income'
        self.graph_template(y_axis_data=params, graph_title=title)

    def diluted_net_income(self):
        params = ['Dilution adjustment', 'Preferred dividends', 'Diluted net income available to common stockholders']
        title = 'Net Income + Dilution Adjustment - Preferred Dividents = Diluted Net Income'
        self.graph_template(y_axis_data=params, graph_title=title)

    def eps(self):
        params = ['Basic earnings per share (Basic EPS)', 'Diluted earnings per share (Diluted EPS)']
        title = 'Earnings Per Share'
        self.graph_template(y_axis_data=params, graph_title=title)

    def shares(self):
        params = ['Average basic shares outstanding', 'Diluted shares outstanding']
        title = 'Shares Outstanding'
        self.graph_template(y_axis_data=params, graph_title=title)

    def ebit(self):
        params = ['EBITDA', 'EBIT']
        title = 'EBIT/EBITDA'
        self.graph_template(y_axis_data=params, graph_title=title)

    def operating_expenses(self):
        params = ['Operating expenses (excl. COGS)', 'Cost of goods sold', 'Total operating expenses']
        title = 'Operating Expenses + Cost of Goods Sold = Total Operating Expenses'
        self.graph_template(y_axis_data=params, graph_title=title)

    def graph_template(self, y_axis_data, graph_title):
        """
        y_axis_list=['Total revenue', 'Cost of goods sold', 'Gross profit'] 
        graph_title= f'{self.company_name} | Total Revenue - Cost Of Goods Sold = Gross Profit'
        """

        fig = px.line(self.df_income_statement,
                        x = self.df_income_statement.index, 
                        y = y_axis_data,
                        title = f'{self.company_name} | {graph_title}',
                        markers = True)
        fig.show()

class BalanceSheetVisualizer():

    def __init__(self, company_data):
        
        self.company_name = company_data.company_data.loc['company_name'][0] #get company_name from the dataframe
        self.df_balanse_sheet = company_data.balanse_sheet.transpose()
        self.balanse_sheet_vars()
    
    def balanse_sheet_vars(self):

        self.total_assets_str = "Total assets"
        self.total_current_assets_str = "Total current assets"
        self.cash_and_short_term_investments_str = "Cash and short term investments"
        self.cash_and_equivalents_str = "Cash & equivalents"
        self.short_term_investments_str = "Short term investments"
        self.total_receivables_net_str = "Total receivables, net"
        self.accounts_receivable_trade_net_str = "Accounts receivable - trade, net"
        self.accounts_receivables_gross_str = "Accounts receivables, gross"
        self.bad_debt___doubtful_accounts_str = "Bad debt / Doubtful accounts"
        self.other_receivables_str = "Other receivables"
        self.total_inventory_str = "Total inventory"
        self.inventories_work_in_progress_str = "Inventories - work in progress"
        self.inventories_progress_payments_and_other_str = "Inventories - progress payments & other"
        self.inventories_finished_goods_str = "Inventories - finished goods"
        self.inventories_raw_materials_str = "Inventories - raw materials"
        self.prepaid_expenses_str = "Prepaid expenses"
        self.other_current_assets_total_str = "Other current assets, total"
        self.total_non_current_assets_str = "Total non-current assets"
        self.long_term_investments_str = "Long term investments"
        self.note_receivable_long_term_str = "Note receivable - long term"
        self.investments_in_unconsolidated_subsidiaries_str = "Investments in unconsolidated subsidiaries"
        self.other_investments_str = "Other investments"
        self.net_property_plant_equipment_str = "Net property/plant/equipment"
        self.gross_property_plant_equipment_str = "Gross property/plant/equipment"
        self.property_plant_equipment_buildings_str = "Property/plant/equipment - Buildings"
        self.property_plant_equipment_construction_in_progress_str = "Property/plant/equipment - Construction in progress"
        self.property_plant_equipment_machinery_and_equipment_str = "Property/plant/equipment - Machinery & equipment"
        self.property_plant_equipment_land_and_improvement_str = "Property/plant/equipment - Land & improvement"
        self.property_plant_equipment_leased_property_str = "Property/plant/equipment - Leased property"
        self.property_plant_equipment_leases_str = "Property/plant/equipment - Leases"
        self.property_plant_equipment_computer_software_and_equipment_str = "Property/plant/equipment - Computer software and equipment"
        self.property_plant_equipment_transportation_equipment_str = "Property/plant/equipment - Transportation equipment"
        self.property_plant_equipment_other_str = "Property/plant/equipment - Other"
        self.accumulated_depreciation_total_str = "Accumulated depreciation, total"
        self.accumulated_depreciation_buildings_str = "Accumulated depreciation - Buildings"
        self.accumulated_depreciation_construction_in_progress_str = "Accumulated depreciation - Construction in progress"
        self.accumulated_depreciation_machinery_and_equipment_str = "Accumulated depreciation - Machinery & equipment"
        self.accumulated_depreciation_land_and_improvement_str = "Accumulated depreciation - Land & improvement"
        self.accumulated_depreciation_leased_property_str = "Accumulated depreciation - Leased property"
        self.accumulated_depreciation_leases_str = "Accumulated depreciation - Leases"
        self.accumulated_depreciation_computer_software_and_equipment_str = "Accumulated depreciation - Computer software and equipment"
        self.accumulated_depreciation_transportation_equipment_str = "Accumulated depreciation - Transportation equipment"
        self.accumulated_depreciation_other_str = "Accumulated depreciation - Other"
        self.deferred_tax_assets_str = "Deferred tax assets"
        self.net_intangible_assets_str = "Net intangible assets"
        self.goodwill_net_str = "Goodwill, net"
        self.goodwill_gross_str = "Goodwill, gross"
        self.accumulated_goodwill_amortization_str = "Accumulated goodwill amortization"
        self.other_intangibles_net_str = "Other intangibles, net"
        self.other_intangibles_gross_str = "Other intangibles, gross"
        self.accumulated_amortization_of_other_intangibles_str = "Accumulated amortization of other intangibles"
        self.deferred_charges_str = "Deferred charges"
        self.other_long_term_assets_total_str = "Other long term assets, total"
        self.total_liabilities_str = "Total liabilities"
        self.total_current_liabilities_str = "Total current liabilities"
        self.short_term_debt_str = "Short term debt"
        self.current_portion_of_lt_debt_and_capital_leases_str = "Current portion of LT debt and capital leases"
        self.short_term_debt_excl_current_portion_of_lt_debt_str = "Short term debt excl. current portion of LT debt"
        self.notes_payable_str = "Notes payable"
        self.other_short_term_debt_str = "Other short term debt"
        self.accounts_payable_str = "Accounts payable"
        self.income_tax_payable_str = "Income tax payable"
        self.dividends_payable_str = "Dividends payable"
        self.accrued_payroll_str = "Accrued payroll"
        self.deferred_income_current_str = "Deferred income, current"
        self.other_current_liabilities_str = "Other current liabilities"
        self.total_non_current_liabilities_str = "Total non-current liabilities"
        self.long_term_debt_str = "Long term debt"
        self.long_term_debt_excl_lease_liabilities_str = "Long term debt excl. lease liabilities"
        self.capital_and_operating_lease_obligations_str = "Capital and operating lease obligations"
        self.capitalized_lease_obligations_str = "Capitalized lease obligations"
        self.operating_lease_liabilities_str = "Operating lease liabilities"
        self.provision_for_risks_and_charge_str = "Provision for risks & charge"
        self.deferred_tax_liabilities_str = "Deferred tax liabilities"
        self.deferred_income_non_current_str = "Deferred income, non-current"
        self.other_non_current_liabilities_total_str = "Other non-current liabilities, total"
        self.total_equity_str = "Total equity"
        self.shareholders_equity_str = "Shareholders' equity"
        self.common_equity_total_str = "Common equity, total"
        self.retained_earnings_str = "Retained earnings"
        self.paid_in_capital_str = "Paid in capital"
        self.common_stock_par_carrying_value_str = "Common stock par/Carrying value"
        self.additional_paid_in_capital_capital_surplus_str = "Additional paid-in capital/Capital surplus"
        self.treasury_stock_common_str = "Treasury stock - common"
        self.other_common_equity_str = "Other common equity"
        self.preferred_stock_carrying_value_str = "Preferred stock, carrying value"
        self.minority_interest_str = "Minority interest"
        self.total_liabilities_and_shareholders_equities_str = "Total liabilities & shareholders' equities"
        self.total_debt_str = "Total debt"
        self.net_debt_str = "Net debt"
        self.book_value_per_share_str = "Book value per share"

    def show_all_visuals(self):
        self.total_assets_liabilities_equity()
        self.current_non_current_assets()
        self.current_non_current_liabilities()
        self.total_debt_net_debt()
        self.book_value_per_share()


    def total_assets_liabilities_equity(self):
        params = ['Total assets', 'Total liabilities', 'Total equity',  "Total liabilities & shareholders' equities"]
        title = 'Total Assets/Liabilities/Equity'
        self.graph_template(y_axis_data=params, graph_title=title)
        

    def current_non_current_assets(self):
        params = ['Total current assets', 'Total non-current assets']
        title = 'Total Current/Non-Current Assets'
        self.graph_template(y_axis_data=params, graph_title=title)

    def current_non_current_liabilities(self):    
        params = ['Total current liabilities', 'Total non-current liabilities']
        title = 'Total Current/Non-Current Liabilities'
        self.graph_template(y_axis_data=params, graph_title=title)

    def total_debt_net_debt(self):    
        params = ['Total debt', 'Net debt']
        title = 'Total/Net Debt'
        self.graph_template(y_axis_data=params, graph_title=title)

    def book_value_per_share(self):    
        params = ['Book value per share']
        title = 'Book Value Per Share'
        self.graph_template(y_axis_data=params, graph_title=title)
    
    def graph_template(self, y_axis_data, graph_title):
        """
        y_axis_list=['Total revenue', 'Cost of goods sold', 'Gross profit'] 
        graph_title= f'{self.company_name} | Total Revenue - Cost Of Goods Sold = Gross Profit'
        """
        fig = px.line(self.df_balanse_sheet,
                        x = self.df_balanse_sheet.index, 
                        y = y_axis_data,
                        title = f'{self.company_name} | {graph_title}',
                        markers = True)
        fig.show()

class CashflowStatementVisualizer():

    def __init__(self, company_data):

        self.company_name = company_data.company_data.loc['company_name'][0] #get company_name from the dataframe
        self.df_cashflow_statement = company_data.cashflow_statement.transpose()
        self.cashflow_statement_vars()
    
    def cashflow_statement_vars(self):

        self.cash_from_operating_activities_str = "Cash from operating activities"
        self.funds_from_operations_str = "Funds from operations"
        self.net_income_cash_flow_str = "Net income (cash flow)"
        self.depreciation_and_amortization_cash_flow_str = "Depreciation & amortization (cash flow)"
        self.depreciation_depletion_str = "Depreciation/depletion"
        self.amortization_str = "Amortization"
        self.deferred_taxes_cash_flow_str = "Deferred taxes (cash flow)"
        self.non_cash_items_str = "Non-cash items"
        self.changes_in_working_capital_str = "Changes in working capital"
        self.change_in_accounts_receivable_str = "Change in accounts receivable"
        self.change_in_taxes_payable_str = "Change in taxes payable"
        self.change_in_accounts_payable_str = "Change in accounts payable"
        self.change_in_accrued_expenses_str = "Change in accrued expenses"
        self.change_in_inventories_str = "Change in inventories"
        self.change_in_other_assets_liabilities_str = "Change in other assets/liabilities"
        self.cash_from_investing_activities_str = "Cash from investing activities"
        self.purchase_sale_of_business_net_str = "Purchase/sale of business, net"
        self.sale_of_fixed_assets_and_businesses_str = "Sale of fixed assets & businesses"
        self.purchase_acquisition_of_business_str = "Purchase/acquisition of business"
        self.purchase_sale_of_investments_net_str = "Purchase/sale of investments, net"
        self.sale_maturity_of_investments_str = "Sale/maturity of investments"
        self.purchase_of_investments_str = "Purchase of investments"
        self.capital_expenditures_str = "Capital expenditures"
        self.capital_expenditures_fixed_assets_str = "Capital expenditures - fixed assets"
        self.capital_expenditures_other_assets_str = "Capital expenditures - other assets"
        self.other_investing_cash_flow_items_total_str = "Other investing cash flow items, total"
        self.investing_activities_other_sources_str = "Investing activities – other sources"
        self.investing_activities_other_uses_str = "Investing activities – other uses"
        self.cash_from_financing_activities_str = "Cash from financing activities"
        self.issuance_retirement_of_stock_net_str = "Issuance/retirement of stock, net"
        self.sale_of_common_and_preferred_stock_str = "Sale of common & preferred stock"
        self.repurchase_of_common_and_preferred_stock_str = "Repurchase of common & preferred stock"
        self.issuance_retirement_of_debt_net_str = "Issuance/retirement of debt, net"
        self.issuance_retirement_of_long_term_debt_str = "Issuance/retirement of long term debt"
        self.issuance_of_long_term_debt_str = "Issuance of long term debt"
        self.reduction_of_long_term_debt_str = "Reduction of long term debt"
        self.issuance_retirement_of_short_term_debt_str = "Issuance/retirement of short term debt"
        self.issuance_retirement_of_other_debt_str = "Issuance/retirement of other debt"
        self.total_cash_dividends_paid_str = "Total cash dividends paid"
        self.common_dividends_paid_str = "Common dividends paid"
        self.preferred_dividends_paid_str = "Preferred dividends paid"
        self.other_financing_cash_flow_items_total_str = "Other financing cash flow items, total"
        self.financing_activities_other_sources_str = "Financing activities – other sources"
        self.financing_activities_other_uses_str = "Financing activities – other uses"
        self.free_cash_flow_str = "Free cash flow"

    def show_all_visuals(self):
        self.cashflow_operating_investing_financial()
        self.cashflow_operating_activities()
        self.cashflow_investing_activities()
        self.cash_from_financing_activities()


    def cashflow_operating_investing_financial (self):
        # params = ['Cash from operating activities', 'Cash from investing activities','Cash from financing activities', 'Free cash flow']
        params = [self.cash_from_operating_activities_str,
                self.cash_from_investing_activities_str,
                self.cash_from_financing_activities_str,
                self.free_cash_flow_str]
        title = 'Cashflow From Operating/Investing/Financial Activities'
        self.graph_template(y_axis_data=params, graph_title=title)
        

    def cashflow_operating_activities(self):
        # params = ['Cash from operating activities', 'Funds from operations','Changes in working capital']
        params = [self.cash_from_operating_activities_str,
                self.funds_from_operations_str,
                self.changes_in_working_capital_str]
        title = 'Cash from operating activities + Funds from operations = Cashflow From Operating Activities'
        self.graph_template(y_axis_data=params, graph_title=title)

    def cashflow_investing_activities (self):
        # params = ['Cash from investing activities', 'Purchase/sale of business, net','Purchase/sale of investments, net', 'Capital expenditures', 'Other investing cash flow items, total']
        params = [ self.cash_from_investing_activities_str,
                self.purchase_sale_of_business_net_str,
                self.purchase_sale_of_investments_net_str,
                self.capital_expenditures_str,
                self.other_investing_cash_flow_items_total_str,]
        title = 'Purchase/sale of business + Purchase/sale of investments + Capital expenditures + Other investing cash flow items = Cash from investing activities'
        self.graph_template(y_axis_data=params, graph_title=title)


    def cash_from_financing_activities(self):
        params = [self.issuance_retirement_of_stock_net_str,
                    self.issuance_retirement_of_debt_net_str,
                    self.total_cash_dividends_paid_str,
                    self.other_financing_cash_flow_items_total_str]
        title =  '+'.join(params) + '= Cash from financial activities'
        self.graph_template(y_axis_data=params, graph_title=title)


    def graph_template(self, y_axis_data, graph_title):
            """
            y_axis_list=['Total revenue', 'Cost of goods sold', 'Gross profit'] 
            graph_title= f'{self.company_name} | Total Revenue - Cost Of Goods Sold = Gross Profit'
            """
            fig = px.line(self.df_cashflow_statement,
                            x = self.df_cashflow_statement.index, 
                            y = y_axis_data,
                            title = f'{self.company_name} | {graph_title}',
                            markers = True)

            fig.update_traces(
                mode="markers+lines", hovertemplate=None)
            fig.update_layout(
                hovermode="x", hoverlabel_namelength=-1, font=dict(size=10))
            fig.show()

class StatisticsRatiosVisualizer():

    def __init__(self, company_data):
        self.company_name = company_data.company_data.loc['company_name'][0] #get company_name from the dataframe
        self.df_statistics = company_data.statistics.transpose()
        self.statistics_ratios_vars()

    def statistics_ratios_vars(self):
        self.total_common_shares_outstanding_str = "Total common shares outstanding"
        self.float_shares_outstanding_str = "Float shares outstanding"
        self.number_of_employees_str = "Number of employees"
        self.number_of_shareholders_str = "Number of shareholders"
        self.price_to_earnings_ratio_str = "Price to earnings ratio"
        self.price_to_sales_ratio_str = "Price to sales ratio"
        self.price_to_cash_flow_ratio_str = "Price to cash flow ratio"
        self.price_to_book_ratio_str = "Price to book ratio"
        self.enterprise_value_str = "Enterprise value"
        self.enterprise_value_to_ebitda_ratio_str = "Enterprise value to EBITDA ratio"
        self.return_on_assets_percent_str = "Return on assets %"
        self.return_on_equity_percent_str = "Return on equity %"
        self.return_on_invested_capital_percent_str = "Return on invested capital %"
        self.gross_margin_percent_str = "Gross margin %"
        self.operating_margin_percent_str = "Operating margin %"
        self.ebitda_margin_percent_str = "EBITDA margin %"
        self.net_margin_percent_str = "Net margin %"
        self.quick_ratio_str = "Quick ratio"
        self.current_ratio_str = "Current ratio"
        self.inventory_turnover_str = "Inventory turnover"
        self.asset_turnover_str = "Asset turnover"
        self.debt_to_assets_ratio_str = "Debt to assets ratio"
        self.debt_to_equity_ratio_str = "Debt to equity ratio"
        self.long_term_debt_to_total_assets_ratio_str = "Long term debt to total assets ratio"

    def show_all_visuals(self):
        self.shares_outstanding()
        self.enterprice_values()
        self.numer_of_employees_shareholders()
        self.price_ratios()
        self.return_ratios()
        self.margins()
        self.dept_ratios()
        self.liquidity_ratios()

    def shares_outstanding(self):
        params = ['Total common shares outstanding', 'Float shares outstanding']
        title = 'Number of Shares'
        self.graph_template(y_axis_data=params, graph_title=title)
    
    def enterprice_values(self):
        params = ['Enterprise value']
        title = 'Enterprise value'
        self.graph_template(y_axis_data=params, graph_title=title)
    
    def numer_of_employees_shareholders(self):
        params = ['Number of employees', 'Number of shareholders']
        title = 'Number of employees/shareholders'
        self.graph_template(y_axis_data=params, graph_title=title)

    def price_ratios(self):
        params = ['Price to earnings ratio', 'Price to sales ratio', 'Price to cash flow ratio', 'Enterprise value to EBITDA ratio','Price to book ratio']
        title = 'Price Ratios'
        self.graph_template(y_axis_data=params, graph_title=title)

    def return_ratios(self):
        params = ['Return on assets %', 'Return on equity %', 'Return on invested capital %']
        title = 'Return Ratios'
        self.graph_template(y_axis_data=params, graph_title=title)

    def margins(self):
        params = ['Gross margin %', 'EBITDA margin %', 'Net margin %', 'Operating margin %']
        title = 'Margins'
        self.graph_template(y_axis_data=params, graph_title=title)

    def dept_ratios(self):
        params = ['Debt to assets ratio', 'Debt to equity ratio', 'Long term debt to total assets ratio']
        title = 'Dept Ratios'
        self.graph_template(y_axis_data=params, graph_title=title)

    def liquidity_ratios(self):
        params = ['Quick ratio', 'Current ratio', 'Inventory turnover', 'Asset turnover']
        title = 'Liquidity Ratios'
        self.graph_template(y_axis_data=params, graph_title=title)

    def graph_template(self, y_axis_data, graph_title):
            """
            y_axis_list=['Total revenue', 'Cost of goods sold', 'Gross profit'] 
            graph_title= f'{self.company_name} | Total Revenue - Cost Of Goods Sold = Gross Profit'
            """
            fig = px.line(self.df_statistics,
                            x = self.df_statistics.index, 
                            y = y_axis_data,
                            title = f'{self.company_name} | {graph_title}',
                            markers = True)

            fig.update_traces(
                mode="markers+lines", hovertemplate=None)
            fig.update_layout(
                hovermode="x", hoverlabel_namelength=-1)
            fig.show()

class CompareCompaniesVisualizer_old():

    def __init__(self, companies_data):
        self.companies_data = companies_data

        self.income_stat_params = IncomeStatementVisualizer(company_data=companies_data[0])
        self.balanse_sh_params = BalanceSheetVisualizer(company_data=companies_data[0])
        self.cashflow_params = CashflowStatementVisualizer(company_data=companies_data[0])
        self.statistics_params = StatisticsRatiosVisualizer(company_data=companies_data[0])

    def income_statement_visualizer(self, parameter_name):

        fig = go.Figure()

        for company in self.companies_data:

            columns = company.income_statement.columns
            rows = company.income_statement.loc[parameter_name]
            trace_name = f"{company.company_name}"# | {parameter_name}"
            fig = fig.add_trace(go.Scatter(x = columns, y= rows, name=trace_name))

        fig.update_xaxes(categoryorder='category ascending')  # sort X-axis (when X-axis of different companies contains different ranges i.e. 2015-2021, 2016-2022)
        fig.update_traces(mode="markers+lines", hovertemplate=None) #enable hover-mode, interactively display values on the graph when pointed with mouse
        fig.update_layout(hovermode="x", hoverlabel_namelength=-1,  title=parameter_name) #display the full parameter name

        fig.show()
                
        # Excel.insert_visual(fig=fig, name=parameter_name)
        # Excel.insert_visual(fig=fig, cell='A2', name=parameter_name )
    
    def balanse_sheet_visualizer(self, parameter_name):

        fig = go.Figure()

        for company in self.companies_data:

            columns = company.balanse_sheet.columns
            rows = company.balanse_sheet.loc[parameter_name]
            trace_name = f"{company.company_name}"# | {parameter_name}"
            fig = fig.add_trace(go.Scatter(x = columns, y= rows, name=trace_name))

        fig.update_xaxes(categoryorder='category ascending')  # sort X-axis (when X-axis of different companies contains different ranges i.e. 2015-2021, 2016-2022)
        fig.update_traces(mode="markers+lines", hovertemplate=None) #enable hover-mode, interactively display values on the graph when pointed with mouse
        fig.update_layout(hovermode="x", hoverlabel_namelength=-1,  title=parameter_name) #display the full parameter name

        fig.show()

    def cashflow_statement_visualizer(self, parameter_name):

        fig = go.Figure()

        for company in self.companies_data:

            columns = company.cashflow_statement.columns
            rows = company.cashflow_statement.loc[parameter_name]
            trace_name = f"{company.company_name}"# | {parameter_name}"
            fig = fig.add_trace(go.Scatter(x = columns, y= rows, name=trace_name))

        fig.update_xaxes(categoryorder='category ascending')  # sort X-axis (when X-axis of different companies contains different ranges i.e. 2015-2021, 2016-2022)
        fig.update_traces(mode="markers+lines", hovertemplate=None) #enable hover-mode, interactively display values on the graph when pointed with mouse
        fig.update_layout(hovermode="x", hoverlabel_namelength=-1,  title=parameter_name) #display the full parameter name

        fig.show()

    def statistics_ratios_visualizer(self, parameter_name):

        fig = go.Figure()

        for company in self.companies_data:
            columns = company.statistics.columns
            rows = company.statistics.loc[parameter_name]
            trace_name = f"{company.company_ticker} | {company.company_name}"# | {parameter_name}"
            fig = fig.add_trace(go.Scatter(x = columns, y= rows, name=trace_name))

        fig.update_xaxes(categoryorder='category ascending')  # sort X-axis (when X-axis of different companies contains different ranges i.e. 2015-2021, 2016-2022)

        fig.update_traces(mode="markers+lines", hovertemplate=None) #enable hover-mode, interactively display values on the graph when pointed with mouse
        fig.update_layout(hovermode="x", hoverlabel_namelength=-1,  title=parameter_name) #display the full parameter name

        fig.show()

    
    def statistics_ratios_subplots(self, parameter_name):

        fig = go.Figure()
        number_of_companies = len(self.companies_data)
        subplot_cols = 3
        subplot_rows = int(number_of_companies / subplot_cols) + (number_of_companies % subplot_cols > 0) #get integer rounded up
        subplot_titles = list(f'{company.company_ticker}|{company.company_name}' for company in self.companies_data) #get titles of subplots
        fig = make_subplots(rows=subplot_rows, cols=subplot_cols, subplot_titles=subplot_titles)
        fig_row = 1
        fig_col = 1

        for company in self.companies_data:
            columns = company.statistics.columns
            rows = company.statistics.loc[parameter_name]
            trace_name = f"{company.company_ticker} | {company.company_name}"# | {parameter_name}"
            fig = fig.add_trace(go.Scatter(x = columns, y= rows, name=trace_name), row=fig_row, col=fig_col)

            if fig_col < subplot_cols:
                fig_col = fig_col+1
            else:
                fig_col=1
                fig_row = fig_row + 1

        fig.update_xaxes(categoryorder='category ascending')  # sort X-axis (when X-axis of different companies contains different ranges i.e. 2015-2021, 2016-2022)

        fig.update_traces(mode="markers+lines", hovertemplate=None) #enable hover-mode, interactively display values on the graph when pointed with mouse
        fig.update_layout(hovermode="x", hoverlabel_namelength=-1,  title=parameter_name) #display the full parameter name
        fig.update_layout(height=300*subplot_rows) #update the subplot height
        fig.update_layout(showlegend=False) #update the subplot height

        fig.show()


    def average_parameter_value(self, parameter_name, top_companies = 15):
        companies_data = [] #collect company-data information, needed for export 
        companies_names = [] #collect copany-names, needed for visuals
        param_values = [] #collect average-value for respective parameter_name

        for company in self.companies_data:
            companies_data.append(company) #get company-data
            companies_names.append(f'{company.company_ticker} | {company.company_name}') #get company ticker and name
            param_values.append(company.statistics.loc[parameter_name].mean()) #get average-values of the respetive parameter

        
        data = pd.DataFrame(list(zip(param_values, companies_data)), index=companies_names, columns =[parameter_name, 'company_data']) #convert lists to pandas
        data.sort_values(by=[parameter_name], axis=0, ascending=False, inplace=True) #sort data by respective parameter_name
        data = data.head(top_companies) #keep the top Nth company only
        # print(data)
        
        data_for_visualizing = data.drop(columns='company_data') #remove company_data colums from dataframe, not need for visuals
        output = data['company_data'].to_list() #get the company_data only, needed for export
        fig = px.bar(data_for_visualizing, orientation='h') #create a bar-chart
        fig.update_yaxes(autorange="reversed") #reverse y-exis to match dataframe top-to-bottom order
        # # fig.update_layout(barmode='stack', yaxis={'categoryorder': 'total ascending'})

        print(data_for_visualizing)
        # fig.show()
        return output

class CompareCompaniesVisualizer():

    def __init__(self, companies_data):
        self.companies_data = companies_data

        self.income_stat_params = IncomeStatementVisualizer(company_data=companies_data[0])
        self.balanse_sh_params = BalanceSheetVisualizer(company_data=companies_data[0])
        self.cashflow_params = CashflowStatementVisualizer(company_data=companies_data[0])
        self.statistics_params = StatisticsRatiosVisualizer(company_data=companies_data[0])


    def income_statement_visualizer_new(self, parameter_name):
        self.singleplot(parameter_name=parameter_name, type='income_statement')

    def balanse_sheet_visualizer_new(self, parameter_name):
        self.singleplot(parameter_name=parameter_name, type='ballance_sheet')

    def cashflow_statement_visualizer_new(self, parameter_name):
        self.singleplot(parameter_name=parameter_name, type='cashflow_statement')

    def statistics_ratios_visualizer_new(self, parameter_name):
        self.singleplot(parameter_name=parameter_name, type='statistics_ratios')

    def singleplot(self, parameter_name, type):

        fig = go.Figure()

        for company in self.companies_data:

            if type == 'income_statement':
                columns = company.income_statement.columns
                rows = company.income_statement.loc[parameter_name]
            elif type == 'ballance_sheet':
                columns = company.balanse_sheet.columns
                rows = company.balanse_sheet.loc[parameter_name]
            elif type == 'cashflow_statement':
                columns = company.cashflow_statement.columns
                rows = company.cashflow_statement.loc[parameter_name]
            elif type == 'statistics_ratios':
                columns = company.statistics.columns
                rows = company.statistics.loc[parameter_name]

            trace_name = f"{company.company_ticker} | {company.company_name}"# | {parameter_name}"
            fig = fig.add_trace(go.Scatter(x = columns, y= rows, name=trace_name))

        fig.update_xaxes(categoryorder='category ascending')  # sort X-axis (when X-axis of different companies contains different ranges i.e. 2015-2021, 2016-2022)
        fig.update_traces(mode="markers+lines", hovertemplate=None) #enable hover-mode, interactively display values on the graph when pointed with mouse
        fig.update_layout(hovermode="x", hoverlabel_namelength=-1,  title=parameter_name) #display the full parameter name
        fig.show()

    ##################################################################################################
   
    def income_statement_subplots(self, parameter_name):
        self.subplots(parameter_name=parameter_name, type='income_statement')

    def ballance_sheet_subplots(self, parameter_name):
        self.subplots(parameter_name=parameter_name, type='ballance_sheet')

    def cashflow_statement_subplots(self, parameter_name):
        self.subplots(parameter_name=parameter_name, type='cashflow_statement')

    def statistics_ratios_subplots(self, parameter_name):
        self.subplots(parameter_name=parameter_name, type='statistics_ratios')

    def subplots(self, parameter_name, type):

        fig = go.Figure()
        number_of_companies = len(self.companies_data)
        subplot_cols = 3
        subplot_rows = int(number_of_companies / subplot_cols) + (number_of_companies % subplot_cols > 0) #get integer rounded up
        subplot_titles = list(f'{company.company_ticker}|{company.company_name}' for company in self.companies_data) #get titles of subplots
        fig = make_subplots(rows=subplot_rows, cols=subplot_cols, subplot_titles=subplot_titles)
        fig_row = 1
        fig_col = 1

        for company in self.companies_data:
            
            if type == 'income_statement':
                columns = company.income_statement.columns
                rows = company.income_statement.loc[parameter_name]
            elif type == 'ballance_sheet':
                columns = company.balanse_sheet.columns
                rows = company.balanse_sheet.loc[parameter_name]
            elif type == 'cashflow_statement':
                columns = company.cashflow_statement.columns
                rows = company.cashflow_statement.loc[parameter_name]
            elif type == 'statistics_ratios':
                columns = company.statistics.columns
                rows = company.statistics.loc[parameter_name]


            trace_name = f"{company.company_ticker} | {company.company_name}"# | {parameter_name}"
            fig = fig.add_trace(go.Scatter(x = columns, y= rows, name=trace_name), row=fig_row, col=fig_col)

            if fig_col < subplot_cols:
                fig_col = fig_col+1
            else:
                fig_col=1
                fig_row = fig_row + 1

        fig.update_xaxes(categoryorder='category ascending')  # sort X-axis (when X-axis of different companies contains different ranges i.e. 2015-2021, 2016-2022)

        fig.update_traces(mode="markers+lines", hovertemplate=None) #enable hover-mode, interactively display values on the graph when pointed with mouse
        fig.update_layout(hovermode="x", hoverlabel_namelength=-1,  title=parameter_name) #display the full parameter name
        fig.update_layout(height=300*subplot_rows) #update the subplot height
        fig.update_layout(showlegend=False) #update the subplot height

        fig.show()

    ##################################################################################################

    def average_income_statement(self, parameter_name, top_companies = 15):
        self.average(parameter_name=parameter_name, top_companies=top_companies, type='income_statement')

    def average_ballance_sheet(self, parameter_name, top_companies = 15):
        self.average(parameter_name=parameter_name, top_companies=top_companies, type='ballance_sheet')

    def average_cashflow_statement(self, parameter_name, top_companies = 15):
        self.average(parameter_name=parameter_name, top_companies=top_companies, type='cashflow_statement')
    
    def average_statistics_ratios(self, parameter_name, top_companies = 15):
        self.average(parameter_name=parameter_name, top_companies=top_companies, type='statistics_ratios')

    def average(self, parameter_name, top_companies, type):
        companies_data = [] #collect company-data information, needed for export 
        companies_names = [] #collect copany-names, needed for visuals
        param_values = [] #collect average-value for respective parameter_name

        for company in self.companies_data:
            companies_data.append(company) #get company-data
            companies_names.append(f'{company.company_ticker} | {company.company_name}') #get company ticker and name
            
            if type == 'income_statement':
                param_values.append(company.income_statement.loc[parameter_name].mean()) #get average-values of the respetive parameter
            elif type == 'ballance_sheet':
                param_values.append(company.balanse_sheet.loc[parameter_name].mean()) #get average-values of the respetive parameter
            elif type == 'cashflow_statement':
                param_values.append(company.cashflow_statement.loc[parameter_name].mean()) #get average-values of the respetive parameter
            elif type == 'statistics_ratios':
                param_values.append(company.statistics.loc[parameter_name].mean()) #get average-values of the respetive parameter

        
        data = pd.DataFrame(list(zip(param_values, companies_data)), index=companies_names, columns =[parameter_name, 'company_data']) #convert lists to pandas
        data.sort_values(by=[parameter_name], axis=0, ascending=False, inplace=True) #sort data by respective parameter_name
        data = data.head(top_companies) #keep the top Nth company only
        # print(data)
        
        data_for_visualizing = data.drop(columns='company_data') #remove company_data colums from dataframe, not need for visuals
        output = data['company_data'].to_list() #get the company_data only, needed for export
        fig = px.bar(data_for_visualizing, orientation='h') #create a bar-chart
        fig.update_yaxes(autorange="reversed") #reverse y-exis to match dataframe top-to-bottom order
        # # fig.update_layout(barmode='stack', yaxis={'categoryorder': 'total ascending'})

        print(data_for_visualizing)
        fig.show()
        return output


# DataBase.Start()
# DataBase.DropTable("NYSE-PXD")
# DataBase.Stop()

# tables = DataBase.ListAllTables()

# for item in tables:
#     print(item)

# rows = DataBase.ReadFromDatabase("NYSE ARCA-SNMP/Company-Data")
# print(rows)

# rows = DataBase.ListTableRows('ARCA-SNMP/Company-Data')
# print(rows)

# indexes = DataBase.ListIndexColumn("NYSE ARCA-SNMP/Company-Data")
# print(indexes)

# schema = DataBase.getTableShema("NYSE ARCA-SNMP/Company-Data")
# print(schema)

# DataBase.RenameColumn(col_old_name='0', col_new_name='value', table_name=item)

# for item in tables:
#     if ' ' in item:
#         new_name = item.split()[1]
#         DataBase.RenameTable(item, new_name)

#TODO
#fix the funtion for getting the ticker and the ticker and exchange in the Company-Data database
#fix the column-name 0 in Company-Data database > current database is already updated to "value" but newly scraped data will use the old name "0"

# company_data_tables = []
# for table in tables:
#     if 'Company-Data' in table:
#         # print(table)
#         company_data_tables.append(table)


# companies_with_wrong_names = []
# right_name = []
# wrong_name = []
# for company in company_data_tables:
#     # rows = DataBase.ListTableRows(company)
#     row = DataBase().ListRowByName(table_name=company, row_name="company_url")
    
#     if row[1] not in company:
#         companies_with_wrong_names.append(company)
#         right_name.append(row[1])
#         wrong_name.append(company.split('/')[0])
#         print("***")

        # new_name = company.split('/')[1]
        # new_name = row[1] + '/' + new_name
        # print(row[1], company, new_name)
        # DataBase().DropTable(new_name.split('/')[0])
        # DataBase().RenameTable(table_name_old=company, table_name_new=new_name)
    
    # print(row)
    
#     # company_url = rows[0][1]
# #     print(company_url)
#     # company_url = company_url.replace('https://www.tradingview.com/symbols/', '')
#     # company_url = company_url.replace('/financials-income-statement/?selected=', '')

#     company_url = 'sample_url'

#     rows.insert(0,("company_url",company_url))
#     # print(company)
#     # print(rows)
#     DataBase().DeleteAllRowsFromTable(table_name=company)

#     for item in rows:
#         # print(item)
#         DataBase.InsertRows(table_name=company, columns_tuple=("index", "value"), values_tuple=item)

# for i in range(len(companies_with_wrong_names)):
#     # print(right_name[i], companies_with_wrong_names[i], wrong_name[i])

#     old_name1 = wrong_name[i] + '/Balance-Sheet'
#     new_name1 = right_name[i] + '/Balance-Sheet'
#     DataBase().RenameTable(table_name_old=old_name1, table_name_new=new_name1)

#     old_name2 = wrong_name[i] + '/Cashflow-Statement'
#     new_name2 = right_name[i] + '/Cashflow-Statement'
#     DataBase().RenameTable(table_name_old=old_name2, table_name_new=new_name2)

#     old_name3 = wrong_name[i] + '/Company-Data'
#     new_name3 = right_name[i] + '/Company-Data'
#     DataBase().RenameTable(table_name_old=old_name3, table_name_new=new_name3)

#     old_name4 = wrong_name[i] + '/Income-Statement'
#     new_name4 = right_name[i] + '/Income-Statement'
#     DataBase().RenameTable(table_name_old=old_name4, table_name_new=new_name4)

#     old_name5 = wrong_name[i] + '/Ratios'
#     new_name5 = right_name[i] + '/Ratios'
#     DataBase().RenameTable(table_name_old=old_name5, table_name_new=new_name5)



# DataBase.Stop()

# end = timer()
# print(end - start) # Time in seconds, e.g. 5.38091952400282