import serial
import time

class Serial_sense():
    '''
    get sensor information from Arduino via serial USB interface
    '''

    def __init__(self, dev='/dev/ttyUSB0', baudrate=115200, poll_delay=0.03):
        self.status = b'F'
        self.dev = dev
        self.baudrate = baudrate
        self.serial_port = serial.Serial(self.dev, self.baudrate)
        time.sleep(1)
        self.poll_delay = poll_delay
        self.on = True

    def update(self):
        while self.on:
            self.poll()
            time.sleep(self.poll_delay)
                
    def poll(self):
        try:
            self.status = self.serial_port.read()
            #print(self.status)
        except:
            print('failed to read serial USB interface!!')
            
    def run_threaded(self):
        return self.status

    def run(self):
        self.poll()
        return self.status

    def shutdown(self):
        self.serial_port.close()
        self.on = False
