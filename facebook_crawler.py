from facepy import GraphAPI

from model.fbmodel import Post, Page, WatchedVideo, Music, Book
from utils.commons import delete_keys_from_dict


class FacebookCrawler:

    graph = None

    def __init__(self, access_token):
        self.graph = GraphAPI(access_token)

    '''
    If post contains the parent_id fields, it is a shared post. in this case, use the /parent_id?fields=from
    to see the author of the original post.
    '''
    def get_posts(self, since):
        url="me/posts?fields=id,created_time,from,link,message,message_tags,place,type,with_tags," \
            "likes.limit(100){id,name},comments.limit(100){id,name},sharedposts,parent_id"
        iterator = self.graph.get(url, page=True, since=since)

        for data in iterator:
            for p in data["data"]:
                post = Post(delete_keys_from_dict(p, ["paging"]))
                print(post.__dict__)

    def get_liked_pages(self):

        iterator = self.graph.get("me/likes", page=True)

        for data in iterator:
            for p in data["data"]:
                page = Page(p)
                print(page.__dict__)

    def get_watched_videos(self):

        iterator = self.graph.get("me/video.watches", page=True)

        for data in iterator:
            for p in data["data"]:

                if "data" in p:

                    field = None

                    if "tv_show" in p["data"]:
                        field = "tv_show"
                    elif "movie" in p["data"]:
                        field = "movie"
                    elif "episode" in p["data"]:
                        field = "episode"
                    elif "tv_episode" in p["data"]:
                        field = "tv_episode"
                    elif "video" in p["data"]:
                        field = "video"

                    video = WatchedVideo(p["data"][field])
                    video.type = field
                    print(video.__dict__)

    def get_listened_musics(self):

        iterator = self.graph.get("me/music.listens", page=True)

        for data in iterator:
            for p in data["data"]:
                if "data" in p and "song" in p["data"]:
                    music = Music(p["data"]["song"])
                    print(music.__dict__)

    def get_read_books(self):

        iterator = self.graph.get("me/books.reads", page=True)

        for data in iterator:
            for p in data["data"]:
                if "data" in p and "book" in p["data"]:
                    book = Book(p["data"]["book"])
                    print(book.__dict__)

