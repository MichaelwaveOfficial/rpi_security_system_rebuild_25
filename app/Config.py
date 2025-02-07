from pathlib import Path 
import os 

BASE_DIR = Path(__file__).resolve().parent.parent 

STATIC_DIR = './app/static/'

CAPTURE_UPLOADS_DIR = './app/upload_folder/'

TEST_DIR = './app/static/stream_test_imgs/'


STATIC_PATH = os.path.join(BASE_DIR, STATIC_DIR)
CAPTURES_PATH = os.path.join(BASE_DIR, CAPTURE_UPLOADS_DIR)
TEST_PATH = os.path.join(BASE_DIR, TEST_DIR)

## Get root dirs.
## Media dirs