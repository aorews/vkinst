import logging
import os
import pickle

logger = logging.getLogger(__name__)


class ShortcodeSaver:
    def __init__(self, path):
        self.shortcodes_path = path
        self.shortcodes = self.load()

    def __contains__(self, element):
        return element in self.shortcodes

    def save(self):
        with open(self.shortcodes_path, "wb") as f:
            pickle.dump(self.shortcodes, f)

    def load(self):
        if os.path.exists(self.shortcodes_path):
            with open(self.shortcodes_path, "rb") as f:
                data = pickle.load(f)
            return data
        else:
            return set()

    def add(self, shortcode):
        self.shortcodes.add(shortcode)
        self.save()


def new_media_iterator(media_iterator, shortcodes):
    for media in media_iterator:
        if media.shortcode not in shortcodes:
            yield media
        else:
            return


def fixed_posts_iterator(media_iterator, shortcodes, required_posts):
    for i, media in enumerate(media_iterator):
        if media.shortcode in shortcodes:
            yield None
        elif i < required_posts:
            yield media
        else:
            return


def download_new_media(downloader_func):
    def wrapper(self, *args, **kwargs):
        required_posts = kwargs["instagram_page"].posts_to_check
        if required_posts < 0 or kwargs["type"] == "story":
            kwargs["media_iterator"] = new_media_iterator(
                media_iterator=kwargs["media_iterator"], shortcodes=self.shortcodes
            )
        else:
            kwargs["media_iterator"] = fixed_posts_iterator(
                media_iterator=kwargs["media_iterator"],
                shortcodes=self.shortcodes,
                required_posts=required_posts,
            )

        try:
            result = downloader_func(self, *args, **kwargs)
        except Exception as e:
            logger.error(e)

        return result

    return wrapper
