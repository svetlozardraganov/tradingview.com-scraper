# TrandingView.com Scraper Overview

The goal of this projects is to provide the analyst/investor a better visualization of financial data available at www.tradingview.com

The website doesn't provide a very good way to compare two or more companies, except for the price-charts. To make informative decision the analist/investor needs compare various financial parameters from income statement, balanse sheet, cashflow statement, ratios, dividents and etc. The project allows to visualize specific financial parameters in adjacent visuals for quickly comparison.

The projects allows organizing the visuals in a more conviniet and easy to read layout. The website layout is too small for reviwing multiple graphs at once. Combining several financial parameters on single chart is also supported.

# Technology 
The project is build using the following technologies:
 - Python - the main technology.
 - Selenium - www.tradingview.com loads the data dynamically so other scrape-frameworks like BeautifulSoup and Scrappy cannot handle the data properly.
 - Pandas - for temporarily storing and manipulating the scraped data
 - Plotly - for interactive charts. Preferable over mathplotlib due to its ability to interact with the visuals.
 - Jupyter Notebook - for interactive code-running and layout organization.
 - Sqlite3 - for permanent data storrage and saving time to download multiple times the same data.


# Usage


# Examples
