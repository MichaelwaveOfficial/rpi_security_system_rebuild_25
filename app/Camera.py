from .AppConfig import *
import cv2
import time
import json 
import os

class Camera(object):

    '''
    
    '''

    def __init__(self, INDEX : int, config_file : str):

        self.capture = cv2.VideoCapture(INDEX) 
        self.config_file = config_file

        self.default_values = {
            'motion_detecion' : {
                'sensitivity' : 50,
                'threat_escalation_timer' : 10,
                'maximum_threat_threshold' : 5,
                'regions_of_interest' : []
            },
            'stream_quality' : {
                'performance' : {
                    'framerate' : 60,
                    'resolution' : [1280, 720]
                },
                'quality' : {
                    'framerate' : 30,
                    'resolution' : [1920, 1080]
                }
            },
            'alert_settings' : {
                'toggle' : False,
                'frequency' : 600,
                'target_email' : 'example@email.com',
                'app_password' : 'password'
            },
            'storage_settings' : {
                'auto_resource_managment' : True,
                'content_type' : 'video'
            }
        }

        self.settings = self.load_settings()


    def load_settings(self):

        '''
            Load settings from the onboard Json file if it is in existence, else use default values. Ensure that 
                both the JSON and default dictionary values are merged to guarantee both are up to date, mitigating
                the chances of missing key value pairs. 
        '''

        if os.path.exists(self.config_file):

            with open(self.config_file, 'r') as config_file:

                print('Config file present, loading settings.')

                loaded_settings = json.load(config_file)

                merged_settings = self.recursive_update(self.default_values, loaded_settings)

                return merged_settings

        else:

            print('Config file not found, loading default values!')

            return self.default_values
    

    def save_settings(self):

        '''
            Save currently applied settings to a JSON file for later access and retrieval.
        '''

        with open(self.config_file, 'w') as config_file:
            json.dump(self.settings, config_file, indent=4)
            print('Settings saved successfully!')


    def recursive_update(self, settings, updated_values):

        '''
            Helper function to iterate through dictionary and its nested values leveraging recursion by calling itself until 
                all keys and their values have been iterated upon.
        '''

        for key, value in updated_values.items():

            if isinstance(value, dict) and key in settings:

                self.recursive_update(settings=settings[key], updated_values=value)

            else:

                settings[key] = value


    def update_settings(self, updated_values):

        '''
            Update settings with new values set by the user, save to the config file. 
        '''

        self.rescursive_update(self.settings, updated_values)
        self.save_settings()


    def fetch_current_settings(self):

        '''
            Helper function to return current settings stored within the JSON file.
        '''

        return self.settings

    
    def capture_frame(self):

        '''
            Method to capture a frame from supplied hardware.
        '''

        try:

            ret, frame = self.capture.read()

            if not ret:

                print('Camera could not be accessed') 

            return frame 

        except cv2.error as e:

            print(f'Hardware error: {e}')


    def fake_frames(self):

        '''
            Simple test function to mimic content streaming without camera hardware. 
        '''

        # Iterate over images.
        frames = [open(f'{str(TEST_PATH + f)}.jpg', 'rb').read() for f in ['1', '2', '3']]

        # Return list
        return frames[int(time.time()) % 3]
        
    
    def test_stream(self):
        
        '''
        
        '''

        yield b'--frame\r\n'

        while True:
            frame = self.fake_frames()
            yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'

    
    def stream_video(self):

        ''' '''
        
        while True:

            frame = self.capture_frame()

            yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'
        
    

    def enforce_fps(self, elapsed_time : int) -> None:

        '''
        Strictly enforce the specified framerate for the stream. Can be decreased to reduce computational load on the device. 

        :param: elapsed_time - Time passed from the inital start.
        '''

        # Calcuate the time required to retrieve next frame.
        timeout = (1 / self.settings['fps']) - elapsed_time

        # If calculated timeout greater than nothing. Pause time taken to fetch next frame.
        if timeout > 0:
            time.sleep(timeout)


    def __del__(self):

        '''
            Automatically invoked once camera object no longer in use for resource cleanup.
        '''

        self.capture.release()
        