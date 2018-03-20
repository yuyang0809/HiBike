from datetime import datetime
import json, requests
import threading as thd
import time
from datetime import datetime
import mysql.connector
conn = mysql.connector.connect(user='root', password='2978291', database='HiBike')
cursor = conn.cursor()

def creat_table():
	stationsList = []
	r0 = requests.get('https://api.jcdecaux.com/vls/v1/stations/?contract=Dublin&apiKey=4b04deb4cd76b0606da005d97cfde13863b090b6')
	for i in range(0, len(r0.json())):
		stationsList.append(r0.json()[i]['number'])
		cursor.execute('create table if NOT EXISTS station_'+str(r0.json()[i]['number'])+' (last_update TIMESTAMP primary key Not null, banking BOOLEAN, bonus BOOLEAN, status VARCHAR(45), bike_stands int(11), available_bike_stands int(11), available_bikes int(11), weather VARCHAR(45), temperature VARCHAR(45))')
	print("created")
	print(stationsList)
	return stationsList
	

def get_data(stationsList):
	try:
		r01 = requests.get('https://api.jcdecaux.com/vls/v1/stations/?contract=Dublin&apiKey=4b04deb4cd76b0606da005d97cfde13863b090b6')
		if len(stationsList) == len(r01.json()):
			for i in stationsList:
				r1 = requests.get('https://api.jcdecaux.com/vls/v1/stations/'+str(i)+'?contract=Dublin&apiKey=4b04deb4cd76b0606da005d97cfde13863b090b6')
				r2 = requests.get("http://api.openweathermap.org/data/2.5/weather?lat="+str(r1.json()['position']['lat'])+"&lon="+str(r1.json()['position']['lng'])+"&APPID=7b3e054e55cf81602b4298ca04a0fa18")
				cursor.execute("INSERT INTO station_"+str(i)+"(last_update, banking, bonus, status, bike_stands, available_bike_stands, available_bikes, weather, temperature) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", [datetime.fromtimestamp(r1.json()['last_update']*0.001), r1.json()['banking'], r1.json()['bonus'], r1.json()['status'], r1.json()['bike_stands'], r1.json()['available_bike_stands'], r1.json()['available_bikes'], r2.json()['weather'][0]['main'], r2.json()['main']['temp']])
				conn.commit()
				print(str(i)+"done")
		else:
			stationsList = creat_table()
			get_data(stationsList)

	except mysql.connector.errors.IntegrityError as e:
		print("There are not new data")
	else:
		pass
	finally:
		thd.Timer(300,get_data).start()
		
	
stationsList = creat_table()
get_data(stationsList)
