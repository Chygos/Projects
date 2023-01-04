import sqlite3
import pandas as pd
import timeit
import matplotlib.pyplot as plt

# Create database and tables
db_name = 'sales.db'


train = pd.read_csv('train.csv', parse_dates=['Date'])
features = pd.read_csv('features.csv', parse_dates=['Date'])
stores = pd.read_csv('stores.csv')
table_names = ['Sales', 'Features', 'Stores']

try:
    start = timeit.timeit()
    conn = sqlite3.connect(db_name)
    print(f'{db_name} is connected')
    for df, table_name in zip([train, features, stores], table_names):
        # save as sql
        df.to_sql(table_name, con=conn, if_exists='replace', index=False)
    
    stop = timeit.timeit()
    print(f'Tables saved. It took {stop-start} seconds')
    conn.commit()
    conn.close()
except Exception as err:
    print(err)

# connect to database    
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Monthly Average Sales
records = cursor.execute("""SELECT strftime('%m', Date) AS Month, 
                            AVG(Weekly_Sales) AS 'Average Monthly Sales'
                            FROM Sales
                            GROUP BY Month;""")


print(pd.DataFrame(records, columns=[i[0] for i in records.description]))


# get years of sale and yearly weekly sales by store
query = cursor.execute("SELECT DISTINCT cast(strftime('%Y', Date) as year) AS INT FROM Sales")

years = list(query)

print('Yearly Weekly Sales by Store\n')
for year in years:
    print('{} Sales'.format(*year))
    records = cursor.execute("""SELECT Store, AVG(Weekly_Sales) AS 'Average Weekly Sales'
                                 FROM Sales
                                 WHERE Date LIKE '{}%' 
                                 GROUP BY Store
                                 ORDER BY "Average Weekly Sales" DESC
                                 LIMIT 10;""".format(*year))

    print(pd.DataFrame(records, columns=[i[0] for i in records.description]))
    print()


# How many stores are in each store types and how much did each store category make?
print('Yearly Weekly Sales by Store\n')
for year in years:
    print('{} Sales'.format(*year))
    records = cursor.execute("""SELECT Stores.Type, COUNT(DISTINCT Stores.Store) AS 'Num of Stores',
                                MIN(Weekly_Sales) AS 'Min Weekly Sales',
                                AVG(Weekly_Sales) AS 'Average Weekly Sales',
                                MAX(Weekly_Sales) AS 'Max Weekly Sales'
                                FROM Sales
                                INNER JOIN Stores
                                ON Stores.Store = Sales.Store
                                WHERE Date LIKE '{}%' AND Weekly_Sales >= 0
                                GROUP BY Stores.Type
                                ORDER BY "Average Weekly Sales" 
                                DESC;""".format(*year))

    print(pd.DataFrame(records, columns=[i[0] for i in records.description]))
    print()


# minimum, average, median and max size of each store
query = cursor.execute("""SELECT
                          CASE 
                          WHEN Stores.Size < 75000 THEN 'SMALL'
                          WHEN Stores.Size > 75000 AND Stores.Size < 150000 THEN 'MEDIUM'
                          ELSE 'LARGE'
                          END SizeGroup,
                          COUNT(DISTINCT Stores.Store) AS Num_stores,
                          AVG(Sales.Weekly_Sales) AS Av_Weekly_Sales,
                          CAST(AVG(Stores.Size) AS INT) AS Mean_size
                          FROM Sales
                          INNER JOIN Stores
                          ON Stores.Store = Sales.Store
                          GROUP BY SizeGroup""")

print(pd.DataFrame(query, columns=[i[0] for i in query.description]))

conn.commit()
cursor.close()