from flask import Blueprint, Response, render_template, request, redirect, url_for
from .Camera import Camera


# Initialise camera object, set camera index to 0.
camera = Camera(INDEX=0, config_file='camera_settings.json')

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

    settings = camera.default_values

    return render_template(
        'settings.html',
        settings=settings
    )


@main.route('/settings/update', methods=['POST'])
def update_settings():

    '''
        Long, arguably over convoluted way of updating settings values through recursion.
    '''

    # Load current settings configuration from JSON. (if present, otherwise default dictionary loaded).
    current_settings = camera.load_settings()

    # Copy config file, mitigate mutating original values. 
    updated_settings = current_settings.copy()

    # Iterate over items and their values.
    for category, updated_value in request.form.items():

        # Ensure category exists before update.
        if category not in updated_settings:
            print(f'Category : {category} not present in config file.')
            return redirect(url_for('settings'))
        
        if category == 'motion_detection':
        
            for sub_category in updated_settings[category]:

                updated_settings[category][sub_category] = int(updated_value)
         
        if category == 'stream_quality':

            for sub_category in updated_settings[category]:

                for key in updated_settings[category][sub_category]:

                    if key == 'framerate':
                        updated_settings[category][sub_category][key] = int(updated_value)
                    
                    if key == 'resolution':
                        updated_settings[category][sub_category][key] = list(map(int, updated_value.split(',')))

        if category == 'alert_settings':

            if 'toggle' in updated_settings[category]:
                updated_settings[category]['toggle'] = updated_value.lower() == 'true'

            if 'frequency' in updated_settings[category]:
                updated_settings[category]['frequency'] = int(updated_value)

            if ['target_email', 'app_password'] in updated_settings[category]:
                updated_settings[category]['target_email'] = str(updated_value)

        if category == 'storage_settings':
            
            if 'auto_resource_management' in updated_settings[category]:
                updated_settings[category]['auto_resource_management'] = updated_value.lower() == 'true'
            
            if 'content_type' in updated_settings[category]:
                updated_settings[category]['cotent_type'] = str(updated_value)
    
    # Save the settings with the freshly updated values. 
    camera.save_settings(updated_settings)

    # Redirect the user back to settings route to render settings page.
    return redirect(url_for('settings'))


@main.route('/captures')
def captures():
    return render_template(
        'captures.html',
        images=[], # Accumulate list of images on device
        image=None # USer selected image.
    )
