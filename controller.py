import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time,threading

import Adafruit_DHT


DHTSENSOR = Adafruit_DHT.DHT22

lastpush=0
DHTPIN = 4
BTPIN=22
LEDPIN=18
t=None
ontime=15.0

DHTWAIT=10

def button_callback(channel):
    global LEDPIN
    global lastpush
    global t
    
    print("Button was pushed!")
    now=time.time()
    print(now)
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
        t.cancel() # Do now want to have a timer hanging around to turn off the led later on.
    
    
    
def turnoff():
    global LEDPIN
    print("LED off")
    print(time.time())
    GPIO.output(LEDPIN,GPIO.LOW)

def readDHT(evt):
    global DHTSENSOR
    global DHTPIN
    global DHTWAIT
    while True:
        if evt.isSet():
            return()
        humidity, temperature = Adafruit_DHT.read_retry(DHTSENSOR, DHTPIN)
        print(humidity)
        print(temperature)
        time.sleep(DHTWAIT)
    


GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
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
GPIO.cleanup() # Clean up


