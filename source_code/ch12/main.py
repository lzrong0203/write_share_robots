import sqlite3
import csv
import datetime as dt
from datetime import datetime


def convert_date(date_str):
    # print(date_str.split("/"))
    year, month, day = map(int, date_str.split("/"))
    year = year + 1911
    return dt.date(year, month, day)


with sqlite3.connect("hahow_stock.sqlite") as conn:
    cur = conn.cursor()
    stocks_table_name = "stocks"
    cur.execute(f"DROP TABLE IF EXISTS {stocks_table_name}")
    cur.execute(f"""CREATE TABLE {stocks_table_name}
                    (
                    stock_id VARCHAR(10) PRIMARY KEY,
                    name VARCHAR(100),
                    stock_name VARCHAR(10),
                    stock_type VARCHAR(10)
                    )""")
    with open("t51sb01_20231122_012457580.csv", encoding="big5") as f:
        data = csv.DictReader(f)
        data_list = list(data)
    col_name = list(data_list[0].keys())
    stock_id = col_name[0]
    name = col_name[1]
    stock_name = col_name[2]
    stock_type = col_name[3]
    for row in data_list:
        cur.execute(f"""INSERT INTO {stocks_table_name} (stock_id, name, stock_name, stock_type)
                        VALUES (?, ?, ?, ?)""",
                    (row[stock_id], row[name], row[stock_name], row[stock_type]))
    conn.commit()

    rows = cur.execute(f"""SELECT * FROM {stocks_table_name}""")
    for row in rows:
        pass
    with open("STOCK_DAY_AVG_2330_202310.csv", encoding="big5") as f:
        # print(f.read())
        next(f)
        data = csv.DictReader(f)
        data_list = list(data)
        date = "日期"
        close = "收盤價"
    trades_table_name = "trades"
    cur.execute(f"DROP TABLE IF EXISTS {trades_table_name}")
    cur.execute(f"""CREATE TABLE {trades_table_name} 
                    (
                    id INTEGER PRIMARY KEY,
                    ticker VARCHAR(10),
                    close FLOAT,
                    date DATE
                    )
                    """)

    for i in data_list[:-5]:
        date_convert = convert_date(i[date])
        date_convert = date_convert.strftime("%Y-%m-%d")
        # print(date_convert)
        cur.execute(f"""INSERT INTO {trades_table_name} (ticker, close, date)
                        VALUES (2330, {i[close]}, '{date_convert}')"""
                    )

    conn.commit()

    rows = cur.execute(f"""SELECT * FROM {trades_table_name}""")
    for row in rows:
        pass

    rows = cur.execute(f"""SELECT date, close, stock_id, stock_name  FROM {stocks_table_name}
                    JOIN {trades_table_name} ON {stocks_table_name}.stock_id = {trades_table_name}.ticker
                    WHERE close > 539.2
    """)
    for row in rows:
        print(f"日期：{row[0]}，收盤價：{row[1]}，股票代號：{row[2]}，股票名稱：{row[3]}")
