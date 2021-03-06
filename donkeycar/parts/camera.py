import os
import time
import numpy as np
from PIL import Image
import glob
from donkeycar.utils import rgb2gray

class BaseCamera:

    def run_threaded(self):
        return self.frame

class CoralCameraGS(BaseCamera):
    '''
    Coral Camera for Tinker Edge T (5M Ominivision based camera) using gstreamer
    '''
    def run_pipeline(self):
        from gi.repository import GLib, GObject, Gst, GstBase

        SRC_WIDTH = 640
        SRC_HEIGHT = 480
        SRC_RATE = '30/1'
        SRC_ELEMENT = 'v4l2src'

        SINK_WIDTH = 640
        SINK_HEIGHT = 480
        SINK_ELEMENT = ('appsink name=appsink sync=false emit-signals=true '
                        'max-buffers=1 drop=true')
        SCREEN_SINK = 'glimagesink sync=false'
        FAKE_SINK = 'fakesink sync=false'

        SRC_CAPS = 'video/x-raw,format=YUY2,width={width},height={height},framerate={rate}'
        SINK_CAPS = 'video/x-raw,format=RGB,width={width},height={height}'
        LEAKY_Q = 'queue max-size-buffers=1 leaky=downstream'

        PIPELINE = '''
            {src_element} ! {src_caps} ! {leaky_q} ! tee name=t
            t. ! {leaky_q} ! {screen_sink}
            t. ! {leaky_q} ! videoconvert ! {sink_caps} ! {sink_element}
            '''
        src_caps = SRC_CAPS.format(width=SRC_WIDTH, height=SRC_HEIGHT, rate=SRC_RATE)
        sink_caps = SINK_CAPS.format(width=SINK_WIDTH, height=SINK_HEIGHT)
        screen_sink = FAKE_SINK

        pipeline = PIPELINE.format(
            leaky_q=LEAKY_Q,
            src_element=SRC_ELEMENT,
            src_caps=src_caps,
            sink_caps=sink_caps,
            sink_element=SINK_ELEMENT,
            screen_sink=screen_sink)

        self.pipeline = Gst.parse_launch(pipeline)
        self.appsink = self.pipeline.get_by_name('appsink')

        #self.loop = GObject.MainLoop()
        self.pipeline.set_state(Gst.State.PLAYING)

    def __init__(self, image_w=160, image_h=120, image_d=3, framerate=60):
        import gi
        gi.require_version('Gst', '1.0')
        gi.require_version('GstBase', '1.0')

        from gi.repository import GLib, GObject, Gst, GstBase
        #GObject.threads_init()
        Gst.init(None)

        self.w = image_w
        self.h = image_h
        self.running = True
        self.frame = None
        self.appsink = None

        CAMERA_INIT_QUERY_SYSFS_NODE = '/sys/module/ov5645_camera_mipi_v2/parameters/ov5645_initialized'
        try:
            with open(CAMERA_INIT_QUERY_SYSFS_NODE) as init_file:
                init_file.seek(0)
                init = init_file.read()
                if int(init) != 1:
                    raise Exception('Cannot find ov5645 CSI camera, ' +
                               'check that your camera is connected')
        except Exception as ex:
            print(ex)

        # Turn off autofocus
        AF_SYSFS_NODE = '/sys/module/ov5645_camera_mipi_v2/parameters/ov5645_af'
        with open(AF_SYSFS_NODE, 'w+') as sysfs:
            try: 
                self.sysfs.write('0')
                self.sysfs.flush()
            except:
                pass

    def init_camera(self):
        # initialize the camera and stream
        self.run_pipeline()
        self.poll_camera()
        print('Coral Camera loaded.. .warming camera')
 
    def update(self):
        self.init_camera()

        while self.running:
            self.poll_camera()

    def poll_camera(self):
        from gi.repository import GLib, GObject, Gst, GstBase

        sample = self.appsink.emit('pull-sample')

        buf = sample.get_buffer()
        result, mapinfo = buf.map(Gst.MapFlags.READ)
        #print('mapinfo', mapinfo)
        if result:
            caps = sample.get_caps()
            width = caps.get_structure(0).get_value('width')
            height = caps.get_structure(0).get_value('height')
            img = Image.frombytes('RGB', (width, height), mapinfo.data, 'raw')
            self.frame = img.resize((self.w, self.h))
        buf.unmap(mapinfo)
        return np.asarray(self.frame)

    def run_threaded(self):
        return np.asarray(self.frame)
    
    def shutdown(self):
        from gi.repository import GLib, GObject, Gst, GstBase

        self.running = False
        print('stopping Coral Camera')
        # Clean up.
        self.pipeline.set_state(Gst.State.NULL)
        #self.loop.quit()
        #while GLib.MainContext.default().iteration(False):
        #    pass
        time.sleep(.5)
        del(self.camera)


