class Control_traffic_sign():
    '''
    This part is to control angle/throttle according to traffic sign.
    '''

    def __init__(self):
        self.new_angle = 0.0
        self.new_throttle = 0.0
        self.stop_sign = False
        self.pause_sign = False
        self.timer = False
        self.ignore_timer = False

    def run(self, mode, angle, throttle, traffic_sign):
        import time
        self.new_angle = angle
        self.new_throttle = throttle

        if self.ignore_timer:
            print('ignore time')
            if(time.perf_counter() - self.timer_ignore > 5.0):
                self.ignore_timer = False
            else:
                return self.new_angle, self.new_throttle, None
        if self.stop_sign:
            if self.timer:
                self.end_time = time.perf_counter()
                if self.end_time - self.start_time > 3.0:
                    print('stop timeout')
                    self.stop_sign = False
                    self.timer = False
                    return self.new_angle, self.new_throttle, None
                else:
                    return self.new_angle, 0.0, 'stop'
        if self.pause_sign:
            if self.timer:
                self.end_time = time.perf_counter()
                if self.end_time - self.start_time > 3.0:
                    print('pause timeout')
                    self.pause_sign = False
                    self.timer = False
                    self.ignore_timer = True
                    self.timer_ignore = time.perf_counter()
                    return self.new_angle, self.new_throttle, None
                else:
                    return self.new_angle, 0.0, 'pause'

        # temporary changing for debugging
        if mode == "user":
            #print('*** ', traffic_sign)
            if traffic_sign == 'stop':
                self.stop_sign = True
                self.timer = True
                self.start_time = time.perf_counter()
                self.new_throttle = 0.0
            elif traffic_sign == 'slow':
                self.new_throttle = self.new_throttle * 0.7
            elif traffic_sign == 'pause':
                self.pause_sign = True
                self.timer = True
                self.start_time = time.perf_counter()
                self.new_throttle = 0.0
            elif traffic_sign == 'left':
                self.new_angle = -0.5
            elif traffic_sign == 'right':
                self.new_angle = 0.5

        print(traffic_sign, ' [', self.new_angle, ', ', self.new_throttle,']')
        self.new_traffic_sign = None

        return self.new_angle, self.new_throttle, self.new_traffic_sign
