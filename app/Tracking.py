import time


class ObjectTracking(object):

    '''
        Module to calculate each detections center points, their distances to one another and wether or not they 
            should be classed as separate. New detections will be assigned unique ID values. Each detection will be tracked and assigned
            a threat level which is reviewed until it is concerned a problem and processed. 
    '''


    def __init__(self, EUCLIDEAN_DISTANCE_THRESHOLD : int = 125, MAXIMUM_THREAT_LEVEL : int = 3, DEREGISTRATION_TIME : int = 10, ESCALATION_TIME : int = 10) -> None:
        
        '''
            Instantiate Object tracking module.

            Paramaters:
                * EUCLIDEAN_DISTANCE_THRESHOLD (int) : Distance between two points before they are classed as separate. 
                * MAXIMUM_THREAT_LEVEL (int) : Maximum threshold before a detection is considered a threat.
                * DEREGISTRATION_TIME (int) : Time taken in seconds before a detection is pruned to free up resources. 
                * ESCALATION_TIME (int) : Time taken in seconds for a detection to be present before its threat level is escalated.  
        '''
        
        # dictionary to hold detections data which can be used for IDs, bounding boxes and center points. 
        self.detections = {}

        # Assign unique ID values to each detection.
        self.ID_increment_counter : int = 0

        # Time taken for a detection to be deregistered.
        self.DEREGISTRATION_TIME = DEREGISTRATION_TIME

        # Minimum number of pixels between each center point before they are classed as new detections. 
        self.EUCLIDEAN_DISTANCE_THRESHOLD = (EUCLIDEAN_DISTANCE_THRESHOLD ** 2)

        # Maximum threat level allowed.
        self.MAXIMUM_THREAT_LEVEL = MAXIMUM_THREAT_LEVEL

        # Time taken to escalate a detections threat level. 
        self.ESCALATION_TIME = ESCALATION_TIME

    
    def update_tracker(self, detections : list[dict]) -> list[dict]:
        
        '''
            Update the tracking module by iterating over each detection, comparing center points with prior detections,
                determining whether to treat is as either new or pre-existing.

            Paramaters:
                * detections (list[dict]) : list of detection metadata dicitonaries.
            Returns:
                * detections (list[dict]) : list of parsed detection metadata dictionaries. 
        '''

        # Initial time detection was registered. 
        processed_at : float = time.time()

        # If none present, return early. 
        if len(detections) == 0:
            return self.detections

        # Iterate over detections parameterised. 
        for detection in detections:
            
            # Check if detection center point matches prior, return ID if so.
            matched_detection_ID = self.match_center_points(detection)

            if matched_detection_ID:
                # If ID returned matches, update current detection.
                self.update_detections(matched_detection_ID, detection, processed_at)
            else :
                # Otherwise, register new one.
                self.register_detection(detection, processed_at)
        
        # Check detections list, prune outdated.
        self.prune_old_detections(processed_at) 

        # Return parsed detections.
        return self.detections
       

    def register_detection(self, detection : dict, intial_time : float) -> None:

        '''
            Initialise fresh detection entry. 

            Paramaters:
                * detection (dict) : Detection encapsulating its data as key value pairs.
                * inital_time (float) : Time detection was registered.
        '''

        # Calculate detections center point.
        center_point = self.calculate_center_point(detection)

        # Append entry to detections. 
        self.detections[self.ID_increment_counter] = {
            'ID' : self.ID_increment_counter,
            'center_point_trajectory' : [center_point],
            'first_seen' : intial_time,
            'last_seen' : intial_time,
            'threat_level' : 0
        }
        
        # Increment ID counter for next detection.
        self.ID_increment_counter += 1

    
    def match_center_points(self, detection : dict) -> int | None:

        '''
            Compare previous and current center point values, if distance between is within the 
                threshold paramaters, return ID proving they are the same.
                Otherwise, return None as they are separate detections, handle accordingly.

            Paramaters:
                * detection (dict) : Detection encapsulating its data as key value pairs.
            Returns:
                * ID (int) | None : Return ID integer value if within threshold parameters. Return None otherwise. 
        ''' 

        # Calculate detections current center point. 
        current_center_point = self.calculate_center_point(detection)

        # Iterate over detection entries.
        for ID, previous_detection in self.detections.items():

            # Fetch previous center point (most recent within the list.)
            previous_center_point = previous_detection['center_point_trajectory'][-1]

            # Calculate distance between the pair.
            euclidean_distance_squared = self.measure_euclidean_distance(current_center_point, previous_center_point)

            # If that distance falls within the set threshold.
            if euclidean_distance_squared < self.EUCLIDEAN_DISTANCE_THRESHOLD:
                # Return detections ID value, they are the SAME!
                return ID
            
        # Return nothing, detection DO NOT match!
        return None


    def update_detections(self, detection_ID : int, detection : dict, processed_at : float) -> None:
        
        '''
            Update detections values if ID values are matched prior meaning that it is now of interest and
                is being monitored.

            Paramaters:
                * detection_ID (int) : Concerned detections ID value to fetch particular detection data for updates.
                * detection (dict) : Detection data dictionary to access key value pairs. 
                * processed_at (float) : Time that detection was being processed at.
            Returns:
                * None
        '''

        # Calculate detections current center point.
        center_point = self.calculate_center_point(detection)
        
        # Append new center point entry to the center points trajectory list.
        self.detections[detection_ID]['center_point_trajectory'].append(center_point)

        # Update last time detection was seen.
        self.detections[detection_ID]['last_seen'] = processed_at

        # Check detections current time exceeds the threat escalation timer before its level can be raised.
        if processed_at - self.detections[detection_ID]['first_seen'] > self.ESCALATION_TIME:
            self.detections[detection_ID]['threat_level'] += 1


    def prune_old_detections(self, processed_at : float) -> None:
        
        '''
            Check detections last seen time against the deregistration threshold, prune if exceeded to free up resources.

            Paramaters:
                * processed_at (float) : Time detection was being processed at.
            Returns:
                * None
        '''
        
        # Filter detections that exceed deregistration time.
        stale_detections = [ID for ID, detection in self.detections.items() if (processed_at - detection['last_seen']) > self.DEREGISTRATION_TIME]

        # Iterate over ID values within the stale_detections list.
        for ID in stale_detections:
            # Use ID values to delete detection entries.
            del self.detections[ID]
            self.ID_increment_counter -= 1

    
    def calculate_center_point(self, detection):

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

        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

        return int(center_x), int(center_y)


    def measure_euclidean_distance(self, p1, p2):

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
    