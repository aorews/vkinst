from dataclasses import dataclass
from typing import Union


@dataclass
class InstagramPage:
    link: str
    post_photo: Union[str, None]
    post_video: Union[str, None]
    stories_photo: Union[str, None]
    stories_video: Union[str, None]
    posts_to_check: int
    userid: int
