class SensorController():
    '''
    This part is to control throttle from ToF sensor on Arduino.

    command: 'F': Full throttle   100%
             'M': Medium           70%
             'S': Slow             40%
             'E': Emergency Stop    0%
    '''

    def __init__(self):
        self.power_dict = {b'\x00':0.0, b'F':100.0, b'M':70.0, b'S':40.0, b'E':0.0}

    def run(self, mode, ai_throttle, status):
        new_throttle = ai_throttle
        # temporary changing for debugging
        if mode != "local":
            power_rate = self.power_dict[status]
            new_throttle = new_throttle * power_rate

        print(power_rate)
        print(new_throttle)
        return new_throttle

