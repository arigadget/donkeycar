class ControllTS():
    '''
    This part is to control angle/throttle according to traffic sign.
    '''

    def __init__(self):
        self.new_angle = 0.0
        self.new_throttle = 0.0

    def run(self, mode, angle, throttle, traffic_sign):
        self.new_angle = angle
        self.new_throttle = throttle
        # temporary changing for debugging
        if mode == "user":
            #print('*** ', traffic_sign)
            if traffic_sign == 'stop':
                self.new_throttle = 0.0
        self.new_traffic_sign = None

        return self.new_angle, self.new_throttle, self.new_traffic_sign

