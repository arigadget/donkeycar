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
        if mode == "local":
            print('*** ', traffic_sign)

        return new_angle, new_throttle

