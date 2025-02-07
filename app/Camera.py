from .Config import *
import cv2
import time

class Camera(object):

    '''
    
    '''

    def __init__(self, INDEX : int = 0):

        self.capture = cv2.VideoCapture(INDEX) 

    
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
        