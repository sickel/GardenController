#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time,threading
import sys
import Adafruit_DHT

from mikezlcd import *
lcd = lcd_module(2004, 25, 24, 22, 18, 17,23)
lcd.disp(0,0,"Booting...")


import psycopg2 
f = open("dbconn.txt", "r")
dsn=f.readline()
SENSORID=f.readline()
f.close()
CONN = psycopg2.connect(dsn)
CUR=CONN.cursor()
DHTSENSOR = Adafruit_DHT.DHT22
DHTPIN = 4
BTPIN=7
LEDPIN=8
ONTIME=1200.0
payload=0

lastpush=0
turnofftimer=None


TIMEFORMAT="%Y/%m/%d %H:%M:%S"
DHTWAIT=30
SQL="insert into measure(sensorid,value,type,aux,payload) values(%s,%s,%s,%s,%s)"
SENSORID=901;
DBWAIT=10*60
lastdb=0


def fmttime(timefloat):
    return time.strftime(TIMEFORMAT,time.localtime(timefloat))

def button_callback(channel): # Being run when BTPIN is pulled high
    global LEDPIN
    global lastpush
    global t
    
    now=time.time()
    print(fmttime(now))
    if now - lastpush < 1: # Debouching
        print("whopsa, wait a moment")
        print(now-lastpush)
        return
    lastpush=now
    state=GPIO.input(LEDPIN)
    if state==0:
        GPIO.output(LEDPIN,GPIO.HIGH)
        turnofftimer = threading.Timer(ONTIME, turnoff)
        turnofftimer.start() 
        print("ON")
    else:
        turnoff()
        


def handleht(hum,temp,mintemp,maxtemp):
    global lcd
    global lastdb
    global payload
    now=time.time()
    if lastdb+DBWAIT < now:
        print("Store")
        payload+=1
        CUR.execute(SQL,(SENSORID,round(hum,2),104,99,payload))
        CUR.execute(SQL,(SENSORID,round(temp,2),116,99,payload))
        CONN.commit()
        lastdb=now
    print("Humidity :    {:4.1f} %".format(hum))
    print("Temperature : {:4.1f} °C".format(temp))
    lcd.disp(0,0,"Temp {:5.1f} oC".format(temp))
    lcd.disp(0,1,"     {:5.1f} - {:5.1f}".format(mintemp,maxtemp))
    lcd.disp(0,2,"Fukt {:5.1f} %".format(hum))
    lcd.disp(0,3,fmttime(now))
    
def turnoff():
    global LEDPIN
    print("OFF")
    print(fmttime(time.time()))
    GPIO.output(LEDPIN,GPIO.LOW)
    if not turnofftimer == None:
        turnofftimer.cancel() # Do now want to have a timer hanging around to turn off the led later on.
    
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
            try:
                
                
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
            except:
                print(fmttime(time.time()))
                #print("Problem reading DHT")
                pass
        time.sleep(1)
    


GPIO.setwarnings(False) # Ignore warning for now
#GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(BTPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)              # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(LEDPIN,GPIO.OUT) 
GPIO.output(LEDPIN,GPIO.LOW)                                        # Want to make sure we start in a known state
GPIO.add_event_detect(BTPIN,GPIO.RISING,callback=button_callback)   # Setup event on pin 10 rising edge
stopDHT=threading.Event()
DHTthread=threading.Thread(target = readDHT, args = (stopDHT, ))
DHTthread.start()
message = input("Press enter to quit\n\n") # Run until someone presses enter
stopDHT.set()
DHTthread.join()
turnoff()
GPIO.cleanup() # Clean up


