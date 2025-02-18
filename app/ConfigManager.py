import json
import os


class ConfigManager(object):

    def __init__(self, config_file : str, default_values : dict):

        '''
            Initialise an instance of the applications configuration manager.

            Paramaters:
                * config_file (str) : Path to the JSON configuration file containing device settings. 
                * default_values (dict) : Default device configuration values structured and encapsulated inside of a dictionary acting as 
                    a fallback should the JSON fail. 
        ''' 
        
        # JSON containing configuration data. 
        self.config_file = config_file 

        # Default values dictionary. 
        self.default_values = default_values

    
    def load_settings(self):

        '''
            Load settings from the onboard Json file if it is in existence, else use default values. Ensure that 
                both the JSON and default dictionary values are merged to guarantee both are up to date, mitigating
                the chances of missing key value pairs. 
        '''

        # If provided path exists, leverage that configuration file. 
        if os.path.exists(self.config_file):
            
            # Read configuration file. 
            with open(self.config_file, 'r') as config_file:

                print('Config file present, loading settings.')

                # Load values.
                loaded_settings = json.load(config_file)

                # Merge values from JSON with that in the default values dictionary. 
                merged_settings = self.recursive_update(self.default_values, loaded_settings)

                # Return merged, updated values.
                return merged_settings

        else:

            # Otherwise, if not present; load, save and return default values.

            print('Config file not found, loading default values!')

            self.settings = self.default_values
            self.save_settings(settings=self.settings)

            return self.settings
    

    def save_settings(self, settings : dict):

        ''' Save currently applied settings to a JSON file for later access and retrieval. '''

        try:
            # Open config file and write new values.
            with open(self.config_file, 'w') as config_file:
                json.dump(settings, config_file, indent=4)

        except IOError as e:
            return f'Failed to save updated values to settings file.\n{e}'
        

    def recursive_update(self, settings : dict, updated_values : dict):

        '''
            Helper function to iterate through dictionary and its nested values leveraging recursion by calling itself until 
                all keys and their values have been iterated upon.
        '''
        
        # Iterate over the key value pairs.
        for key, value in updated_values.items():

            # If nested key value pair exists.
            if isinstance(value, dict) and key in settings:
                # Get that setting, its key and update it, use recursion for nested key value pairs.
                settings[key] = self.recursive_update(settings=settings[key], updated_values=value)
            else:
                # Otherwise, just update that existing key value pair.
                settings[key] = value

        # Return updated settings. 
        return settings
    

    def build_dictionary(self, keys : str, value : int | str | list):

        ''' Takes a list of keys and values assembling a dictionary. '''

        if not keys:
            return value 
        
        key = keys[0]

        if len(keys) == 1:
            return { key : self.type_cast_values(value=value)}


        return { key : self.build_dictionary(keys=keys[1:], value=value)}


    def type_cast_values(value : str | bool | int | list):

        ''' Helper function to enforce type checking when updating values. '''

        # Handle non-string values.
        if not isinstance(value, str):
            value = str(value)

        # Handle bool strings.
        elif value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        
        # Handle integer strings.
        elif value.isdigit():
            value = int(value)
        
        # Handle list strings.
        elif ',' in value:
            value = list(map(int, value.split(',')))
            
        # return original value if no conversion rulesets apply. 
        return value


    def update_settings(self, updated_values):

        ''' Update settings with new values set by the user, save to the config file. '''

        self.recursive_update(self.settings, updated_values)
        self.save_settings(self.settings)


    def fetch_current_settings(self):

        ''' Helper function to return current settings stored within the JSON file. '''

        return self.settings
