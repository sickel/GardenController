import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time,threading

lastpush=0
BTPIN=22
LEDPIN=18
t=None
ontime=15.0

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




GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(BTPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(LEDPIN,GPIO.OUT) # Want to make sure we start in a known state
GPIO.output(LEDPIN,GPIO.LOW)
GPIO.add_event_detect(BTPIN,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge
message = input("Press enter to quit\n\n") # Run until someone presses enter
GPIO.cleanup() # Clean up


