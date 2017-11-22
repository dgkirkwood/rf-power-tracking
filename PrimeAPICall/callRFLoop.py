import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import influxdb
from influxdb import InfluxDBClient
import time

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



#print (response.text)
time.sleep(20)


grafanaAddr = 'grafana:3000'
influxAddr = 'influxdb:8086'
grafanaHead = {'accept' : 'application/json' , 'Content-type' : 'application/json' }

datasourceInfo = {"name": "influx", "type": "influxdb", "access" : "direct" , "url" : "http://" + influxAddr , "database" : "RFStats" , "isdefault" : True}

datasourceJSON = json.dumps(datasourceInfo)

createDataSource = requests.request('POST' , "http://" + grafanaAddr , headers=grafanaHead, auth=('admin' , 'admin') , data =datasourceJSON)

print (createDataSource.status_code)
print (createDataSource.text)

influxClient = InfluxDBClient('influxdb' , '8086', 'test')
influxClient.create_database('RFStats')



url1 = 'https://se-cis-prime-infra1.nsd5.ciscolabs.com/webacs/api/v1/data/RFStats.json?ethernetMac="70:db:98:bc:9b:d0"'


while True:

	headers = {
	    'authorization': "Basic QVBJcmVhZDpDIXNjbzEyMw==",
	    }

	response = requests.request('GET' , url1 , headers=headers, verify=False)

	RFStats = json.loads(response.text)





	for stat in RFStats['queryResponse']['entityId']:
		
		#print (stat['@url'])



		response = requests.request('GET' , stat['@url']+'.json' , headers=headers, verify=False)

		RFStats = json.loads(response.text)

		#print (RFStats)

		RFDetail = RFStats['queryResponse']['entity'][0]['rfStatsDTO']

		print ('The AP MAC with MAC address ' + RFDetail['macAddress'] + ' is transmitting on channel ' + RFDetail['channelNumber'] + ' at power level ' + str(RFDetail['powerLevel']) + ' with output TX of ' + str(RFDetail['txPowerOutput']))

		dbJSON = [{"measurement": "txPowerOutput" , "tags" : {"ethernetMac" : RFDetail['ethernetMac'] , "APMac" : RFDetail['macAddress'] , 	"channel" : RFDetail['channelNumber']}, "fields" : {"value": float(RFDetail['txPowerOutput'])}} , {"measurement": "PowerLevel" , "tags" : {"ethernetMac" : RFDetail['ethernetMac'] , "APMac" : RFDetail['macAddress'] , 	"channel" : RFDetail['channelNumber']}, "fields" : {"value": float(RFDetail['powerLevel'])}}]


		influxClient.write_points(dbJSON, database='RFStats')


	time.sleep(10)