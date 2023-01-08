import sqlite3

# Connect to the database
conn = sqlite3.connect('mydatabase.db')

# Create a cursor
cursor = conn.cursor()

#cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")

cursor.execute("""CREATE TABLE if not exists Tickers (
	market TEXT,
	exchange TEXT,
	symbol TEXT,
	sector TEXT,
	industry TEXT,
	company_ticker TEXT PRIMARY KEY,
	company_name TEXT,
	company_url	TEXT)""")


# Build the INSERT OR IGNORE statement
#stmt = 'INSERT OR IGNORE INTO users (id, name, age) VALUES (?, ?, ?)'

# Execute the statement
# cursor.execute(stmt, (1, 'John', 24))

table_name="Tickers"
input_columns = ("market", "exchange", "symbol", "sector", "industry", "company_ticker", "company_name", "company_url")
input_values = ("market1", "exchange1", "symbol1", "sector1", "industry1", "company_ticker2", "company_name1", "company_url1")

cursor.execute(f'INSERT OR IGNORE INTO "{table_name}" {input_columns} VALUES {input_values}')



# Commit the change
conn.commit()

# Close the connection
conn.close()