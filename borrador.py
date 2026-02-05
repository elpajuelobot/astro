from spotify_manager import Spotify, spoti_info
from system_config import talk_async

actual_device_id = spoti_info(talk_async, "device_id", "device_name")
print(actual_device_id)
