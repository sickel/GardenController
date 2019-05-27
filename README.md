# GardenController
Using to take various input and control a watering system in my greenhouse

For lcd, using library mikezlcd.py from https://www.mikronauts.com/raspberry-pi/raspberry-pi-1602-and-2004-lcd-interfacing/ 


sudo apt install python3-rpi.gpio python3-setuptools python3-dev python3-psycopg2 


git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT.git
sudo python3 setup.py install


dbconn.txt:

dbname=<database> user=<username> password=<password> hostaddr=<host> port=<port>
<Number that identifies station>
