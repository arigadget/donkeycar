import time
import donkeycar as dk

g_angle = 0

class MekamonSteering:
    def __init__(self):
        global g_angle
        g_angle = 0

    def run(self, angle):
        global g_angle
        g_angle = angle

    def shutdown(self):
        self.run(0, 0, 0) # stop

class MekamonThrottle:
    def __init__(self):
        print("mekamon throttle")
 
    def run(self, throttle):
        global g_angle

        if throttle > 1 or throttle < -1:
            raise ValueError( "throttle must be between 1(forward) and -1(reverse)")
        if g_angle > 1 or g_angle < -1:
            raise ValueError( "angle must be between 1(right) and -1(left)")

        # -128 =< value =< 127
        fwd = dk.util.data.map_range(throttle, -1.0, 1.0, -128, 127)
        turn = dk.util.data.map_range(g_angle,  -1.0, 1.0, -128, 127)
        strafe = 0

        print('fwd: ', fwd, 'turn: ', turn)

    def shutdown(self):
        self.run(0, 0, 0) #stop vehicle
