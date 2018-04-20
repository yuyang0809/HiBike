
__author__ = "xuanchen yao"
__copyright__ = "xuanchen yao"
__license__ = "mit"

import mysql.connector
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier



def train(i):
	try:

		rds_host='mybike.c0jxuz6r8olg.us-west-2.rds.amazonaws.com'
		name='hibike'
		pwd='zx123456'
		db_name='bike'
		port=3306

		conn = mysql.connector.connect(host=rds_host,user=name, password=pwd, database=db_name)

		df = pd.read_sql("select * from weather", con=conn)
		df1 = pd.read_sql("select * from station_{}".format(i), con=conn)

		# prepare data
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

		df2 = pd.merge(df, df1, left_on=['minute', 'hour', 'weekday', 'month', 'day'], right_on=['minute', 'hour', 'weekday', 'month','day'])

		df2 = df2.drop(['last_update_x'] , axis=1)

		categorical_columns = df2[['weather_main', 'weekday', 'status']]
		for column in categorical_columns:
		    df2[column] = df2[column].astype('category')


		continuous_columns = []
		for column in df2.columns.values:
			if column not in categorical_columns:
				continuous_columns.append(column)
		
		df2['humidity'] = df2['humidity'].astype('float')
		continuous_columns.pop(continuous_columns.index('last_update_y'))

		df_dummies_weather_main = pd.get_dummies(df2[['weather_main']])
		df_dummies_weekday = pd.get_dummies(df2[['weekday']])
		
		describe_columns = [x for x in continuous_columns if x not in ['available_bike_stands', 'bike_stands', 'available_bikes', 'visibility', 'day', 'month']]

		X = pd.concat([df2[describe_columns], df_dummies_weather_main, df_dummies_weekday], axis =1)
		y = df2.available_bikes

		# Train RF with 100 trees
		rfc = RandomForestClassifier(n_estimators=80, max_features='auto', oob_score=True, random_state=1)
		rfc.fit(X, y)
		diCol = [x for x in X.columns]
		return(rfc, diCol)

	except Exception as e:
		print("rds error :", e)
	finally:
		pass

if __name__ == '__main__' :
    train(1)
