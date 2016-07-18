import time
from datetime import datetime
import os
import requests
import json
import pandas as pd

def time_str_to_ms(time_str):
    pattern = "%Y-%m-%d %H:%M:%S"
    try:
        epoch = int(time.mktime(time.strptime(time_str, pattern)))
    except ValueError:
        print "time_str_to_ms(): Unexpected input -> %s" % time_str
        raise
    return int(epoch*1000)

#smap_post() function takes ipnuts and sends data to smap database on LBNL remote server.
#smap_value is a list of lists (date in ms and value).
def smap_post(sourcename, smap_value, path, uuid, units, timeout): #prior smap_value was x, y
    smap_obj = {}
    smap_obj[path] = {}
    metadata = {}
    metadata['SourceName'] = sourcename
    metadata['Location'] = {'City': 'Fresno'}
    smap_obj[path]["Metadata"] = metadata
    smap_obj[path]["Properties"] = {"Timezone": "America/Los_Angeles",
                                    "UnitofMeasure": units,
                                    "ReadingType": "double"}
    smap_obj[path]["Readings"] = smap_value # previously:[smap_value], [x,y]
    smap_obj[path]["uuid"] = uuid
    data_json = json.dumps(smap_obj)
    http_headers = {'Content-Type': 'application/json'}
    #smap_url = "https://render04.lbl.gov/backend/add/vQRmOWwffl65TRkb4cmj3jWfDiPsglwy4Bog"
    smap_url = "https://rbs-box2.lbl.gov/backend/add/vQRmOWwffl65TRkb4cmj3jWfDiPsglwy4Bog"
    r = requests.post(smap_url, data=data_json, headers=http_headers, verify=False, timeout=timeout)
    return r.text
    
def file_to_int(file):
	return int(file.split('.')[0])    
	
def datetime_to_int(dt):
	valstr = '%s%s%s%s' %(dt.strftime('%Y'), dt.strftime('%m'), dt.strftime('%d'), dt.strftime('%H'))
	return int(valstr)
	 
    
#smap constants
smap_sourcename = 'Turnberry'
sensor_paths = ['/Outdoor_WindDir', '/Outdoor_WindSpd', '/Outdoor_Pressure', '/Outdoor_RH', '/Outdoor_Temp', '/Outdoor_DewPt']
sensor_uuids = ['65f57b21-3d41-11e6-bc07-acbc32bae629', '6b9cfc9e-3d41-11e6-a3dc-acbc32bae629', '73452e75-3d41-11e6-8d67-acbc32bae629', '7afd9399-3d41-11e6-bb26-acbc32bae629', '818f6a4f-3d41-11e6-958e-acbc32bae629', '8a238263-3d41-11e6-883d-acbc32bae629']
sensor_units = ['degrees', 'm/s', 'hpa', '%', 'C', 'C']
timeout = 10

#permanent file paths
path = '/home/pi/Documents/RPi_WeatherStation/data/'
#path = '/Users/brennanless/GoogleDrive/Attics_CEC/DAQ/RPi_WeatherStation/data/'
#archive_path = '/Users/brennanless/GoogleDrive/Attics_CEC/DAQ/RPi_WeatherStation/data/archive/'
archive_path = '/home/pi/Documents/RPi_WeatherStation/data/archive/'

#Create list of .csv files to upload
os.chdir(path) #change working directory to path
#all files in pwd except those beginning with '.', such as mac .DS_store files.
files = []
for item in os.listdir(path):
    if not item.startswith('.') and os.path.isfile(os.path.join(path, item)):
        files.append(item)

#establish current system time
dt = datetime.now() 
val_now = datetime_to_int(dt)


#smap data posting loop. Iterates through each file in the list 'files'; skips the current hourly file.
for file in range(len(files)):
	val = file_to_int(files[file])
	if(val == val_now):
		continue
	else:
		data = pd.read_csv(files[file], header=None, dtype = {0:str, 1:float, 2:float, 3:float, 4:float, 5:float, 6:float})
		data = data.dropna()
		times = []
		times_as_list = data[data.columns[0]].tolist() #extracts the date-time column as a list. 
		#Convert column of datetimes to Unix timestamps in msec
		for i in range(len(times_as_list)):
			times.append(time_str_to_ms(times_as_list[i]))
		#zips each data column with the Unix timestamp list, creating a nested list.
		#Process and post each data column individually. 
		count = 0
		for col in range(len(data.columns)-1):
			smap_value = []
			data_as_list = data[data.columns[col+1]].tolist()
			#create nested list of tuples [(x,y), (a,b), ...]
			smap_value = zip(times, data_as_list)
			#create nested list of lists [[x,y], [a,b], ...]
			for i in range(len(smap_value)):
				smap_value[i] = list(smap_value[i])  		 
			try:	     
				response = smap_post(smap_sourcename, smap_value, sensor_paths[col], sensor_uuids[col], sensor_units[col], timeout=timeout)
			except requests.exceptions.ConnectionError:	
				print 'Connection error, will try again later.'	
			#if smap post is successsful, archive the data file.
			if not response:
				count += 1
		#if all six data columns were posted, then archive the data file.
		if count==6:
			os.rename(path + files[file], archive_path + files[file])			

		
