import time
import donkeycar as dk
import binascii
from struct import * # for 'pack'
from cobs import cobs

from gattlib import GATTRequester, GATTResponse

class MekamonController:
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
        cmd = b""
        for x in intSeq:
            cmd += pack('b',x)      # b means treat as signed +- 128
        # COBS before the checksum and terminal byte
        #cmd = cmd.encode('utf-8')
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

    def send_cmd(self, envelop, times, interval):
        msgOut = self.mm_command(envelop)
        sendOut = binascii.unhexlify(msgOut)
        print("Sending: ", msgOut)
        for i in range(times):
            self.requester.write_cmd(0x000e, sendOut)
            time.sleep(interval)

    def ready_for_mekamon(self):
        # 0210
        self.send_cmd([16], 20, 0.5)
        #
        #self.send_cmd([13, 45, 110, 75, 55, 70, 90, 2, 36, 0, 0], 1, 0) 
        # 03070101
        self.send_cmd([7, 1, 0], 2, 0.5) 
        #
        #self.send_cmd([60, 0, 100], 1, 0)
        self.send_cmd([6, 0, 0, 0], 1, 0)

        print("ready for mekamon")
    
    def ready_for_mekamon2(self):
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
        self.fwd = 0
        self.turn = 0
        self.running = True

    def connect(self):
        self.requester = GATTRequester("F7:9B:A8:A6:26:5F", False)
        print("Connecting...", end=' ')
        #sys.stdout.flush()

        self.requester.connect(True, channel_type="random")
        print("OK!")
        time.sleep(0.5)

    def mm_controller(self, fwd, turn):
        strafe = 0
        print ('fwd: %d turn: %d strafe: %d' % (fwd, turn, strafe))

        msgOut = self.mm_command([6, 3, fwd, turn, strafe]) # 6=motion
        #print("Sending: ", msgOut)
        msgOut = binascii.unhexlify(msgOut)
        self.requester.write_cmd(0x000e, msgOut)
        #time.sleep(0.1)            

    def update(self):
        while self.running:
            self.mm_controller(self.fwd, self.turn)

    def run_threaded(self, angle, throttle):
        self.angle = angle
        if self.angle == None:
            self.angle = 0
        self.throttle = throttle

        if self.throttle > 1 or self.throttle < -1:
            raise ValueError( "throttle must be between 1(forward) and -1(reverse)")
        if self.angle > 1 or self.angle < -1:
            raise ValueError( "angle must be between 1(right) and -1(left)")

        # -128 =< value =< 127
        if self.throttle >= 0:
            self.fwd = dk.utils.map_range(self.throttle, 0, 1.0, 0, 127)
        else:
            self.fwd = dk.utils.map_range(self.throttle, -1.0, 0, -128, 0)
        if self.angle >= 0:
            self.turn = dk.utils.map_range(self.angle, 0, 1.0, 0, 127)
        else:
            self.turn = dk.utils.map_range(self.angle, -1.0, 0, -128, 0)

    def run(self, angle, throttle):
        self.run_threaded(angle, throttle)
        self.mm_controller(self.fwd, self.turn)

    def shutdown(self):
        self.run(0, 0) #stop vehicle
        self.running = False
        #self.requester.disconnect()
            


