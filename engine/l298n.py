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
    
    
    def __init__(self,cfg,logger=False):
        
        threading.Thread.__init__(self)
        
        self.speedCurrent=0;
        self.speedNext=0;
        self.speedNextTemp=0;
    
        self.directionCurrent="forward";
        self.directionNext="forward";
        self.motorSpeed=False;
    
        self.logger=logger;
        self.cfg=cfg;
        self.log("function","call __init__");
       
        self.distance_impulse=0;
        
        '''
        GPIO settings
        '''
        ### forward
        GPIO.setup(self.cfg["motor_left"],GPIO.OUT);
        GPIO.output(self.cfg["motor_left"],0);
        ### reward
        GPIO.setup(self.cfg["motor_right"],GPIO.OUT);
        GPIO.output(self.cfg["motor_right"],0);
        ### PWM Speed Port
        GPIO.setup(self.cfg["motor_speed"],GPIO.OUT);
        self.motorSpeed=GPIO.PWM(self.cfg["motor_speed"],self.cfg("pwm_cycle"));
        self.motorSpeed.stop();        
        ### distance impulse
        GPIO.setup(self.cfg["distance_port"],GPIO.IN);
        GPIO.add_event_detect(self.cfg["distance_port"],GPIO.RISING, callback=self.__detectDistanceImpulse(),boncetime=10);
        self.log("info","l298 is init");
        return;
    def __detectDistanceImpulse(self):
        '''
        __detectDistanceImpulse
        '''
        self.log("function","call __detectDistanceImpulse");
        self.distance_impulse=self.distance_impulse+1;
        return;
    
    def run(self):
        '''
        run
        '''
        self.log("info","l298 is starting");
        while (1):
            self.__checkDirection();
            self.__checkSpeed();
            sleep (0.01);
            
    def __checkDirection(self):
        '''
        check_direction
        '''
        self.log("function","call check_direction");
        if self.directionCurrent<>self.directionNext:
            self.log("info","current direction is :%s, next deriction is:%s"% (self.directionCurrent,self.directionNext));
            if self.speedCurrent==0:
                self.__setDirection(self.directionNext);
                if self.speedNextTemp>0:
                    self.speedNext=self.speedNextTemp;
                    self.speedNextTemp=0;
            else:
                if self.speedNext>0:
                    self.log("info","can not change direction, set speed from %s to 0" %(self.speedCurrent));
                    self.speedNextTemp=self.speedNext;
                    self.speedNext=0;    
    def __setDirection(self,direction):
        '''
        __setDirection
        '''   
        self.log("function","call __setDirection");
        if direction=="forward":
            GPIO.output(self.cfg["motor_right"],(1^self.cfg["invert_direction"]));
            GPIO.output(self.cfg["motor_left"],(0^self.cfg["invert_direction"])); 
        else:
            GPIO.output(self.cfg["motor_right"],(1^self.cfg["invert_direction"]));
            GPIO.output(self.cfg["motor_left"],(0^self.cfg["invert_direction"])); 
        self.log("info","set diretion to %s" %(direction));         
        self.directionCurrent=direction;                 
        return;
    def __setPWM(self,speed):
        '''
        __setPWM
        '''
        self.log("function","call __setPWM");
        if speed==0:
            self.motorSpeed.stop();
            self.log("info","motor stop");
        else:
            self.motorSpeed.start(speed);
            self.log("info","set motor speed to %s"%(speed));  
        return;  
    def __checkSpeed(self):
        '''
        __check_speed
        ''' 
        self.log("function","call check_speed");
        if self.speedCurrent>self.speedNext:
            self.speedCurrent-1;
            self.log("debug","decrease speed to %s" %(self.speedCurrent));   
            self.__setPWM(self.speedCurrent);
        elif self.speedCurrent<self.speedNext:
            self.speedCurrent+1;
            self.log("debug","increase speed to %s" %(self.speedCurrent));   
            self.__setPWM(self.speedCurrent);
        return ;
    def setSpeed(self,speed):
        '''
        setSpeed
        '''
        self.log("function","call setSpeed");
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
        reward
        '''
        self.log("function","call reward");
        self.speedNext=speed;
        self.directionNext="reward";
        return;
    def estop(self):
        '''
        estop
        '''
        self.log("function","call estop");
        self.set_speed(0);
        return;
    def getdistance(self):
        '''
        getdistance
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

