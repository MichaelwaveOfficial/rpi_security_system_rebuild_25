import os

class DeviceManagement(object):

    '''
        FileHandling class to seperate multiple functions concerned with managing the captures kept within the devices local storage, bunlding them together in one location.
    '''

    def __init__(self) -> None:
        
        # Initialise list that will store the images metadata.
        self.stored_images : list = []

        # Store value of the file order when displaying captures stored on screen.
        self.file_order : bool = False


    def sort_files(self, files : list[dict], reverse_order : bool = False) -> list[dict]:

        '''
        Sort list containing captures from newest to oldest from the order parameterised, OS natively sorts in order due to filenames date+time structure,
        meaning it is simple enough to reverse the list these entries are stored in. 

        :param: files - list of files to be sorted. 
        :param: reverse_order - Order required for files to be sorted into.
        :return: sorted_list - Sorted list of images.
        '''

        # Copy list, do NOT modify directly.
        sorted_list = files.copy()
        
        # If reverse order parameterised, reverse the list using .reverse() BIF.  
        if reverse_order:
            sorted_list.reverse()
        else:
            # Otherwise reutrn list in default order. 
            sorted_list.sort(
                key = lambda cap: cap['capture_date'] + cap['capture_time'],
            )

        # Return list of files in desired order. 
        return sorted_list
    

    def access_stored_captures(self, directory: str) -> list[dict[str, str]]:

        '''
        Access images stored locally on the device. By iterating over each file, it will accumulate the meta data associated
        with each image, appending it to a dictionary, forming the metadata for an image which can be rendered into a html template,
        sanitised which can provide useful output for the user. 

        :params: directory - Access the cameras capture directory attribute.
        :return: stored_images - list consisting of dictionaries containing an images metadata for later access. 
        (img = {'fullpath','filename','file_ext', 'capture_date'})
        '''

        # Loop over all image files found within the captures directory. 
        for file in os.listdir(directory):

            # Check the file extensions match those desired.
            if file.endswith(('.jpg', '.jpeg', '.png')):

                # Append the filename to the captures directory path.
                fullpath = os.path.join(directory, file)
                # Get the standalone filename (date) and the file extention.
                filename, file_ext = os.path.splitext(file)
                # Access just the date.
                capture_date = filename.split('_')[0]
                # Access the time. 
                capture_time = filename.split('_')[1]

                # Append the images data to the images dictionary. 
                self.stored_images.append({
                    # Full filepath.
                    'fullpath': fullpath,
                    # Standalone filename.
                    'filename': filename,
                    # Files extension.
                    'file_ext': file_ext,
                    # Date it was captured.
                    'capture_date': capture_date, 
                    # Time the capture was taken.
                    'capture_time' : capture_time,
                })

        # Return dictionary containing meta data associated with images.
        return self.stored_images
    

    def check_file_exhaustion(self, directory : str, file_limit : int) -> None:

        '''
            Check stored files, remove oldest captures in order to mitigate resource exhaustion, can be set by user. 

            :param: directory - Specified directory where files are stored. 
            :param: file_limit - Maximum number of files allowed within the devices local storage. 
            :return: N/A.
        '''

        try:

            files = sorted(os.listdir(directory), key=os.path.getmtime)

            for file in files[file_limit:]:
                fullpath = os.path.join(directory, file)
                os.remove(fullpath)
                print(f'Storage limits exceeded!\n {fullpath} has been deleted from the system to mitigate resource exhausiton!')

        except FileNotFoundError:
            print(f'Directory : {directory} not found!')
        except Exception as e:
            print(f'An error has occured: {e}')
