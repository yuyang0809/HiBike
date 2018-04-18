
__author__ = "xuanchen yao"
__copyright__ = "xuanchen yao"
__license__ = "mit"


from flask import Flask, render_template, url_for, redirect
from flask import request
import json
import requests
from datetime import datetime
import mysql.connector


app = Flask(__name__)
conn = mysql.connector.connect(user='root', password='2978291', database='HiBike')
cur = conn.cursor()

cur.execute("select * from Bike_Stations")
stationData = cur.fetchall()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def maps():
    return render_template('map.html', stationData=stationData)

@app.route('/test', methods=['get'])
def test0():
    return render_template('test.html', stationData=stationData)

@app.route('/test', methods=['post'])
def test00():
	methodId = request.values.get('Id')
	if methodId == 'searchForm':
		address = request.values.get('address')
		r0 = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyA-IvyG8VIRCmxjbqpJoPJQvcVTW6NkKFQ'.format(address))
		lat = r0.json()['results'][0]['geometry']['location']['lat']
		lng = r0.json()['results'][0]['geometry']['location']['lng']
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
	elif methodId == '1':
		dynamicData = {'available_bike_stands':request.values.get('stationNum')}
		dynamicData = json.dumps(dynamicData)
		return dynamicData
	#if methodId == 'distant':
		#data={'lat':request.values.get('lat'), 'lng':request.values.get('lng')}
		#url=("https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={},{}&destinations=53.3393%2C-6.267%7C&key=AIzaSyA-IvyG8VIRCmxjbqpJoPJQvcVTW6NkKFQ".format(str(data['lat']),str(data['lng'])))
		#r=requests.get(url)
		#distant = json.dumps(r.json())
		#return(distant)




@app.route('/test2', methods=['get'])
def test1():
	return render_template('test2.html', stationData=stationData)

@app.route('/test2', methods=['post'])
def test10():
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
	elif methodId == 'searchform':
		address = request.values.get('address')
		r0 = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyA-IvyG8VIRCmxjbqpJoPJQvcVTW6NkKFQ'.format(address))
		lat = r0.json()['results'][0]['geometry']['location']['lat']
		lng = r0.json()['results'][0]['geometry']['location']['lng']
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


@app.route('/station/<stationNum>', methods=['get'])
def stationDetail(stationNum=None):
    cur.execute('select * from station_'+str(stationNum)+' ORDER BY last_update DESC limit 0, 1')
    detailData = cur.fetchone()
    cur.execute("select * from Bike_Stations where Number = {}".format(stationNum))
    stationData = cur.fetchall()
    return render_template('stationDetail.html', stationNum=stationNum, detailData=detailData, stationData=stationData)


@app.route('/test3', methods=['get'])
def test3():
    return render_template('test3.html')

with app.test_request_context():
	print(url_for('index'))
	print(url_for('test00'))
	print(url_for('test10'))
	print(url_for('index'))


if __name__ == '__main__' :
   	#app.run(debug=True, ssl_context='adhoc')
    app.run(debug=True)
