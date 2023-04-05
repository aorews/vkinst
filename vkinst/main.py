import argparse

from vkinst.configs.base_config import BaseConfig
from vkinst.configs.upload_config import UploadConfig
from vkinst.instagram.instagram_downloader import InstagramDownloader
from vkinst.logger import set_logger
from vkinst.vk.vk_uploader import VKUploader


def main(config_path):
    set_logger()

    config = BaseConfig(path=config_path).config

    loader = InstagramDownloader(path_to_config=config_path)

    if config["download_instagram"]["posts"]:
        loader.download_posts()
    if config["download_instagram"]["stories"]:
        loader.download_stories()

    UploadConfig(path=config_path)

    VKUploader(path_to_config=config_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="Path to config file")
    args = parser.parse_args()
    main(args.config_path)