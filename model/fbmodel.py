from utils.commons import delete_keys_from_dict

POST_FIELDS = ("id", "created_time", "from", "link", "message", "message_tags", "place", "type", "with_tags",
               "likes", "comments", "sharedposts", "parent_id")
PAGE_FIELDS = ("id", "name", "link", "fan_count")
BOOK_FIELDS = ("id", "title", "url")
WATCHED_VIDEO_FIELDS = ("id", "title", "type", "url")
MUSIC_FIELDS = ("id", "title", "url")
PHOTO_FIELDS = ("id", "from", "link", "created_time", "tags", "place", "likes", "comments")
VIDEO_FIELDS = ("id", "from", "permalink_url", "created_time", "tags", "place", "likes", "description", "comments")


class ObjectWithGeoInfo:

    def __init__(self, d, fields):

        d = delete_keys_from_dict(d, ["paging"])

        for k in fields:
            if k in d:
                self.__dict__[k] = d[k]
                if k == 'place' and 'location' in d[k] and 'latitude' in d[k]['location'] and\
                        'longitude' in d[k]['location']:
                    self.__dict__[k]['location']['latitude'] = float(d[k]['location']['latitude'])
                    self.__dict__[k]['location']['longitude'] = float(d[k]['location']['longitude'])


class SimpleObject:

    def __init__(self, d, fields):

        d = delete_keys_from_dict(d, ["paging"])

        for k in fields:
            if k in d:
                self.__dict__[k] = d[k]