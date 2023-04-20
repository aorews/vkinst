import os
from pathlib import Path

from vkinst.configs.base_config import BaseConfig
from vkinst.helper import get_dict_element, get_folder_names, replace_at_links


class UploadConfig(BaseConfig):
    def __init__(self, path):
        super().__init__(path)
        self.download_folder = self.config["download_folder"]
        self.upload_config_path = self.config["upload_config_path"]
        self.write_summary_config()

    def collect_post_media(self, post_info, path_to_profile, shortcode):
        post_media = list()
        post_files = [
            file for file in os.listdir(path_to_profile) if file.startswith(shortcode)
        ]
        for media_file in post_files:
            if media_file.endswith(".mp4"):
                post_info["media_type"] = "video"
            elif media_file.endswith(".jpg"):
                post_info["media_type"] = "image"
            else:
                post_info["media_type"] = "misc"
            post_info["path"] = str(Path(path_to_profile, media_file))
            post_media.append(post_info.copy())

        return post_media

    def collect_profile_media(self, path_to_profile, username):
        profile_media = list()
        post_json_list = [
            file for file in os.listdir(path_to_profile) if file.endswith(".json")
        ]
        for post_json in post_json_list:
            post_config = BaseConfig(Path(path_to_profile, post_json)).config

            shortcode = post_json.replace(".json", "")
            caption = replace_at_links(
                get_dict_element(
                    post_config, "node.edge_media_to_caption.edges.node.text"
                )
            )

            post_info = {
                "shortcode": shortcode,
                "post_type": get_dict_element(post_config, "instaloader.node_type"),
                "caption": caption,
                "username": username,
                "timestamp": get_dict_element(post_config, "node.taken_at_timestamp"),
            }
            profile_media.extend(
                self.collect_post_media(post_info, path_to_profile, shortcode)
            )

        return profile_media

    def collect_download_summary(self):
        summary_config = list()
        for downloaded_profile in get_folder_names(self.download_folder):
            summary_config.extend(
                self.collect_profile_media(
                    Path(self.download_folder, downloaded_profile), downloaded_profile
                )
            )
        return summary_config

    def write_summary_config(self):
        download_summary = self.collect_download_summary()
        config = BaseConfig(self.upload_config_path)
        config.config = download_summary
        config.write_config()
