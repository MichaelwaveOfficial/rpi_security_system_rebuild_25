
'''
    Ground truth file for single source of application configurations.
'''

from pathlib import Path 
import os 

'''
    Application Directories.
'''

BASE_DIR = Path(__file__).resolve().parent.parent 
STATIC_DIR = './app/static/'
CAPTURE_UPLOADS_DIR = './app/upload_folder/'
TEST_DIR = './app/static/stream_test_imgs/'
APP_DIR = os.path.join(BASE_DIR, './app')

'''
    Full Application Paths.
'''

STATIC_PATH = os.path.join(BASE_DIR, STATIC_DIR)
CAPTURES_PATH = os.path.join(BASE_DIR, CAPTURE_UPLOADS_DIR)
TEST_PATH = os.path.join(BASE_DIR, TEST_DIR)


'''
    Camera settings.
'''

INDEX = 0
CAMER_CONFIG = 'camera_settings.json'
CAMERA_CONFIG_PATH = os.path.join(APP_DIR, CAMER_CONFIG)

''' Default values for the device camera to act as a fallback should the JSON retrieval fail. '''

DEFAULT_CAMERA_CONFIG_DICT = {
    'motion_detection' : {
        'sensitivity' : 50,
        'threat_escalation_timer' : 10,
        'maximum_threat_threshold' : 5,
        'regions_of_interest' : []
    },
    'stream_quality' : {
        'preferred_quality' : 'performance',
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
        'recipient_email' : os.getenv('RECIPIENT_EMAIL', 'example@email.com'),
        'app_email' : os.getenv('APP_EMAIL','example@email.com'),
        'app_password' : os.getenv('APP_PASSWORD', 'password')
    },
    'storage_settings' : {
        'auto_resource_management' : True,
        'content_type' : 'video'
    }
}

'''
    Device Storage Configuration Settings.
'''

FORMATTED_FILENAME_DATE : str = '%a-%b-%Y_%I-%M-%S%p',
FORMATTED_DISPLAY_DATE : str = '%I:%M:%S%p',
MAXIMUM_FILES_STORED : int = 60