class CoralCameraCV(BaseCamera):
    '''
    Camera for Tinker Edge T(5M Ominivision based camera) using opencv
    '''
    def __init__(self, image_w=160, image_h=120, image_d=3, framerate=30):
        self.w = image_w
        self.h = image_h
        self.running = True
        self.frame = None

    def init_camera(self):
        import cv2
        # initialize the camera and stream
        # /dev/video0
        fn_video = 0
        self.camera = cv2.VideoCapture(fn_video)

        self.poll_camera()
        print('CoralCamera loaded.. .warming camera')
        time.sleep(2)

    def update(self):
        self.init_camera()

        while self.running:
            self.poll_camera()

    def poll_camera(self):
        import cv2

        #while True:
        #    self.ret , frame = self.camera.read()
        #    print("return: ", self.ret)
        #    if self.ret == True:
        #       break
        self.ret, frame = self.camera.read()
        frame = cv2.resize(frame, dsize=(160, 120))
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def run(self):
        self.poll_camera()
        return self.frame

    def shutdown(self):
        self.running = False
        time.sleep(.5)
        del(self.camera)


class PiCamera(BaseCamera):
    def __init__(self, image_w=160, image_h=120, image_d=3, framerate=20):
        from picamera.array import PiRGBArray
        from picamera import PiCamera
        
        resolution = (image_w, image_h)
        # initialize the camera and stream
        self.camera = PiCamera() #PiCamera gets resolution (height, width)
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="rgb", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.on = True
        self.image_d = image_d

        print('PiCamera loaded.. .warming camera')
        time.sleep(2)


    def run(self):
        f = next(self.stream)
        frame = f.array
        self.rawCapture.truncate(0)
        if self.image_d == 1:
            frame = rgb2gray(frame)
        return frame

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            if self.image_d == 1:
                self.frame = rgb2gray(self.frame)

            # if the thread indicator variable is set, stop the thread
            if not self.on:
                break

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('Stopping PiCamera')
        time.sleep(.5)
        self.stream.close()
        self.rawCapture.close()
        self.camera.close()

class Webcam(BaseCamera):
    def __init__(self, image_w=160, image_h=120, image_d=3, framerate = 20, iCam = 0):
        import pygame
        import pygame.camera

        super().__init__()
        resolution = (image_w, image_h)
        pygame.init()
        pygame.camera.init()
        l = pygame.camera.list_cameras()
        print('cameras', l)
        self.cam = pygame.camera.Camera(l[iCam], resolution, "RGB")
        self.resolution = resolution
        self.cam.start()
        self.framerate = framerate

        # initialize variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.on = True
        self.image_d = image_d

        print('WebcamVideoStream loaded.. .warming camera')

        time.sleep(2)

    def update(self):
        from datetime import datetime, timedelta
        import pygame.image
        while self.on:
            start = datetime.now()

            if self.cam.query_image():
                # snapshot = self.cam.get_image()
                # self.frame = list(pygame.image.tostring(snapshot, "RGB", False))
                snapshot = self.cam.get_image()
                snapshot1 = pygame.transform.scale(snapshot, self.resolution)
                self.frame = pygame.surfarray.pixels3d(pygame.transform.rotate(pygame.transform.flip(snapshot1, True, False), 90))
                if self.image_d == 1:
                    self.frame = rgb2gray(self.frame)

            stop = datetime.now()
            s = 1 / self.framerate - (stop - start).total_seconds()
            if s > 0:
                time.sleep(s)

        self.cam.stop()

    def run_threaded(self):
        return self.frame

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('stoping Webcam')
        time.sleep(.5)


