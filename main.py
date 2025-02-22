#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color)
from pybricks.tools import  wait, StopWatch

from pybricks import version
import struct

ARM = 1
INTAKE = 2

EVENT_PATH = "/dev/input/event4"

# If your robot is driving backwards due to motor orientation being different set DRIVE_DIRECTION to -1:
DRIVE_DIRECTION = 1
ARM_DIRECTION = 1

# Arm speed is a value from 0-1 that is multiplied by the input value for the arm movement.
# 1 is default, but you can lower it for better control. Example 0.5 runs at half speed, .75 at 3/4
ARM_SPEED = 1   

# Declare motors 
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
arm_motor = Motor(Port.A)
autodone = False
# Defining variables that will store the dc values for the motors
drive = 0
steer = 0
arm = 0
print(version)

################
#     AUTO     #
################
#Enter  = ARM or = INTAKE 
BALL_GRABBER_TYPE = ARM


################
#   ARM ROBOT  #
################
def auto_arm():
    # Example
    #Maximum speed is 1050 for a large (drive) motor and 1560 for a medium (arm/intake) motor.
    arm_motor.run_until_stalled(300, then=Stop.COAST, duty_limit=None)
    wait(2200) #2.5 seconds
    # drive forward # 0-100 percent speed
    left_motor.dc(100) 
    right_motor.dc(100) # run right motor slower to correct turn
    wait(2200) #2.5 seconds

    #put arm down
    arm_motor.dc(-100) # 0-100 percent speed
    wait(100) #1/4 second
    arm_motor.stop()

    # drive backward # 0-100 percent speed
    left_motor.dc(-100) # drive backward
    right_motor.dc(-100) # run right motor slower to correct turn
    wait(2200) #2.5 seconds

    #put arm up
    arm_motor.dc(100)
    wait(100)
    arm_motor.stop()

    #leave these commands 
    arm_motor.stop()
    left_motor.stop()
    right_motor.stop()

################
#    INTAKE    #
################

def auto_intake():
    # Example
    #Maximum speed is 1050 for a large (drive) motor and 1560 for a medium (arm/intake) motor.

    #run arm motor
    arm_motor.dc(100) # 0-100 percent speed

    # drive forward # 0-100 percent speed
    left_motor.dc(100) 
    right_motor.dc(100) # run right motor slower to correct turn
    wait(2200) #2.5 seconds

    # drive backward # 0-100 percent speed
    left_motor.dc(-100) # drive backward
    right_motor.dc(-100) # run right motor slower to correct turn
    wait(2200) #2.5 seconds


    #leave these commands 
    arm_motor.stop()
    left_motor.stop()
    right_motor.stop()



#########
# Setup #
#########

# This function scales a range of values from source_range (typically 0-255) to target_range (for instance -100-100),
# where 0 is -100, 255 is 100, and all inbetween values are scaled porportionally
# example: scale(source(0,255), (-100-100))
def scale(source, source_range, target_range):
    return (float(source-source_range[0]) / (source_range[1]-source_range[0])) * (target_range[1]-target_range[0])+target_range[0]

# Open the Gamepad event file:
infile_path = EVENT_PATH

#EONET Errors on the next line may also be caused by the controller not being turned on or connected
in_file = open(infile_path, "rb")
# Read from the file
FORMAT = 'llHHI'    
EVENT_SIZE = struct.calcsize(FORMAT)

#############
# Main loop #
#############

while True:
    (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, in_file.read(EVENT_SIZE))
    #print(ev_type,code,value)
    # Read analog stick values    
    if ev_type == 3: # Stick or trigger moved
        
        if code == 1: # Left stick y axis
            drive = scale(value, (0,255), (100,-100)) # Scale input from 0-255 to -100-100 for the motor
        if code == 3: # Right stick x axis
            steer = scale(value, (0,255), (100, -100)) # Scale input from 0-255 to -100-100 for the motor
        if code == 2: # Left trigger axis
            arm = value / 2
        if code == 5: # Left trigger axis
            arm = -value / 2

    if ev_type == 1: # Button pressed
        if code == 310 and value == 1:
            print("L1 Pressed!")
        if code == 310 and value == 0:
            print("L1 Released")
        if code == 305:
            #print("Red Circle")
            if autodone == False:
                if BALL_GRABBER_TYPE == INTAKE:
                    auto_intake()
                if BALL_GRABBER_TYPE == ARM:
                    auto_arm()
                autodone = True

    
    # Set motor voltages. 
    left_motor.dc(DRIVE_DIRECTION * (drive - steer))
    right_motor.dc(DRIVE_DIRECTION * (drive + steer))
    arm_motor.dc(ARM_DIRECTION  * arm * ARM_SPEED)

in_file.close()
