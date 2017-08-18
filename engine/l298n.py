'''
Created on 18.08.2017

@author: uschoen
'''
import time.sleep as sleep;
import RPi.GPIO as GPIO;
from time import localtime, strftime;
from datetime import datetime;
import threading;

class l298n(threading.Thread):
    '''
    classdocs
    '''
    speedCurrent=0;
    speedNext=0;
    speedNextTemp=0;
    directionCurrent="forward";
    directionNext="forward";
    motorSpeed=False;
    
    cfg={};
    log=False;
    
    def __init__(self,cfg,logger=False):
        
        threading.Thread.__init__(self)
        
        self.logger=logger;
        self.cfg=cfg;
        self.log("function","call __init__");
        self.estop();
        self.direction="forward";
        self.distance_impulse=0;
        
        '''
        GPIO settings
        '''
        ### forward
        GPIO.setup(self.cfg("motor_left"),GPIO.OUT);
        GPIO.output(self.cfg("motor_left"),0);
        ### reward
        GPIO.setup(self.cfg("motor_right"),GPIO.OUT);
        GPIO.output(self.cfg("motor_right"),0);
        ### PWM Speed Port
        GPIO.setup(self.cfg("motor_speed"),GPIO.OUT);
        self.motorSpeed=GPIO.PWM(self.cfg("motor_speed"),self.cfg("pwm_cycle"));
        self.motorSpeed.stop();        
        
        GPIO.setup(self.cfg("distance_port"),GPIO.IN);
        GPIO.add_event_detect(self.cfg("distance_port"),GPIO.RISING, callback=self.detect_distance_impulse(),boncetime=10);
        
    def detect_distance_impulse(self):
        '''
        Constructor
        '''
        self.log("function","call detect_distance_impulse");
        self.distance_impulse=self.distance_impulse+1;
        return;
    def run(self):
        while (1):
            self.check_direction();
            self.check_speed();
            sleep (0.01);
    def check_direction(self):
        '''
        Constructor
        '''
        self.log("function","call check_direction");
        if self.directionCurrent<>self.directionNext:
            if self.speedCurrent==0:
                self.setDirection(self.directionNext);
                self.speedNext=self.speedNextTemp;
            else:
                self.speedNextTemp=self.speedNext;
                self.speedNext=0;    
    def setDirection(self,direction):
        '''
        Constructor
        '''   
        self.log("function","call setDirection");
        if direction=="forward":
            GPIO.output(self.cfg("motor_right"),(1^self.cfg("invert_direction")));
            GPIO.output(self.cfg("motor_left"),(0^self.cfg("invert_direction")));          
        else:
            GPIO.output(self.cfg("motor_right"),(1^self.cfg("invert_direction")));
            GPIO.output(self.cfg("motor_left"),(0^self.cfg("invert_direction"))); 
        self.directionCurrent=direction;                 
        return;
        
    def check_speed(self):
        '''
        Constructor
        ''' 
        self.log("function","call check_speed");
        if self.speedCurrent>self.speedNext:
            self.speedCurrent-1;
            self.setSpeed(self.speedCurrent);
        elif self.speedCurrent<self.speedNext:
            self.speedCurrent+1;
            self.setSpeed(self.speedCurrent);
        return ;
    def setSpeed(self,speed):
        '''
        Constructor
        '''
        self.log("function","call setSpeed");
        if speed==0:
            self.motorSpeed.stop();
        else:
            self.motorSpeed.start(speed);
        self.speedNext=speed;
        return;
    def stop(self):   
        '''
        Constructor
        '''
        self.log("function","call stop");
        self.speedNext=0;
        return;
    def forward(self,speed):
        '''
        Constructor
        '''
        self.log("function","call forward");
        self.speedNext=speed;
        self.directionNext="forward";
        return;
    def reward(self,speed):
        '''
        Constructor
        '''
        self.log("function","call reward");
        self.speedNext=speed;
        self.directionNext="reward";
        return;
    def estop(self):
        '''
        Constructor
        '''
        self.log("function","call estop");
        self.set_speed(0);
        return;
    def getdistance(self):
        '''
        contructor
        '''
        self.log("function","call getdistance");
        distance=self.distance_impulse;
        self.distance_impulse=0;
        return distance;
    def log (self,level="unkown",messages="no messages"):
        if self.logger:
            dt = datetime.now()
            conf={}
            conf['package']=__name__
            conf['level']=level
            conf['messages']=str(messages)
            conf['time']=strftime("%d.%b %H:%M:%S", localtime())
            conf['microsecond']=dt.microsecond
            self.logger.write(conf) 

