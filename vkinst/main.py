import argparse
import logging

from vkinst.configs.base_config import BaseConfig
from vkinst.configs.upload_config import UploadConfig
from vkinst.instagram.instagram_downloader import InstagramDownloader
from vkinst.logger import set_logger
from vkinst.vk.vk_uploader import VKUploader

logger = logging.getLogger(__name__)


def main(config_path):
    try:
        set_logger()
        
        logger.info("Script started")

        config = BaseConfig(path=config_path).config

        download_posts = config["download_instagram"]["posts"]
        download_stories = config["download_instagram"]["stories"]

        if download_posts or download_stories:
            loader = InstagramDownloader(path_to_config=config_path)

        if download_posts:
            loader.download_posts()
        if download_stories:
            loader.download_stories()

        UploadConfig(path=config_path)

        VKUploader(path_to_config=config_path)

    except Exception as e:
        logger.error(e)
    
    finally:
        logger.info("Script finished")
        input("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="Path to config file")
    args = parser.parse_args()
    main(args.config_path)
