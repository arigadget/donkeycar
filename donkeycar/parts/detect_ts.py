"""
detect_ts.py
Classes to detect traffic sign using tpu.
"""
class DetectTS():
    # Function to read labels from text files.
    def ReadLabelFile(self, file_path):
        with open(file_path, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        ret = {}
        for line in lines:
            pair = line.strip().split(maxsplit=1)
            ret[int(pair[0])] = pair[1].strip()
        return ret

    def __init__(self, model_path=None, label_path=None):
        from edgetpu.detection.engine import DetectionEngine
        # Initialize engine.
        #print('load traffic sign model')
        self.engine = DetectionEngine(model_path)
        self.labels = self.ReadLabelFile(label_path)
        
        self.on = True
        self.traffic_sign = None

    def inference_traffic_sign(self, image, angle, throttle):
        import time
        import numpy
        from PIL import Image

        self.new_angle = angle
        self.new_throttle = throttle

        # Run inference
        pilImg = Image.fromarray(numpy.uint8(image))
        start_time = time.perf_counter()
        ans = self.engine.detect_with_image(pilImg, threshold=0.7, keep_aspect_ratio=True,
                                          relative_coord=False, top_k=1)
        end_time =  time.perf_counter()
        #print('Inference time:{:.7}'.format(end_time - start_time))

        # Display result.
        if ans:
            for obj in ans:
                #print ('-----------------------------------------')
                if self.labels:
                    #print(self.labels[obj.label_id],'   ',obj.score)
                    traffic_sign = self.labels[obj.label_id]
                    if traffic_sign == "stop" :
                        print("stop")
                        self.new_throttle = 0.0
                    elif traffic_sign == "pause":
                        self.new_angle = 1.0
                    else:
                        self.new_throttle = throttle

    def update(self):
        while self.on:
            pass

    def run(self, image, angle, throttle):
        self.run_threaded(image, angle, throttle)

    def run_threaded(self, image, angle, throttle):
        self.new_angle = angle
        self.new_throttle = throttle
        if image is not None:
            self.inference_traffic_sign(image, angle, throttle)
        return self.new_angle, self.new_throttle

    def shutdown(self):
        self.on = False
        print('Stopping inference')
