from flask import Blueprint, Response, render_template
from .Camera import Camera


# Initialise camera object, set camera index to 0.
camera = Camera(INDEX=0)

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
    return render_template(
        'settings.html',
        title='Settings'
    )


@main.route('/captures')
def captures():
    return render_template(
        'captures.html',
        images=[], # Accumulate list of images on device
        image=None # USer selected image.
    )
