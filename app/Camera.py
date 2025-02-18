from .AppConfig import *
import cv2
from ConfigManager import ConfigManager


class Camera(object):

    '''
        Functionality pertaining to the devices (Raspberry Pi) onboard camera. 
    '''

    def __init__(self, INDEX : int, config_manager : ConfigManager):

        '''
            Initialise an instance of the camera class.

            Paramaters:
                * INDEX (int) : index where device can be accessed, set to 0 by default in the AppConfig.py file.
                * config_manager (ConfigManager) : Instace of the ConfigManager class handling the settings. 
        '''

        # Camera location index.
        self.capture = cv2.VideoCapture(INDEX) 

        # Implement small delay to warm up the camera.
        self.warmup_camera()

        # Fetch properties of the camera capture.
        self.fps = self.capture.get(cv2.CAP_PROP_FPS) if self.capture.get(cv2.CAP_PROP_FPS) > 0 else 30
        self.frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_size = (self.frame_width, self.frame_height)
    
        # Config file accessed from parsed dir.
        self.config_manager = config_manager

        # Fetch device settings.
        self.settings = self.config_manager.load_settings()

    
    def warmup_camera(self, delay=2):

        ''' Iterate seconds to set delay, allowing camera to warmup. '''

        for _ in range(delay):
            self.capture.read()

    
    def capture_frame(self):

        '''
           Capture a frame from supplied hardware leveraging opencv.
        '''

        try:
            
            # Fetch status and frame from video capture object. 
            ret, frame = self.capture.read()

            # If unccessful, let user know.
            if not ret:
                print('Camera could not be accessed') 

            # Return frame for access. 
            return frame 

        except cv2.error as e:
            # Inform user of a cv2 error.
            print(f'Hardware error: {e}')

        
    def __del__(self):

        '''
            Automatically invoked once camera object no longer in use for resource cleanup.
        '''

        self.capture.release()
        