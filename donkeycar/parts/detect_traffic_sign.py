"""
detect_traffic_sign.py
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
        #Webcam
        import pygame
        import pygame.camera

        self.image_w = 160
        self.image_h = 120
        self.image_d = 3
        self.framerate = 20
        self.iCam = 1

        resolution = (self.image_w, self.image_h)
        pygame.init()
        pygame.camera.init()
        l = pygame.camera.list_cameras()
        print('cameras', l)
        self.cam = pygame.camera.Camera(l[iCam], resolution, "RGB")
        self.resolution = resolution
        self.cam.start()
        self.frame = None

        print('WebcamVideoStream loaded.. .warming camera')

        time.sleep(2)

        # Initialize engine.
        #print('load traffic sign model')
        self.engine = DetectionEngine(model_path)
        self.labels = self.ReadLabelFile(label_path)
        
        self.on = True
        self.traffic_sign = None

    def inference_traffic_sign(self, image):
        import time
        import numpy
        from PIL import Image

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
                if self.labels:
                    #print(self.labels[obj.label_id],'   ',obj.score)
                    self.traffic_sign = self.labels[obj.label_id]
                    if self.traffic_sign == "stop" :
                        print("stop")
                    else:
                        print(self.traffic_sign)

    def update(self):
        from datetime import datetime, timedelta
        import pygame.image
        while self.on:
            start = datetime.now()

            if self.cam.query_image():
                snapshot = self.cam.get_image()
                snapshot1 = pygame.transform.scale(snapshot, self.resolution)
                self.frame = pygame.surfarray.pixels3d(pygame.transform.rotate(pygame.transform.flip(snapshot1, True, False), 90))
 
                if image is not None:
                    self.inference_traffic_sign(self.frame)
 
            stop = datetime.now()
            s = 1 / self.framerate - (stop - start).total_seconds()
            if s > 0:
                time.sleep(s)

        self.cam.stop()

    def run_threaded(self):
        return self.traffic_sign

    def shutdown(self):
        self.on = False
        print('Stopping inference')
        time.sleep(.5)

