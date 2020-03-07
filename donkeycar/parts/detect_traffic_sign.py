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
        import time
        from donkeycar.parts.camera import CoralCameraGS
        # coral camera
        self.image_w = 640
        self.image_h = 480
        self.image_d = 3
        self.cam = CoralCameraGS(image_w=self.image_w, image_h=self.image_h, image_d=self.image_d)
        print('Coral Camera loaded.. .warming camera')

        # Initialize engine.
        print('load traffic sign model')
        from edgetpu.basic import edgetpu_utils
        edge_tpus = edgetpu_utils.ListEdgeTpuPaths(edgetpu_utils.EDGE_TPU_STATE_NONE)
        print(edge_tpus[0])
        self.engine = DetectionEngine(model_path, edge_tpus[0])
        self.labels = self.ReadLabelFile(label_path)
        
        self.on = True
        self.traffic_sign = None

    def inference_traffic_sign(self, image):
        import time
        import numpy
        from PIL import Image

        self.traffic_sign = None
        # Run inference
        pilImg = Image.fromarray(numpy.uint8(image))
        start_time = time.perf_counter()
        ans = self.engine.detect_with_image(pilImg, threshold=0.8, keep_aspect_ratio=True,
                                          relative_coord=False, top_k=1)
        end_time =  time.perf_counter()
        print('TS: Inference time:{:.7}'.format(end_time - start_time))

        # Set result.
        if ans:
            for obj in ans:
                if self.labels:
                    #print(self.labels[obj.label_id],'   ',obj.score)
                    self.traffic_sign = self.labels[obj.label_id]
                    print('detect: ', self.traffic_sign)
            print('        ', self.labels[obj[0].label_id])        

    def update(self):
        while self.on:
            self.frame = self.cam.poll_camera()
            self.inference_traffic_sign(self.frame)
    
        self.cam.shutdown()

    def run_threaded(self):
        return self.traffic_sign

    def shutdown(self):
        import time
        self.on = False
        print('Stopping inference of traffic sign')
        time.sleep(.5)
        #del(self.camera)
