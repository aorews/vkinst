import logging
import os
from pathlib import Path

import instaloader

from vkinst.configs.instagram_download_config import InstagramDownloadConfig
from vkinst.instagram.shortcode_saver import ShortcodeSaver, download_new_media

logger = logging.getLogger(__name__)


class InstagramSession:
    def __init__(self, username, password, session_path, dirname_pattern) -> None:
        self.inst_session = instaloader.Instaloader(
            dirname_pattern=dirname_pattern,
            filename_pattern="{shortcode}",
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=True,
            compress_json=False,
        )
        self.username = username
        self.password = password
        self.session_path = session_path

        self.login()

    def login(self):
        if os.path.isfile(self.session_path):
            self.login_from_session()
        else:
            self.login_with_password()

    def login_with_password(self):
        self.inst_session.login(self.username, self.password)
        # пока убрано т.к предположительно инстаграм теперь банит сессии бота и нет смысла открывать сессию, которая в бане
        # self.inst_session.save_session_to_file(filename=self.session_path)

    def login_from_session(self):
        self.inst_session.load_session_from_file(
            username=self.username, filename=self.session_path
        )


class InstagramDownloader:
    def __init__(self, path_to_config) -> None:
        self.config = InstagramDownloadConfig(path=path_to_config).config
        self.session_path = self.config["session_path"]

        self.session = InstagramSession(
            username=self.username,
            password=self.password,
            session_path=self.session_path,
            dirname_pattern=self.dirname_pattern,
        ).inst_session

        self.shortcodes = ShortcodeSaver(path=self.config["shortcodes_path"])

    @property
    def username(self):
        return self.config["inst"]["login"]

    @property
    def password(self):
        return self.config["inst"]["pass"]

    @property
    def download_folder(self):
        return self.config["download_folder"]

    @property
    def dirname_pattern(self):
        return str(Path(self.download_folder, "{profile}"))

    @download_new_media
    def media_download(self, media_iterator, instagram_page, type):
        if type == "post":
            downloader = self.session.download_post
        elif type == "story":
            downloader = self.session.download_storyitem

        for media in media_iterator:
            downloader(media, "")
            self.shortcodes.add(media.shortcode)

    def download_posts(self):
        for instagram_page in self.config["Links"]:
            logger.info(f"{instagram_page.link} posts")
            profile = instaloader.Profile.from_username(
                self.session.context, instagram_page.link
            )
            self.media_download(
                media_iterator=profile.get_posts(),
                instagram_page=instagram_page,
                type="post",
            )

    def download_stories(self):
        for instagram_page in self.config["Links"]:
            logger.info(f"{instagram_page.link} stories")
            for stories in self.session.get_stories([instagram_page.userid]):
                self.media_download(
                    media_iterator=stories.get_items(),
                    instagram_page=instagram_page,
                    type="story",
                )
