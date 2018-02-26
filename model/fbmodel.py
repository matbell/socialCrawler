POST_FIELDS = ("id", "created_time", "link", "message", "message_tags", "type", "object_id", "likes", "comments")


class Post:

    def __init__(self, d):

        for k in POST_FIELDS:
            if k in d:
                self.__dict__[k] = d[k]
