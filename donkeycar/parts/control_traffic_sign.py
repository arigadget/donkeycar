class Control_traffic_sign():
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
            elif traffic_sign == 'slow':
                self.new_throttle = self.new_throttle * 0.7
            elif traffic_sign == 'pause':
                self.new_throttle = 0.0
            else traffic_sign == 'left':
                self.new_angle = -1.0
            else traffic_sign == 'right':
                self.new_angle = 1.0

        print(traffic_sign, ' [', self.new_angle, ', ', self.new_throttle,']')
        self.new_traffic_sign = None

        return self.new_angle, self.new_throttle, self.new_traffic_sign
