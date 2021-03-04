import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)

def jarakMobil(min, max):
    
    GPIO.setmode(GPIO.BOARD)
    TRIG = 11
    ECHO = 12
    
    jarakMinimal = min
    jarakMaksimal = max

    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)
    while True:
        GPIO.output(TRIG,False)
        print('Pengukuran dimulai')
        time.sleep(2)
        GPIO.output(TRIG,True)
        time.sleep(0.00001)
        GPIO.output(TRIG,False)
        
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            
        pulse_duration = pulse_end - pulse_start
        
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        if distance > jarakMinimal and distance 
                < jarakMaksimal :
            return True
        
GPIO.cleanup()