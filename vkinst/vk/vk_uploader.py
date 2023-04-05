import logging
import os
import re
import webbrowser
from datetime import datetime
from functools import lru_cache

import vk_api

from vkinst.configs.vk_config import VKConfig
from vkinst.helper import wait_between_requests

logger = logging.getLogger(__name__)


class VKUploader:
    def __init__(self, path_to_config) -> None:
        self.vk_config = VKConfig(path_to_config)
        self.login(self.vk_config.username, self.vk_config.password)
        self.upload_media_files()

    def captcha_handler(self, captcha):
        key = input(f"Enter captcha code {captcha.get_url()}: ").strip()
        return captcha.try_again(key)

    def auth_handler(self):
        code = input("Код для двухфакторной аутентификации: ")
        return code, True

    def login(self, username, password):
        url = "https://oauth.vk.com/authorize?client_id=6287487&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1"
        webbrowser.open(url, new=0, autoraise=True)
        token = input("Write token: ")
        self.vk_session = vk_api.VkApi(token=token)

    def upload_media_files(self):
        for batch in self.vk_config.media_files_generator():
            paths_to_delete = list()
            for media_file in batch:
                uploaded_file_path = self.upload_file(media_file=media_file)
                paths_to_delete.append(uploaded_file_path)

            logger.info(
                f"{media_file.shortcode} {media_file.username} {media_file.post_type} done"
            )

            self.delete_files(paths_to_delete)

    def upload_file(self, media_file):
        if media_file.media_type == "image":
            self.upload_image(media_file)
        if media_file.media_type == "video":
            self.upload_video(media_file)
        return media_file.path

    @wait_between_requests
    def upload_image(self, media_file):
        group_id, album_id = self.get_photo_album(media_file)

        if group_id is None:
            logger.info(
                f"{media_file.shortcode} No vk album link for {media_file.username} {media_file.post_type} image skip"
            )
            return

        vk_api.upload.VkUpload(self.vk_session).photo(
            photos=media_file.path,
            caption=media_file.caption,
            group_id=group_id,
            album_id=album_id,
        )

    @wait_between_requests
    def upload_video(self, media_file):
        group_id, album_id = self.get_video_album(media_file)

        if group_id is None:
            logger.info(
                f"{media_file.shortcode} No vk album link for {media_file.username} {media_file.post_type} video skip"
            )
            return

        video_name = self.get_video_name(media_file)
        vk_api.upload.VkUpload(self.vk_session).video(
            video_file=media_file.path,
            name=video_name,
            description=media_file.caption,
            group_id=group_id,
            album_id=album_id,
        )

    def get_photo_album(self, media_file):
        username_page = self.vk_config.profile_vk_album_links[media_file.username]
        if media_file.post_type == "Post":
            album_link = username_page.post_photo
        elif media_file.post_type == "StoryItem":
            album_link = username_page.stories_photo

        group_id, album_id = self.get_group_album_id(album_link=album_link)

        return group_id, album_id

    def get_video_album(self, media_file):
        username_page = self.vk_config.profile_vk_album_links[media_file.username]
        if media_file.post_type == "Post":
            album_link = username_page.post_video
        elif media_file.post_type == "StoryItem":
            album_link = username_page.stories_video

        group_id, album_id = self.get_group_album_id(album_link=album_link)

        return group_id, album_id

    @lru_cache
    def get_group_album_id(self, album_link):
        if album_link is None:
            return None, None
        group_id, album_id = re.findall("-(\d+).*_(\d+)", album_link)[0]
        return group_id, album_id

    def get_video_name(self, media_file):
        date = datetime.fromtimestamp(media_file.timestamp).strftime("%y%m%d")
        return f"{date} Instagram @{media_file.username}"

    def delete_files(self, file_paths):
        for path in file_paths:
            os.remove(path)
