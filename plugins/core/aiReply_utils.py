#random_str,file_upload_toUrl,and so on.
import base64
import io

import httpx
from PIL import Image

from plugins.core.llmDB import get_user_history, update_user_history
from plugins.utils.random_str import random_str




