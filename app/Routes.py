from flask import Blueprint, Response, render_template, request, jsonify
from .AppConfig import *
import re
from .Pipeline import stream_pipeline


# Register main app blueprint.
main = Blueprint('main', __name__)


@main.route('/video_stream')
def video_stream():

    ''' Route leveraging a generator function to stream captured video frames to the client. '''

    return Response(
        stream_pipeline.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@main.route('/')
def index():

    ''' Render index page with stream availabilty status. '''

    # Testing fake stream with test stream iteration.
    try:
        # Try to get the first frame
        next(stream_pipeline.generate_frames())
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

    ''' Render settings paeg with current camera configuration. '''

    settings = stream_pipeline.configuration_manager.load_settings()

    return render_template(
        'settings.html',
        settings=settings
    )


@main.route('/settings/update', methods=['POST'])
def update_settings():

    ''' Update camera settings based on user form input. '''

    try:
        
        # Load current settings configuration from JSON. (if present, otherwise default dictionary loaded).
        current_settings = stream_pipeline.camera.settings

        # Iterate over items and their values.
        for key, updated_value in request.form.items():

            # Leverage regular expressions to take objects array keys and put them into a list. 
            keys = re.findall(r'\w+', key)

            # Build the updated settings dictionary from users form input. 
            updated_settings = stream_pipeline.configuration_manager.build_dictionary(keys=keys, value=updated_value)

            # Merge new dictionary and its updatred with the current settings.
            current_settings = stream_pipeline.configuration_manager.recursive_update(settings=current_settings, updated_values=updated_settings)
        
        # Save the settings with the freshly updated values. 
        stream_pipeline.configuration_manager.save_settings(current_settings)

        # Return JSON success response. 
        return jsonify({"status": "success", "message": "Settings updated successfully"})
    
    except Exception as e:

        # Return JSON error response. 
        return jsonify({"status": "error", "message": f"Failed to update settings!\n{e}"})


@main.route('/captures')
def captures():

    ''' Render captures page with a list of images stored on the device. '''

    return render_template(
        'captures.html',
        images=[], # Accumulate list of images on device
        image=None # USer selected image.
    )
