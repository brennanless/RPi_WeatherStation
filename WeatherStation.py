import signal
import os
import time
from datetime import datetime
import serial
import math
import threading


##########################
#ASCII String format:
##########################

#Stx, Node, WindDir, WindSpd, Pressure, Humidity, Temperature, DewPoint, SupplyVolt, StatusCode, ETX, Checksum, CarriageReturnLineFeed
#<STX>Q,170,000.08,1019.5,035.0,+024.7,+008.3,+04.9,00,<ETX>55 & (CR,LF)


##########################
#Configuration vales
##########################

#This usb port assignment changes if you unplug and reinsert the usb cable.
#ttyUSB0 ttyUSB1, ttyUSB2, etc. 
#Need to sudo reboot the RPi to get normal ttyUSB0 assignment. 
usb_port = '/dev/ttyUSB0'
baud = 19200
timeOut = 1

historyFilepath = '/home/pi/Documents/RPi_WeatherStation/data/'

WindDir_list = []
WindSpd_list = []
Pressure_list = []
RH_list = []
Temp_list = []
DewPt_list = []

#function takes a datetime.now() object and creates a file name string formatted as 'YYYYMMDDHH.csv'	
def datetime_to_filepath(dt):
	return '%s%s%s%s.csv' %(dt.strftime('%Y'), dt.strftime('%m'), dt.strftime('%d'), dt.strftime('%H'))  

def daemon_serial_read():

	global WindDir_list
	global WindSpd_list
	global Pressure_list
	global RH_list
	global Temp_list
	global DewPt_list
	
	time.sleep(20)
	
	serial_port = serial.Serial(usb_port, baud, timeout=timeOut)
	
	while True:
		data = serial_port.readline().split(',')
		print data
		if data[0]:
			if data[1].isdigit() == True:
		#format values as numeric, then strings
				WindDir_list.append(int(data[1]))
				WindSpd_list.append(float(data[2]))
				Pressure_list.append(float(data[3]))
				RH_list.append(float(data[4]))
				Temp_list.append(float(data[5]))
				DewPt_list.append(float(data[6]))
				time.sleep(0.5)
			else:
				time.sleep(0.5)
		else:
			time.sleep(0.5)


##########################
#Main function loop
##########################

def write_to_file():

	global WindDir_list
	global WindSpd_list
	global Pressure_list
	global RH_list
	global Temp_list
	global DewPt_list

# 	time.sleep(20) #must wait 9.5 seconds after turning on MetPak for data output
# 	
# 	#open serial communication with MetPak
# 	#if serial connection is not successful, pause 10-sec, try again.
# 	#This only happens if USB is not connected to RPi.
# 	while True:
# 		try:
# 			serial_port = serial.Serial(usb_port, baud, timeout=timeOut)
# 			break	
# 		except:
# 			time.sleep(10)
# 			continue

	start_time = time.time()
	
	while True:
	
# 		WindDir_list = []
# 		WindSpd_list = []
# 		Pressure_list = []
# 		RH_list = []
# 		Temp_list = []
# 		DewPt_list = []

			
# 		read line of data from serial port, split by comma. 
# 		try:
# 			data = serial_port.readline().split(',')
# 		except:
# 			if readline fails, pause 60-seconds, try again.
#                 	start_time += 60
#                 	time.sleep(start_time - time.time())
# 			break
# 			continue
# 
# 		print(data)
# 
# 		for i in range(15):
# 		
# 			data = serial_port.readline().split(',')
# 
# 			if data[1].isdigit() == False:
# 				break
# 		
# 			format values as numeric, then strings
# 			WindDir_list.append(int(data[1]))
# 			WindSpd_list.append(float(data[2]))
# 			Pressure_list.append(float(data[3]))
# 			RH_list.append(float(data[4]))
# 			Temp_list.append(float(data[5]))
# 			DewPt_list.append(float(data[6]))
# 			
# 			format values as numeric, then strings
# 			WindDir = .append('{0}'.format(int(data[1])))
# 			WindSpd.append('{0}'.format(float(data[2])))
# 			Pressure.append('{0}'.format(float(data[3])))
# 			RH.append('{0}'.format(float(data[4])))
# 			Temp.append('{0}'.format(float(data[5])))
# 			DewPt.append('{0}'.format(float(data[6])))

		#calculate the average of the last 15 values.
		WindDir = sum(WindDir_list[-15:]) / float(len(WindDir_list[-15:]))
		WindSpd = sum(WindSpd_list[-15:]) / len(WindSpd_list[-15:])
		Pressure = sum(Pressure_list[-15:]) / len(Pressure_list[-15:])
		RH = sum(RH_list[-15:]) / len(RH_list[-15:])
		Temp = sum(Temp_list[-15:]) / len(Temp_list[-15:])
		DewPt = sum(DewPt_list[-15:]) / len(DewPt_list[-15:])
		
		DT = datetime.now()
		TimeStr = DT.strftime('%Y-%m-%d %H:%M:%S')
		
		#assemble data string to write to file.
		data_string = '%s,%s,%s,%s,%s,%s,%s\n' %(TimeStr, WindDir, WindSpd, Pressure, RH, Temp, DewPt)
		print(data_string)
		
		filename = datetime_to_filepath(DT)
		historyFile = os.path.join(historyFilepath, filename)
		
		#open data file for current hour, write data line, close file.
		#if file opening fails, pause 60-sec, try again.
		try:
			with open(historyFile, 'a') as datacsv: 
				datacsv.write(data_string)
		except:
              		start_time += 60
                	time.sleep(start_time - time.time())
			continue
			
		start_time += 60
		time.sleep(start_time - time.time())	
			
	
def main():
	try:
		d = threading.Thread(name='daemon_serial_read', target=daemon_serial_read)
		d.setDaemon(True)	
		m = threading.Thread(name='write_to_file', target=write_to_file)	
		d.start()
		time.sleep(60)
		m.start()
		signal.pause()
	except(KeyboardInterrupt, SystemExit):
		print 'Exiting program'		
			
			
if __name__ == '__main__':
	main()			
			
		
