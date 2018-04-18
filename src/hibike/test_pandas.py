
__author__ = "xuanchen yao"
__copyright__ = "xuanchen yao"
__license__ = "mit"

import mysql.connector
import pandas as pd

rds_host='mybike.c0jxuz6r8olg.us-west-2.rds.amazonaws.com'
name='hibike'
pwd='zx123456'
db_name='bike'
port=3306

conn = mysql.connector.connect(host=rds_host,user=name, password=pwd, database=db_name)

df = pd.read_sql("select * from weather", con=conn)
df1 = pd.read_sql("select * from station_1", con=conn)

df['month'] = df['last_update'].dt.month
df['day'] = df['last_update'].dt.day
df['weekday'] = df['last_update'].dt.weekday_name
df['hour'] = df['last_update'].dt.hour
df['minute'] = df['last_update'].dt.minute

df1['month'] = df1['last_update'].dt.month
df1['day'] = df1['last_update'].dt.day
df1['weekday'] = df1['last_update'].dt.weekday_name
df1['hour'] = df1['last_update'].dt.hour
df1['minute'] = df1['last_update'].dt.minute

df1.minute = (df1.minute > 30) *30

df2 = pd.merge(df, df1, left_on=['minute', 'hour', 'weekday', 'month', 'day'], right_on=['minute', 'hour', 'weekday', 'month', 'day'])

df2.drop(['last_update_x'] , axis=1)
print(df1)

