import cv2 
import os
import numpy as np
import yagmail
import yagmail.error
from AppConfig import *
from time import time


class ObjectDetection(object):

    '''
        Utilities leveraging more traditional computer vision techniques to mitigate over exhaustion of the pi due to its resource constraints
            whilst running in real time. 

        On top of this, helper functions pertaining to the handling of detections can also be found within this module. 
    '''

    def __init__(self):
        pass


    def annotate_bbox_corners(
            self,
            frame : np.ndarray,
            detection : dict,
            colour=(10, 250, 10),
            size_factor=0.1,
            thickness_factor=0.01,
            font = cv2.FONT_HERSHEY_SIMPLEX,
            font_scale = 1.25,
            font_thickness = 3,
            font_color = (0, 255, 0),
            bg_colour = (0, 0, 0),
            padding=10,
            border_radius=6,
        ) -> np.ndarray:
        
        '''
            Dynamically annotate a given detection adjusting the size and border radius of the annotated bounding box in relativity to 
            the detections size. 

            Paramaters: 
                * frame ( np.ndarray) : Frame to be annotated upon.
                * detection (dict) : Detection containing data to be digested and visualised. 
                * colour (tuple) : Bbox corner colours.
                * size_factor (float) : Size of the corners.
                * thickness_factor (float) : Thickness of the corners.
                * font (str) : cv2 font type
                * font_scale (float) : Scaling of the font.
                * font_thickness (int) : Fonts thickness to increase legibility.
                * font_color (tuple) : Colour of the font.
                * bg_colour (tuple) : Font annotations background colour,
                * padding (int) : Padding within the font annotation label.
                * border_radius (int) : General border radius for bbox corners and label.
            
            Returns:
                * annotated_frame (np.ndarray) : Annotated frame with a detections given bounding box and metadata labelled. 
        '''

        # Initalise minimum and maximum contraints.
        min_corner_radius, max_corner_radius = 5, 30
        min_thickness, max_thickness = 1, 5

        # Fetch detection bounding box values, typecast to full integer values. 
        x1, y1, x2, y2, ID, threat_level = detection.get('x1'), detection.get('y1'), detection.get('x2'), detection.get('x2'), str(detection.get('ID')), str(detection.get('threat_level'))
        
        # Calculate detection dimensions.
        detection_width = x2 - x1
        detection_height = y2 - y1
        detection_size = min(detection_width, detection_height)

        # Dynamically calculate a detections line thickness and corner radius for annotation.
        detection_corner_radius = max(min(int(detection_size * size_factor), max_corner_radius), min_corner_radius)
        detection_thickness = max(min(int(detection_size * thickness_factor) * 2, max_thickness), min_thickness)

        ''' Bounding Box Corners. '''

        # Top left arc.
        cv2.ellipse(
            frame,
            (x1 + detection_corner_radius, y1 + detection_corner_radius),
            (detection_corner_radius, detection_corner_radius),
            0, 180, 270,
            colour,
            detection_thickness
        )
        
        # Bottom left arc.
        cv2.ellipse(
            frame,
            (x1 + detection_corner_radius, y2 - detection_corner_radius),
            (detection_corner_radius, detection_corner_radius),
            0, 90, 180,
            colour,
            detection_thickness
        )

        #Top right arc.
        cv2.ellipse(
            frame,
            (x2 - detection_corner_radius, y1 + detection_corner_radius),
            (detection_corner_radius, detection_corner_radius),
            0, 270, 360,
            colour,
            detection_thickness
        )

        # Botton right arc.
        cv2.ellipse(
            frame,
            (x2 - detection_corner_radius, y2 - detection_corner_radius),
            (detection_corner_radius, detection_corner_radius),
            0, 0, 90,
            colour,
            detection_thickness
        )

        # Labels data to be presented. 
        data_annotation = f'ID : {ID}, Threat Level: {threat_level}'

        # Dynamically fetch height and width of the text.
        (text_width, text_height), _ = cv2.getTextSize(data_annotation, font, font_scale, font_thickness)

        # Height and width of the detections bounding box. 
        box_width = text_width + 2 * padding
        box_height = text_height + 2 * padding

        # Add the text on top of the background
        text_position = (x1 + padding, y1 + box_height - padding)

        # Draw the rounded rectangle (background)
        cv2.rectangle(
            frame,
            (x1 + border_radius, y1),  # Top-left inner corner
            (x1 + box_width - border_radius, y1 + box_height),  # Bottom-right inner corner
            bg_colour,
            -1  # Fill the rectangle
        )
        cv2.rectangle(
            frame,
            (x1, y1 + border_radius),
            (x1 + box_width, y1 + box_height - border_radius),
            bg_colour,
            -1
        )
        # Append text annotation to the frame.
        frame = cv2.putText(
            frame,
            data_annotation,
            text_position,
            font,
            font_scale,
            font_color,
            font_thickness
        )

        # Return fully annotated frame.
        return frame


    def process_frame(self, frame : np.ndarray) -> np.ndarray:

        ''' preprocess frame before it is analysed further. '''

        # Convert the frame to greyscale to reduce colours channels, in turn reducing processing.
        frame_greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply gaussian filter to reduce noise in an attempt to mitigate false positives. 
        return cv2.GaussianBlur(frame_greyscale, (21, 21), 0)


    def detect_motion(self, prev_frame : np.ndarray, curr_frame : np.ndarray, binarisation_threshold : int = 25, min_contour_area : int = 500) -> tuple[np.ndarray, list[np.ndarray]]:

        ''' Detect motion in frame utilising traditional computer vision techniques. '''

        bboxes = []

        # Check frames passed are not None Type. Raise exception if they are. 
        if curr_frame is None or prev_frame is None:
            return ValueError('Provided frames were returned as None!')

        # Compute absolute difference between current and previous frames. 
        frame_difference = cv2.absdiff(prev_frame, curr_frame)

        # Apply a binary threshold to fetch regions with significant change within the frame.
        _, frame_thresholded = cv2.threshold(frame_difference, binarisation_threshold, 255, cv2.THRESH_BINARY)

        # Dilate on the thresholded frame to fill in the gaps and solidify contour areas.
        frame_dilation = cv2.dilate(frame_thresholded, None, iterations=3)

        # Fetch regions in the frame where motion has been detected. 
        contours, _ = cv2.findContours(frame_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Store list of detected motion areas.
        filtered_contours = [contour for contour in contours if cv2.contourArea(contour) > min_contour_area]

        # Iterate over the filtrated detections.
        for contour in filtered_contours:
            
            # Use opencv to draw a bounding box around the detected contour, unpack its values. 
            x1, y1, w, h = cv2.boundingRect(contour)

            # Append these values to a dictionary for each detection. Convert to x1, y1, x2, y2 format.
            detection = {'x1' : int(x1), 'y1' : int(y1), 'x2' : int(x1 + w), 'y2' : int(y1 + h)}

            # Add to bboxes list.
            bboxes.append(detection)

        # Return process frame and parsed bounding boxes
        return frame_dilation, bboxes


    def annotate_detections(self, frame : np.ndarray, contours : list[np.ndarray]) -> np.ndarray:

        ''' Iterate over the passed frames, their associated areas where motion has been detected and annotate that movement. '''

        # Create a copy of the frame for operating upon. 
        annotated_frame = frame.copy()

        # Iterate each detections contours.
        for detection in contours:

            # Annotate a bounding boxes corners onto the detection within the frame.
            annotated_frame = self.annotate_bbox_corners(annotated_frame, detection)

        return annotated_frame

    
    def send_email_alert(self, media, max_retries : int = 3, secs_delay : int = 10) -> None:

        ''' 
            Uses envinronment variables to send an email from a given gmail account to the users recipient address with an alert
                encapsulating data about the detection and the media where it has been captured.

            Paramaters:
                * media (np.ndarray | mp4 video) : Parsed media wether it is a single frame acting as a still image 
                    or a processed mp4 video of the event. 
                * max_retries (int) : Number of tries before operation is terminated. 
                * secs_delay (int) : Number of seconds until an attempt to resend the email if unsuccessful is made. 

            Returns:
                * None : Returns early if operation successful. 
        '''

        # Fetch environment variables.
        app_email = os.getenv('APP_EMAIL')
        app_password = os.getenv('APP_PASSWORD')
        target_email = os.getenv('TARGET_EMAIL')

        # If not all environment variables are present, raise this issue with user. 
        if not all([app_email, app_email, target_email]):
            raise ValueError('Missing essential email configurations from environment variables file.')

        # Make an attempt until max retries threshold met.
        for attempt in range(max_retries + 1):

            try:
                
                # Create a yagmail SMTP client.
                yag_client = yagmail.SMTP(app_email, app_password)

                # Email subject. 
                subject = f'Security Alert: Threat detected'

                # Email contents.
                contents = f'Your Raspberry Pi has detected a threat at {time.strftime("%Y-%m-%d %H:%M:%S")}'

                # Email object.
                yag_client.send(
                    to=target_email,
                    subject=subject, 
                    contents=contents,
                    attachments=media
                )

                # Return early if successful.
                return

            except (yagmail.YagConnectionClosed, yagmail.YagAddressError):
                
                # If max tries met, raise error with user.
                if attempt == max_retries:
                    raise RuntimeError(f'Failed to send email alert after {max_retries} attempts.')
                
                # Delay next attempt.
                time.sleep(secs_delay)


    def capture_video(
            pre_buffer : list,
            post_buffer : list,
            directory : str,
            frame_rate : int,
            frame_width : int,
            frame_height : int,
            captured_at : str,
            codec : str = 'mp4v'
        ) -> bool:

        '''
            Combines both pre and post detection buffers if content type set to video captures. That way, the combined frames can form 
                a full list of frames which can then be processed and written out into an mp4 video for the users convenience.

            Paramaters:
                * pre_buffer (deque) : Deck limited to specified length, always capturing set amount of frames for when an
                    event will eventually occur, storing the events leading to it. 
                * post_buffer (list) : Initialised and parsed once event has taken place, later to be appended to the pre_buffer, 
                    forming a whole video.
                * directory (str) : Directory where video clip will be stored. 
                * frame_rate (int) : Frame rate parsed from the capture object. 
                * frame_width (int) : Frame width parsed from the capture object. 
                * frame_height (int) : Frame height parsed from the capture object. 
                * captured_at (str) : Time event was captured at.
                * codec (str) : Chosen video format type. 

            Returns:
                * (bool) : Boolean to confirm status of the operation and its success status.
        '''

        # Create directory if it does not exist. 
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Join the desired directory and the filename to save capture.
        filename = os.path.join(directory, f'{captured_at}')

        # Ensure both buffers are appropriately type casted as lists. 
        frames = list(pre_buffer) + list(post_buffer)

        # Initialise fourcc object with the desired codec setting.
        fourcc = cv2.VideoWriter_fourcc(*codec)

        # Ouput object where frames will be written to. 
        output = cv2.VideoWriter(filename, fourcc, frame_rate, (frame_width, frame_height))

        try:
            
            # Iterate over each frame in frames list representing video.
            for frame in frames:

                # If frame is valid.
                if frame is not None:
                    # Write that to output.
                    output.write(frame)
            
            # Return true when operation completed successfully. 
            return True

        except Exception as e:
            print(f'Error : Failed to write frames to video!\n{e}')
            return False
        finally:
            # Always cleanup resources. 
            output.release()
            print(f'Clip captured and saved to {directory}')


    def capture_still(self, frame : np.ndarray, directory : str, formatted_date : str) -> None:

        '''
            Save captured frames to the devices local storage. Simultaneouly checking for resource exhaustion, removing oldest files that exceed the set limit. 

            :param: frame - Desired frame to be saved, capturing perpetrators.
            :param: directory - Specified directory where the captured frame can be written to.
            :param: formatted_date - Format of the date to be appended to the filename.
            :return: N/A
        '''

        # Create directory if it does not exist. 
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Join the desired directory and the filename to save capture.
        filename = os.path.join(directory, f'{formatted_date}.jpg')

        # Write capture to directory with native filename.
        cv2.imwrite(f'{os.path.join(directory, filename)}.jpg', frame)
        

    def trigger_capture(self, last_captured : float, delay : float, max_threat : int, detections : list[dict]) -> bool:

        '''
            Filtrate detections of concern once time delay set by user has been exceeded and the detections threat level exceeds
                the set limit. 

            Paramaters:
                * last_captured (float) : Last time an event occured.
                * delay (float) : Delay in seconds until another event should be captured. 
                * detections (list[dict]) : Detections to access their threat level to be reviewed against
                    the set threshold.
        '''

        # Fetch current time of invocation.
        current_time = time.time()

        # Check if timer subceeds delay threshold.
        if current_time - last_captured < delay:
            return False 
        
        # Check if any detection exceeds the threat threshold
        if any(detection.get('threat_level', 0) > max_threat for detection in detections):
            return True

        return False
    