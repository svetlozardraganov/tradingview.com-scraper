# TrandingView.com Scraper Overview

The goal of this projects is to provide the analyst/investor a better visualization of financial data available at www.tradingview.com

The website doesn't provide a very good way to compare two or more companies, except for the price-charts. To make informative decision the analist/investor needs compare various financial parameters from income statement, balanse sheet, cashflow statement, ratios, dividents and etc. The project allows to visualize specific financial parameters in adjacent visuals for quickly comparison.

The projects allows organizing the visuals in a more conviniet and easy to read layout. The website layout is too small for reviwing multiple graphs at once. Combining several financial parameters on single chart is also supported.

# Technology 
The project is build using the following technologies:
 - Python - the core technology.
 - Selenium - www.tradingview.com loads the data dynamically so other scrape-frameworks like BeautifulSoup and Scrappy cannot handle the data properly.
 - Pandas - for temporarily storing and manipulating the scraped data.
 - Plotly - for interactive charts. Preferable over mathplotlib due to its ability to interact with the visuals.
 - Jupyter Notebook - for interactive code-running and layout organization.
 - Sqlite3 - for permanent data storrage and saving time to download multiple times the same data.
 - Yfinance - for getting the price data (not possible to download from www.tradingview.com)
 - Xlwings - for exporting the data to excell spredsheets.

# Project Structure

The core-funtionality is written in TrandingViewClasses.py file as follows:
- class DataBase - for reading/writing data from/to database-file.
- class Excel - for exporting data to excel-spreadsheets.
- class Helper - for generating income statement, balance sheet, cashflow statement, statistics variables.
- class ScrapeTrendingView - main scraping funtionality and data clean-up
- class GetCompanyData - this is the input class where everything starts from
- class IncomeStatementVisualizer - visualize income-statement parameters
- class BalanceSheetVisualizer - visualize balanse-sheet parameters
- class CashflowStatementVisualizer - visualize cashflow statement parameters
- class StatisticsRatiosVisualizer - visualize ratios parameters
- class CompareCompaniesVisualizer - compare more than one company

# What I learned
- Working with sqlite3 database.
- Scraping web-pages with Selenium framework.
- Working with Pandas Dataframe
- Working with Plotly library.

# Usage
 - for single company: tradignview-apple.ipynb
 - for multiple companies: tradingview_energy_companies.ipynb

# Examples
![image](https://user-images.githubusercontent.com/74985932/206324014-92e0220e-c381-4157-b30b-c42e3f4fdb4f.png)
![image](https://user-images.githubusercontent.com/74985932/206324188-e9bcd0be-ffda-4182-84c5-ebb0acfb9fac.png)



