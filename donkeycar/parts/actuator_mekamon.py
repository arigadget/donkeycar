import time
import donkeycar as dk
import binascii
from struct import * # for 'pack'
from cobs import cobs

from gattlib import GATTRequester, GATTResponse

g_angle = 0

class MekamonSteering:
    def __init__(self):
        global g_angle
        g_angle = 0

    def run(self, angle):
        global g_angle
        g_angle = angle

    def shutdown(self):
        self.run(0) # stop

class MekamonThrottle:
    def calc_checksum(self, cmd):
        #ints = [ord(char) for char in cmd]
        ints = [int(char) for char in cmd]
        checksum = sum(ints)
        checksum %= 256 # roll over if bigger than 8b max
        checksum ^= 256 # twos complement
        checksum += 1 # why add 1?
        checksum %= 256 # roll over if bigger than 8b max
        #print ('checksum:',checksum)
        return checksum

    # mm_command produces hex for MM command from signed int inputs
    # this uses actual byte stuffing method
    def mm_command(self, intSeq):
        #print('intSeq:', intSeq)
        # build the command, append vars in hex string '\xff' format
        cmd = ''
        for x in intSeq:
            cmd += pack('b',x).decode() # b means treat as signed +- 128
        # COBS before the checksum and terminal byte
        cmd = cmd.encode('utf-8')
        cmd = cobs.encode(cmd)
        #print ('cobs encode: ', cmd)
        # checksum
        checksum = self.calc_checksum(cmd)
        #cmd += chr(checksum) # chr hexifies 0-255
        cmd += pack('B',checksum)
        # terminator
        #cmd += chr(0)
        cmd += pack('B', 0)
        # convert to hex literal string without \x
        cmd = binascii.hexlify(cmd)
        return cmd

    def ready_for_mekamon(self):
        init1 = [16] # 02101300
        msgOut = self.mm_command(init1)
        sendOut = binascii.unhexlify(msgOut)
        print("Sending: ", msgOut)
        for i in range(20):
            self.requester.write_cmd(0x000e, sendOut)
            time.sleep(0.5)

        init2 = [7, 1, 0] # 03070101
        msgOut = self.mm_command(init2)
        sendOut = binascii.unhexlify(msgOut)
        print("Sending: ", msgOut)
        for i in range(2):
            self.requester.write_cmd(0x000e, sendOut)
            time.sleep(0.5)

        print("ready for mekamon")
    
    def __init__(self):
        self.connect()
        name = self.requester.read_by_uuid("00002a00-0000-1000-8000-00805f9b34fb")[0]
        print("mekamon: ", name)
        # activate notification 
        self.requester.write_by_handle(0x000c, bytes([1, 0]))
        self.ready_for_mekamon()

    def connect(self):
        self.requester = GATTRequester("F7:9B:A8:A6:26:5F", False)
        print("Connecting...", end=' ')
        #sys.stdout.flush()

        self.requester.connect(True, channel_type="random")
        print("OK!")
        time.sleep(0.5)

    def run(self, throttle):
        global g_angle

        if throttle > 1 or throttle < -1:
            raise ValueError( "throttle must be between 1(forward) and -1(reverse)")
        if g_angle > 1 or g_angle < -1:
            raise ValueError( "angle must be between 1(right) and -1(left)")

        # -128 =< value =< 127
        fwd = dk.utils.map_range(throttle, -1.0, 1.0, -128, 127) + 1
        turn = dk.utils.map_range(g_angle,  -1.0, 1.0, -128, 127) + 1
        strafe = 0
        if fwd == 0:
            turn = 0
        print ('fwd: %d turn: %d strafe: %d' % (fwd, turn, strafe))

        msgOut = self.mm_command([6, 3, fwd, turn, strafe]) # 6=motion
        print("Sending: ", msgOut)

        msgOut = binascii.unhexlify(msgOut)
        self.requester.write_cmd(0x000e, msgOut)
        time.sleep(0.1)            

    def shutdown(self):
        self.run(0) #stop vehicle


