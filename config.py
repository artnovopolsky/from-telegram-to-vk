import os
from datetime import datetime

TG_API_ID = # must be integer
TG_API_HASH = ''
CHANNEL_NAME = ''

VK_GROUP_TOKEN = ''
VK_GROUP_ID = ''


def get_unique_filename():
    media_folder_path = os.path.join(os.path.abspath(''), 'media', datetime.now().strftime("%d-%m-%Y_%H:%M:%S"))
    return media_folder_path
