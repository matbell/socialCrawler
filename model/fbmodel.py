POST_FIELDS = ("id", "created_time", "link", "message", "message_tags", "type", "object_id", "likes", "comments")
PAGE_FIELDS = ("id", "name", "created_time")
BOOK_FIELDS = ("id", "title", "url")
WATCHED_VIDEO_FIELDS = ("id", "title", "type", "url")
MUSIC_FIELDS = ("id", "title", "url")


class Post:

    def __init__(self, d):

        for k in POST_FIELDS:
            if k in d:
                self.__dict__[k] = d[k]


class Page:

    def __init__(self, d):

        for k in PAGE_FIELDS:
            if k in d:
                self.__dict__[k] = d[k]


class Book:

    def __init__(self, d):

        for k in BOOK_FIELDS:
            if k in d:
                self.__dict__[k] = d[k]


class WatchedVideo:

    def __init__(self, d):

        for k in WATCHED_VIDEO_FIELDS:
            if k in d:
                self.__dict__[k] = d[k]


class Music:

    def __init__(self, d):

        for k in MUSIC_FIELDS:
            if k in d:
                self.__dict__[k] = d[k]