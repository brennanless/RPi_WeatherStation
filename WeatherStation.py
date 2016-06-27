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

usb_port = '/dev/ttyACM0'
baud = 19200
timeOut = None

historyFilepath = '/home/pi/Documents/WeatherStation/data/'

#function takes a datetime.now() object and creates a file name string formatted as 'YYYYMMDDHH.csv'	
def datetime_to_filepath(dt):
	return '%s%s%s%s.csv' %(dt.strftime('%Y'), dt.strftime('%m'), dt.strftime('%d'), dt.strftime('%H'))  



##########################
#Main function loop
##########################

def main():

	serial_port = serial.Serial(usb_port, baud, timeOut)
	start_time = time.time()
	
	while True:
	
		DT = datetime.now()
		TimeStr = DT.strftime('%Y-%m-%d %H:%M:%S')
		
		data = serial_port.readline().split(',')
		print(data)
		
		WindDir = '{0}'.format(int(data[1]))
		WindSpd = '{0}'.format(float(data[2]))
		Pressure = '{0}'.format(float(data[3]))
		RH = '{0}'.format(float(data[4]))
		Temp = '{0}'.format(float(data[5]))
		DewPt = '{0}'.format(float(data[6]))
		
		data_string = '%s,%s,%s,%s,%s,%s,%s\n' %(TimeStr, WindDir, WindSpd, Pressure, RH, Temp, DewPt)
		print(data_string)
		
		filename = datetime_to_filepath(DT)
		historyFile = os.path.join(historyFilepath, filename)
		
		with open(historyFile, 'a') as datacsv: 
			datacsv.write(data_string)
			
		start_time += 60
		time.sleep(start_time - time.time())	
			
			
if __name__ == '__main__':
	main()			
			
		