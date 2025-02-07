import cv2
import numpy as np

'''

    Utilities pertaining to annotating and estimating a detections metadata. 

'''

def annotate_bbox_corners(
        frame : np.ndarray,
        detection : dict,
        colour=(10, 250, 10),
        size_factor=0.1,
        thickness_factor=0.01
    ) -> np.ndarray:
    
    '''
        Dynamically annotate a given detection adjusting the size and border radius of the annotated bounding box in relativity to 
        the detections size. 

        Paramaters: 
            * frame : np.ndarray -> frame to be drawn upon.
            * detection : dict -> detection dictionary containing desired values to plot data points.
            * colour : tuple -> BGR values to determine annotation colour. 
            * size_factor : float -> Scaling factor relative to detection size. 
            * thickness_factor : float -> Line thickness factor relative to detection size. 
           
        Returns:
            * annotated_frame : np.ndarray -> Annotated frame with a detections given bounding box. 
    '''

    # Initalise minimum and maximum contraints.
    min_corner_radius, max_corner_radius = 5, 30
    min_thickness, max_thickness = 1, 5

    # Fetch detection bounding box values, typecast to full integer values. 
    x1, y1, x2, y2 = int(detection['x1']), int(detection['y1']), int(detection['x2']), int(detection['y2'])

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

    return frame


def annotate_center_point_trail(
        frame,
        detection,
        colour=(180, 50, 50),
        thickness=8
    ):

    if 'center_points_history' not in detection:
        return frame

    for x in range(1, len(detection['center_points_history'])):

        cv2.line(
            frame,
            detection['center_points_history'][x - 1],
            detection['center_points_history'][x],
            colour,
            thickness
        )

    return frame
    

def calculate_center_point(detection):

    '''
        Simple function to calculate the center point of a given detection. This can be useful for both 
        annotation and tracking purposes. 

        Paramaters:
            * bbox : dict -> the detections metadata to calculate the center point. 

        Returns: 
            * center_x, center_y : tuple -> two floating point values representing the detections center 
                on the x and y axis. 

    
    '''

    x1, y1, x2, y2 = int(detection['x1']), int(detection['y1']), int(detection['x2']), int(detection['y2'])

    center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2

    return int(center_x), int(center_y)


def measure_euclidean_distance(p1, p2):

    '''
        Function to measure the straight-line distance between two points. Gets the sqaure values of the inputs and sqaures the output
            to help reduce computation. 

        Paramaters:

            * p1 : tuple -> (x1, y1), detection start position.
            * p2 : tuple -> (x2,y2), detection end position.

        Returns:

            * euclidean_distance : float -> distance between one position and another. 
    '''

    return ( p1[0] - p2[0] ) **2 + ( p1[1] - p2[1] ) **2
