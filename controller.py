import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time,threading

import Adafruit_DHT

from mikezlcd import *
lcd = lcd_module(2004, 25, 24, 22, 18, 17,23)

DHTSENSOR = Adafruit_DHT.DHT22

lastpush=0
DHTPIN = 4
BTPIN=7
LEDPIN=8
t=None
ontime=120.0

TIMEFORMAT="%m/%d/%Y, %H:%M:%S.%f"

DHTWAIT=30

def fmttime(timefloat):
    return time.strftime(TIMEFORMAT,time.localtime(timefloat))

def button_callback(channel):
    global LEDPIN
    global lastpush
    global t
    
    print("Button was pushed!")
    now=time.time()
    print(fmttime(now))
    if now - lastpush < 1: # Debouching
        print("whopsa, wait a moment")
        return
    lastpush=now
    state=GPIO.input(LEDPIN)
    if state==0:
        GPIO.output(LEDPIN,GPIO.HIGH)
        t = threading.Timer(ontime, turnoff)
        t.start() 
        print("ON")
    else:
        turnoff()
        


def handleht(hum,temp,mintemp,maxtemp):
    global lcd
    print("Humidity",hum,"%")
    print("Temperature",temp,"°C")
    lcd.disp(0,0,"Temp {:5.1f} oC".format(temp))
    lcd.disp(0,1,"     {:5.1f} - {:5.1f}".format(mintemp,maxtemp))
    lcd.disp(0,2,"Fukt {:5.1f} %".format(hum))
    
    
def turnoff():
    global LEDPIN
    print("LED off")
    print(fmttime(time.time()))
    GPIO.output(LEDPIN,GPIO.LOW)
    if not t == None:
        t.cancel() # Do now want to have a timer hanging around to turn off the led later on.
    
def readDHT(evt):
    global DHTSENSOR
    global DHTPIN
    global DHTWAIT
    mintemp=100
    maxtemp=-100
    dhtread=0
    while True:
        if evt.isSet():
            return()
        now=time.time()
        if now-dhtread>DHTWAIT: # Cannot sleep for DHTWAIT as it will stop processing of ev
            print("DHTread:")
            dhtread=now
            print()
            humidity, temperature = Adafruit_DHT.read_retry(DHTSENSOR, DHTPIN)
            mintemp=min(mintemp,temperature)
            maxtemp=max(maxtemp,temperature)
            handleht(humidity,temperature,mintemp,maxtemp)
            if evt.isSet():
                return()
            if humidity>75:
                state=GPIO.input(LEDPIN)
                if not state==0:
                    print("Too humid, turning off")
                    turnoff()
        time.sleep(1)
    


GPIO.setwarnings(False) # Ignore warning for now
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(BTPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(LEDPIN,GPIO.OUT) # Want to make sure we start in a known state
GPIO.output(LEDPIN,GPIO.LOW)
GPIO.add_event_detect(BTPIN,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge
stopDHT=threading.Event()
DHTthread=threading.Thread(target = readDHT, args = (stopDHT, ))
DHTthread.start()
message = input("Press enter to quit\n\n") # Run until someone presses enter
stopDHT.set()
DHTthread.join()
turnoff()
GPIO.cleanup() # Clean up


