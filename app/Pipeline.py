from .AppConfig import *
from .ConfigManager import ConfigManager
from .Camera import Camera 
from .Detection import ObjectDetection
from .Tracking import ObjectTracking
from .Managment import DeviceManagement

from collections import deque
from time import time 
import cv2


class VisionPipeline(object):

    '''
        Leverage singleton design pattern to ensure that objects are only instantiated once by providing access points throughout 
            the application.

        That way we can mitigate conflicting instances with different configurations, reduce computational load ++ promote
            extensibility and maintainability.
    '''

    # initialisation representation.
    _instance = None 


    def __new__(cls):

        '''
            If an instance does not exist of this class, create one and store it to keep it atomic.

            Returns:
                * VisionPipeline: Single, atomic instance of the VisionPipeline Class.
        '''

        if cls._instance is None:
            cls._instance = super(VisionPipeline, cls).__new__(cls) 
            cls._instance.initialise_pipeline()
        return cls._instance
    

    def __init__(self):

        '''
            Initialise an instance of this class if not yet already in existence. Helping to mitigate subsequent 
                instantiations. 
        '''
        
        if not hasattr(self, 'Initialised'):
            self.initialise_pipeline()
            self.initialised = True


    def initialise_pipeline(self):
        
        ''' Initialise the pipelines components. '''

        self.configuration_manager = ConfigManager(config_file=CAMERA_CONFIG_PATH, default_values=DEFAULT_CAMERA_CONFIG_DICT)
        self.camera = Camera(INDEX=INDEX, config_manager=self.configuration_manager)
        self.object_detection = ObjectDetection()
        self.object_tracking = ObjectTracking()
        self.device_management = DeviceManagement()

        ''' Buffer Variables. '''
        self.prev_frame = None
        self.clip_length = 5
        self.buffer_size = self.clip_length * self.camera.fps 
        self.pre_capture_buffer = deque(maxlen=self.buffer_size)
        self.post_capture_buffer = []
        self.motion_detected = False
        self.saved_pre_buffer = []
        self.counter = 0

        # Content type to discern whether device captures stills or video clips.
        self.content_type = str(self.configuration_manager.settings.get('content_type', 'stills'))

        # User set delay in seconds for alerts ++ captures. 
        self.frequency_delay = int(self.configuration_manager.settings.get('alert_settings').get('frequency'))

        # Boolean to determine whether stream running or not. 
        self.running = True

        # Timer when algorithm last triggered.
        self.last_captured = 0


    def generate_frames(self):

        '''
        Generator function concerned with handling the devices streaming capabilities.

        Yields:
            bytes: Multipart-encoded video frames suited to streaming to the web server.
        '''

        while self.running:

            ''' Read frames from the camera. '''

            # Read frame from the camera.
            frame = self.camera.capture_frame()

            # Fetch inital detections time in specified format. 
            detected_at = time.strftime(FORMATTED_FILENAME_DATE)

            if self.content_type == 'clips':
                # Preserve a buffer of copied frames for when a capture of interest comes around.
                self.pre_capture_buffer.append(frame.copy())

            ''' Detect motion leveraging motion detection utility. '''

            if self.prev_frame is not None:

                # Compare current and previous frames, assign first denoted var to access cv2 post processing frame.
                _, detection_bboxes = self.object_detection.detect_motion(self.prev_frame, frame) # Returns [{'x1' : int(x1), 'y1' : int(y1), 'x2' : int(x1 + w), 'y2' : int(y1 + h)}]

                ''' Use detection data to update tracker and provide ID values. '''

                # If parsed detection data is returned. 
                if detection_bboxes:

                    ''' Object Tracking // Annotation. '''

                    # Returns [{'x1', 'y1', 'x2', 'y2', 'ID', 'center_point_trajectory', 'first_seen', 'last_seen', 'threat_level'}]
                    tracked_detections = self.object_tracking.update_tracker(detection_bboxes)

                    print(tracked_detections)

                    ''' Annotate detections. '''

                    # Annotate the detection metadata.
                    annotated_frame = self.object_detection.annotate_detections(frame, tracked_detections)

                    ''' Handle capture accordingly. '''

                    if self.content_type == 'stills' and \
                        self.object_detection.trigger_capture(
                            self.last_captured,
                            self.frequency_delay, 
                            self.object_tracking.MAXIMUM_THREAT_LEVEL,
                            tracked_detections
                        ):

                        # If content type is set to stills, capture annotated frame and store.
                        self.object_detection.capture_still(annotated_frame, CAPTURE_UPLOADS_DIR, detected_at)

                    elif self.content_type == 'clips':
                        # Otherwise, freeze pre event buffer, start appending post event frame to post event buffer.
                        self.saved_pre_buffer = list(self.pre_capture_buffer)
                        # Empty post event buffer for use.
                        self.post_capture_buffer.clear()
                        # Counter set to buffer size to decrement. 
                        self.counter = self.buffer_size
                        # Motion has been detected!
                        self.motion_detected = True

                else:
                    # No detections, continue.
                    annotated_frame = frame 
            else: 
                # No frame for comparison.
                annotated_frame = frame

            # Prepare a previous copy for next interations motion detection operations. 
            self.prev_frame = frame.copy()

            ''' Capture clip of event. '''

            # If motion has been detected and content type concerned with capturing clips.
            if self.motion_detected and \
                self.content_type == 'clips' and \
                        self.object_detection.trigger_capture(
                            self.last_captured,
                            self.frequency_delay, 
                            self.object_tracking.MAXIMUM_THREAT_LEVEL,
                            tracked_detections
                        ):

                self.last_captured = time.time()
                
                # Decrement counter.
                self.counter -= 1
                # Add frame copies to post event buffer.
                self.post_capture_buffer.append(annotated_frame.copy())

                # If buffer size depleted.
                if self.counter <= 0:
                    
                    # Capture the video clip.
                    self.object_detection.capture_video(
                        self.saved_pre_buffer,
                        self.post_capture_buffer,
                        CAPTURE_UPLOADS_DIR,
                        self.camera.fps,
                        self.camera.frame_width,
                        self.camera.frame_height,
                        detected_at
                    )

                    # Resest motion detection operations.
                    self.motion_detected = False 
                    # Clear buffers. 
                    self.post_capture_buffer.clear()
            
            ''' Monitor system resources, manage accordingly. '''

            ''' Handle frames to be streamed to the web server. '''

            # Encode frame for streaming.
            success, buffer = cv2.imencode('.jpg', annotated_frame)
            if not success:
                continue
            
            # Yield frame in multipart format.
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                buffer.tobytes() +
                b'\r\n--frame\r\n')


    def stop_stream(self):

        ''' Helper function to handle the streams termination. '''
        self.running = False

# Instantiate single instance of this pipeline for access in routes.py
stream_pipeline = VisionPipeline()
