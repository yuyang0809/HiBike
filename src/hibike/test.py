
__author__ = "xuanchen yao"
__copyright__ = "xuanchen yao"
__license__ = "mit"


from flask import Flask, render_template, url_for, redirect
from flask import request
import json
from info import *
import requests
from datetime import datetime
import mysql.connector
from distance import dis


app = Flask(__name__)
conn = mysql.connector.connect(host=rds_host,user=name, password=pwd, database=db_name)
cur = conn.cursor()

cur.execute("select * from Bike_Stations")
stationData = cur.fetchall()


	#if methodId == 'distant':
		#data={'lat':request.values.get('lat'), 'lng':request.values.get('lng')}
		#url=("https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={},{}&destinations=53.3393%2C-6.267%7C&key=AIzaSyA-IvyG8VIRCmxjbqpJoPJQvcVTW6NkKFQ".format(str(data['lat']),str(data['lng'])))
		#r=requests.get(url)
		#distant = json.dumps(r.json())
		#return(distant)




@app.route('/', methods=['get'])
def index():
    cur.execute('select weather_main,temp from weather ORDER BY last_update DESC limit 0, 1')
    weatherData = cur.fetchone()
    return render_template('index.html', stationData=stationData,weatherData=weatherData)

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
    stationData = cur.fetchall()
    return render_template('stationDetail.html', stationNum=stationNum, detailData=detailData, stationData=stationData,alldata=alldata)

@app.route('/test', methods=['get'])
def index1():
	return render_template('index1.html', stationData=stationData)


with app.test_request_context():
	print(url_for('communicate'))

@app.route('/try', methods=['get'])
def try1():
	return render_template('try.html', stationData=stationData)

if __name__ == '__main__' :
   	#app.run(debug=True, ssl_context='adhoc')
    app.run(debug=True)
