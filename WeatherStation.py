import os
import time
from datetime import datetime
import serial


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
timeOut = None

historyFilepath = '/home/pi/Documents/RPi_WeatherStation/data/'

#function takes a datetime.now() object and creates a file name string formatted as 'YYYYMMDDHH.csv'	
def datetime_to_filepath(dt):
	return '%s%s%s%s.csv' %(dt.strftime('%Y'), dt.strftime('%m'), dt.strftime('%d'), dt.strftime('%H'))  



##########################
#Main function loop
##########################

def main():

	time.sleep(20) #must wait 9.5 seconds after turning on MetPak for data output
	
	#open serial communication with MetPak
	#if serial connection is not successful, pause 10-sec, try again.
	#This only happens if USB is not connected to RPi.
	while True:
		try:
			serial_port = serial.Serial(usb_port, baud, timeout=timeOut)
			break	
		except:
			time.sleep(10)
			continue

	start_time = time.time()
	
	while True:
	
		DT = datetime.now()
		TimeStr = DT.strftime('%Y-%m-%d %H:%M:%S')
			
		#read line of data from serial port, split by comma. 
		try:
			data = serial_port.readline().split(',')
		except:
			#if readline fails, pause 60-seconds, try again.
                	start_time += 60
                	time.sleep(start_time - time.time())
			break
			#continue

		#print(data)

		if data[1].isdigit() == False:
			break
		
		#format values as numeric, then strings
		WindDir = '{0}'.format(int(data[1]))
		WindSpd = '{0}'.format(float(data[2]))
		Pressure = '{0}'.format(float(data[3]))
		RH = '{0}'.format(float(data[4]))
		Temp = '{0}'.format(float(data[5]))
		DewPt = '{0}'.format(float(data[6]))
		
		#assemble data string to write to file.
		data_string = '%s,%s,%s,%s,%s,%s,%s\n' %(TimeStr, WindDir, WindSpd, Pressure, RH, Temp, DewPt)
		#print(data_string)
		
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
			
			
if __name__ == '__main__':
	main()			
			
		
