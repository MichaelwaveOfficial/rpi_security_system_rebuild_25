from flask import Blueprint, Response, render_template, request, jsonify
from .Camera import Camera
from .AppConfig import *
import re
import json


# Initialise camera object, set camera index to 0.
camera = Camera(INDEX=0, config_file=CAMERA_CONFIG_PATH)

# Register main app blueprint.
main = Blueprint('main', __name__)


@main.route('/video_stream')
def video_stream():

    return Response(
        camera.test_stream(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@main.route('/')
def index():

    # Testing fake stream with test stream iteration.
    try:
        # Try to get the first frame
        next(camera.test_stream())
        stream_available = True  
    except StopIteration:
        # Otherwise camera loading?
        stream_available = False
  
    return render_template(
        'index.html',
        stream_available=stream_available
    )


@main.route('/settings')
def settings():

    settings = camera.load_settings()

    return render_template(
        'settings.html',
        settings=settings
    )


@main.route('/settings/update', methods=['POST'])
def update_settings():

    '''
        Long, arguably over convoluted way of updating settings values through recursion.
    '''

    try:
        
        # Load current settings configuration from JSON. (if present, otherwise default dictionary loaded).
        current_settings = camera.settings

        # Iterate over items and their values.
        for key, updated_value in request.form.items():

            # Leverage regular expressions to take objects array keys and put them into a list. 
            keys = re.findall(r'\w+', key)

            # Build the updated settings dictionary from users form input. 
            updated_settings = build_dictionary(keys=keys, value=updated_value)

            # Merge new dictionary and its updatred with the current settings.
            current_settings = camera.recursive_update(settings=current_settings, updated_values=updated_settings)
        
        # Save the settings with the freshly updated values. 
        camera.save_settings(current_settings)

        # Return JSON success response. 
        return jsonify({"status": "success", "message": "Settings updated successfully"})
    
    except Exception as e:

        # Return JSON error response. 
        return jsonify({"status": "error", "message": f"Failed to update settings!\n{e}"})


def build_dictionary(keys, value):

    '''
        Takes a list of keys and values assembling a dictionary.
    '''

    if not keys:
        return value 
    
    key = keys[0]

    if len(keys) == 1:
        return { key : type_cast_values(value=value)}


    return { key : build_dictionary(keys=keys[1:], value=value)}

def type_cast_values(value):

    '''
        Helper function to enforce type checking when updating values.
    '''

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

@main.route('/captures')
def captures():
    return render_template(
        'captures.html',
        images=[], # Accumulate list of images on device
        image=None # USer selected image.
    )
