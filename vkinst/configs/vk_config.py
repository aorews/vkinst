from itertools import groupby

from dacite import from_dict

from vkinst.configs.base_config import BaseConfig
from vkinst.configs.instagram_download_config import InstagramDownloadConfig
from vkinst.configs.media_file import MediaFile


class VKConfig(BaseConfig):
    def __init__(self, path):
        super().__init__(path)
        self.path = path
        self.files = BaseConfig(self.config["upload_config_path"]).config
        self.profile_vk_album_links = self.get_vk_album_links()
        self.collect_media_files()

    @property
    def username(self):
        return self.config["vk"]["login"]

    @property
    def password(self):
        return self.config["vk"]["pass"]

    def collect_media_files(self):
        self.media_files = [
            from_dict(data_class=MediaFile, data=file) for file in self.files
        ]

    def media_files_generator(self):
        media_files = sorted(self.media_files, key=lambda x: (x.username, x.timestamp))
        batched_media_files = groupby(
            media_files, key=lambda x: (x.username, x.shortcode)
        )
        for _, batch in batched_media_files:
            yield sorted(batch, key=lambda x: x.path, reverse=True)

    def get_vk_album_links(self):
        self.instagram_pages = InstagramDownloadConfig(self.path).config["Links"]
        profile_vk_album_links = {
            instagram_page.link: instagram_page
            for instagram_page in self.instagram_pages
        }
        return profile_vk_album_links
