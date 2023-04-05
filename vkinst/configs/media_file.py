from dataclasses import dataclass
from typing import Union


@dataclass
class MediaFile:
    shortcode: str
    post_type: str
    caption: Union[str, None]
    username: str
    timestamp: int
    media_type: str
    path: str
