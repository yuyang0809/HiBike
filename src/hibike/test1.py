
__author__ = "xuanchen yao"
__copyright__ = "xuanchen yao"
__license__ = "mit"

from test_pandas import train
from flask import Flask, render_template, url_for, redirect
from flask import request
import json
import requests
from datetime import datetime
import mysql.connector
from distance import dis

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

rds_host='mybike.c0jxuz6r8olg.us-west-2.rds.amazonaws.com'
name='hibike'
pwd='zx123456'
db_name='bike'
port=3306

app = Flask(__name__)
conn = mysql.connector.connect(host=rds_host,user=name, password=pwd, database=db_name)
cur = conn.cursor()

cur.execute("select * from Bike_Stations")
stationData = cur.fetchall()


from test_pandas import train

import threading as thd
import time
di={}
diCol = {}
def renewdict():
    global di
    global diCol
    print('work')
    di, diCol = getformlation()
    print('done')
    print(di)
    thd.Timer(86400,renewdict).start()

def getformlation():
    di = {}
    diCol = {}
    for i in stationData:
        di[i[0]], diCol[i[0]] = train(i[0])
    return(di, diCol)

	#if methodId == 'distant':
		#data={'lat':request.values.get('lat'), 'lng':request.values.get('lng')}
		#url=("https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={},{}&destinations=53.3393%2C-6.267%7C&key=AIzaSyA-IvyG8VIRCmxjbqpJoPJQvcVTW6NkKFQ".format(str(data['lat']),str(data['lng'])))
		#r=requests.get(url)
		#distant = json.dumps(r.json())
		#return(distant)




@app.route('/', methods=['get'])
def index():
	return render_template('index.html', stationData=stationData)

@app.route('/', methods=['post'])
def communicate():
	methodId = request.values.get('Id')
	if methodId == '1':
		stationNum = request.values.get('stationNum')
		cur.execute('select available_bike_stands, available_bikes from station_'+stationNum+' ORDER BY last_update DESC limit 0, 1')
		data = cur.fetchone()
		dynamicData = {'available_bike_stands':data[0], 'available_bikes':data[1]}
		dynamicData = json.dumps(dynamicData)
		return dynamicData
	elif methodId == '2':
		stationNum = request.values.get('stationNum')
		cur.execute('select * from station_'+stationNum+' ORDER BY last_update DESC limit 0, 1')
		detailData = cur.fetchone()
		detailData = {'last_update':detailData[0].timestamp(), 'banking':detailData[1], 'bonus':detailData[2], 'status':detailData[3], 'bike_stands':detailData[4], 'weather':detailData[5], 'temperature':detailData[6]}
		detailData = json.dumps(detailData)
		return detailData
	elif methodId == 'searchForm':
		address = request.values.get('address')
		r0 = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyA-IvyG8VIRCmxjbqpJoPJQvcVTW6NkKFQ'.format(address))
		lat = r0.json()['results'][0]['geometry']['location']['lat']
		lng = r0.json()['results'][0]['geometry']['location']['lng']
		if dis(lat,lng,53.344,-6.2668)<=10:
			station_lat = stationData[0][3]
			station_lng = stationData[0][4]
			minDistance = (lat-station_lat)**2 + (lng-station_lng)**2
			nearNum = stationData[0][0]
			for i in range(1,len(stationData)):
				station_lat = stationData[i][3]
				station_lng = stationData[i][4]
				current = (lat-station_lat)**2 + (lng-station_lng)**2
				if(current < minDistance):
					minDistance = current
					nearNum = stationData[i][0]
			return json.dumps({'station':nearNum})
		else:
			return json.dumps({'station':None})
		


@app.route('/station/<stationNum>', methods=['get'])
def stationDetail(stationNum=None):
	cur.execute('select * from station_'+str(stationNum)+' ORDER BY last_update DESC limit 0, 1')
	detailData = cur.fetchone()
	cur.execute("select concat(hour(last_update),':00') as time,available_bike_stands,available_bikes from station_"+str(stationNum)+' WHERE last_update >=  NOW() - interval 1 day  GROUP BY floor(hour(last_update))  ORDER BY last_update ASC;')
	alldata = cur.fetchall()
	cur.execute("select * from Bike_Stations where Number = {}".format(stationNum))
	stationDetail = cur.fetchall()
	diCol_pr = {}
	global diCol
	global di
	stationNum = int(stationNum)
	try:
		print(diCol[stationNum])
	except Exception as e:
		print(stationNum, type(stationNum))
	try:
	    for i in diCol[stationNum]:
	        diCol_pr[i] = 0

	    r_w = requests.get('http://api.openweathermap.org/data/2.5/forecast?q=Dublin,IE&APPID=7b3e054e55cf81602b4298ca04a0fa18')

	    diCol_pr['pre_available_bikes'] = detailData[-1]
	    di['pre_minute'] = detailData[0].hour * 60 + detailData[0].minute

	    diCol_pr['day'] = datetime.utcfromtimestamp(r_w.json()['list'][0]['dt']).day
	    diCol_pr['hour'] = datetime.utcfromtimestamp(r_w.json()['list'][0]['dt']).hour
	    diCol_pr['humidity'] = r_w.json()['list'][0]['main']['humidity']
	    diCol_pr['minute'] = datetime.utcfromtimestamp(r_w.json()['list'][0]['dt']).minute + datetime.utcfromtimestamp(r_w.json()['list'][0]['dt']).hour * 60
	    diCol_pr['temp'] = r_w.json()['list'][0]['main']['temp']
	    diCol_pr['wind'] = r_w.json()['list'][0]['wind']['speed']

	    weather = r_w.json()['list'][0]['weather'][0]['main']
	    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
	                'Friday', 'Saturday', 'Sunday']
	    weekday = weekdays[datetime.utcfromtimestamp(r_w.json()['list'][0]['dt']).weekday()]
	    if 'weather_main_{}'.format(weather) in diCol_pr.keys():
	        diCol_pr['weather_main_{}'.format(weather)] = 1
	        if 'weekday_{}'.format(weekday) in diCol_pr.keys():
	            diCol_pr['weekday_{}'.format(weekday)] = 1

	            predi = pd.DataFrame([diCol_pr])
	            rfc_predictions = "available_bikes : {}".format(int(di[stationNum].predict(predi)))
	        else:
	            rfc_predictions = "Something wrong, day information get error."
	    else:
	        rfc_predictions = "A new weather may appear, not enough data to make a prediction."
	except Exception as e:
	    rfc_predictions = "We rebuild the prediction module, please try 10 minutes late. {}".format(e) 
	return render_template('stationDetail.html', stationNum=stationNum, stationDetail=stationDetail ,detailData=detailData, stationData=stationData,alldata=alldata, rfc_predictions=rfc_predictions)


with app.test_request_context():
	print(url_for('communicate'))


if __name__ == '__main__' :
	t = thd.Thread(target=renewdict, name='renewThread')
	#t.start()
	app.run(debug=True)
    