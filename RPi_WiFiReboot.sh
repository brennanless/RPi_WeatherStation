
#This script is borrowed from http://weworkweplay.com/play/rebooting-the-raspberry-pi-when-it-loses-wireless-connection-wifi/
#It pings the remote cradle point router (in the Fresno attic), and if the connection is down, the RPi wifi is rebooted, which
#hopefully leads RPi to reconnect to 'live' network.

ping -c4 192.168.21.1 > /dev/null
 
if [ $? != 0 ] 
then
  echo "No network connection, restarting wlan0"
  /sbin/ifdown 'wlan0'
  sleep 5
  /sbin/ifup --force 'wlan0'
fi