class CSICamera(BaseCamera):
    '''
    Camera for Jetson Nano IMX219 based camera
    Credit: https://github.com/feicccccccc/donkeycar/blob/dev/donkeycar/parts/camera.py
    gstreamer init string from https://github.com/NVIDIA-AI-IOT/jetbot/blob/master/jetbot/camera.py
    '''
    def gstreamer_pipeline(self, capture_width=3280, capture_height=2464, output_width=224, output_height=224, framerate=21, flip_method=0) :   
        return 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=%d, height=%d, format=(string)NV12, framerate=(fraction)%d/1 ! nvvidconv flip-method=%d ! nvvidconv ! video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! videoconvert ! appsink' % (
                capture_width, capture_height, framerate, flip_method, output_width, output_height)
    
    def __init__(self, image_w=160, image_h=120, image_d=3, capture_width=3280, capture_height=2464, framerate=60, gstreamer_flip=0):
        '''
        gstreamer_flip = 0 - no flip
        gstreamer_flip = 1 - rotate CCW 90
        gstreamer_flip = 2 - flip vertically
        gstreamer_flip = 3 - rotate CW 90
        '''
        self.w = image_w
        self.h = image_h
        self.running = True
        self.frame = None
        self.flip_method = gstreamer_flip
        self.capture_width = capture_width
        self.capture_height = capture_height
        self.framerate = framerate

    def init_camera(self):
        import cv2

        # initialize the camera and stream
        self.camera = cv2.VideoCapture(
            self.gstreamer_pipeline(
                capture_width =self.capture_width,
                capture_height =self.capture_height,
                output_width=self.w,
                output_height=self.h,
                framerate=self.framerate,
                flip_method=self.flip_method),
            cv2.CAP_GSTREAMER)

        self.poll_camera()
        print('CSICamera loaded.. .warming camera')
        time.sleep(2)
        
    def update(self):
        self.init_camera()
        while self.running:
            self.poll_camera()

    def poll_camera(self):
        import cv2
        self.ret , frame = self.camera.read()
        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def run(self):
        self.poll_camera()
        return self.frame

    def run_threaded(self):
        return self.frame
    
    def shutdown(self):
        self.running = False
        print('stoping CSICamera')
        time.sleep(.5)
        del(self.camera)

class V4LCamera(BaseCamera):
    '''
    uses the v4l2capture library from this fork for python3 support: https://github.com/atareao/python3-v4l2capture
    sudo apt-get install libv4l-dev
    cd python3-v4l2capture
    python setup.py build
    pip install -e .
    '''
    def __init__(self, image_w=160, image_h=120, image_d=3, framerate=20, dev_fn="/dev/video0", fourcc='MJPG'):

        self.running = True
        self.frame = None
        self.image_w = image_w
        self.image_h = image_h
        self.dev_fn = dev_fn
        self.fourcc = fourcc

    def init_video(self):
        import v4l2capture

        self.video = v4l2capture.Video_device(self.dev_fn)

        # Suggest an image size to the device. The device may choose and
        # return another size if it doesn't support the suggested one.
        self.size_x, self.size_y = self.video.set_format(self.image_w, self.image_h, fourcc=self.fourcc)

        print("V4L camera granted %d, %d resolution." % (self.size_x, self.size_y))

        # Create a buffer to store image data in. This must be done before
        # calling 'start' if v4l2capture is compiled with libv4l2. Otherwise
        # raises IOError.
        self.video.create_buffers(30)

        # Send the buffer to the device. Some devices require this to be done
        # before calling 'start'.
        self.video.queue_all_buffers()

        # Start the device. This lights the LED if it's a camera that has one.
        self.video.start()


    def update(self):
        import select
        from donkeycar.parts.image import JpgToImgArr

        self.init_video()
        jpg_conv = JpgToImgArr()

        while self.running:
            # Wait for the device to fill the buffer.
            select.select((self.video,), (), ())
            image_data = self.video.read_and_queue()
            self.frame = jpg_conv.run(image_data)


    def shutdown(self):
        self.running = False
        time.sleep(0.5)



class MockCamera(BaseCamera):
    '''
    Fake camera. Returns only a single static frame
    '''
    def __init__(self, image_w=160, image_h=120, image_d=3, image=None):
        if image is not None:
            self.frame = image
        else:
            self.frame = np.array(Image.new('RGB', (image_w, image_h)))

    def update(self):
        pass

    def shutdown(self):
        pass

class ImageListCamera(BaseCamera):
    '''
    Use the images from a tub as a fake camera output
    '''
    def __init__(self, path_mask='~/mycar/data/**/*.jpg'):
        self.image_filenames = glob.glob(os.path.expanduser(path_mask), recursive=True)
    
        def get_image_index(fnm):
            sl = os.path.basename(fnm).split('_')
            return int(sl[0])

        '''
        I feel like sorting by modified time is almost always
        what you want. but if you tared and moved your data around,
        sometimes it doesn't preserve a nice modified time.
        so, sorting by image index works better, but only with one path.
        '''
        self.image_filenames.sort(key=get_image_index)
        #self.image_filenames.sort(key=os.path.getmtime)
        self.num_images = len(self.image_filenames)
        print('%d images loaded.' % self.num_images)
        print( self.image_filenames[:10])
        self.i_frame = 0
        self.frame = None
        self.update()

    def update(self):
        pass

    def run_threaded(self):        
        if self.num_images > 0:
            self.i_frame = (self.i_frame + 1) % self.num_images
            self.frame = Image.open(self.image_filenames[self.i_frame]) 

        return np.asarray(self.frame)

    def shutdown(self):
        pass
