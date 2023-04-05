from dacite import from_dict

from vkinst.configs.base_config import BaseConfig
from vkinst.configs.instagram_page import InstagramPage


class InstagramDownloadConfig(BaseConfig):
    def __init__(self, path):
        super().__init__(path)
        self.config["Links"] = self.get_download_config()

    def get_download_config(self) -> list:
        links = list()

        for link_config in self.config["Links"]:
            links.append(from_dict(InstagramPage, link_config))
        return links
