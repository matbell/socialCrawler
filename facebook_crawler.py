from facepy import GraphAPI

from model.fbmodel import ObjectWithGeoInfo, SimpleObject, POST_FIELDS, PHOTO_FIELDS, VIDEO_FIELDS, PAGE_FIELDS, \
    BOOK_FIELDS, MUSIC_FIELDS, WATCHED_VIDEO_FIELDS
from utils.mongo_data import MONGO_HOST
from pymongo import MongoClient


class FacebookCrawler:

    def __init__(self, access_token):
        self.graph = GraphAPI(access_token)

        client = MongoClient(MONGO_HOST)
        self.db = client.myDigitalFootprints

        self.user = self.get_user()

    def get_user(self):
        url = "me?fields=email,name,first_name,last_name,birthday,picture.height(800).width(800){url}"

        user = self.graph.get(url)
        del user["headers"]
        self.db.fbUsers.update({"id": user["id"]}, user, upsert=True)
        return user

    '''=================================================================================================================
    Uploaded & tagged POSTS
    ================================================================================================================='''
    def get_posts(self, since=None):
        url = "me/posts?fields=id,created_time,from,link,message,message_tags,place,type,with_tags," \
              "likes.limit(200){id,name},comments.limit(200){id,message,from},sharedposts,parent_id"

        iterator = self.graph.get(url, page=True, since=since)

        print("Downloading user's posts...")

        for data in iterator:
            for p in data["data"]:
                post = ObjectWithGeoInfo(p, POST_FIELDS)
                self.db.fbPosts.update({"id": post.__dict__["id"]}, post.__dict__, upsert=True)

    def get_tagged_posts(self, since=None):
        url = "me/tagged?fields=id,created_time,from,link,message,message_tags,place,type,with_tags," \
              "likes.limit(200){id,name},comments.limit(200){id,message,from},sharedposts,parent_id"

        iterator = self.graph.get(url, page=True, since=since)

        print("Downloading tagged posts...")

        for data in iterator:
            for p in data["data"]:
                post = ObjectWithGeoInfo(p, POST_FIELDS)
                self.db.fbPosts.update({"id": post.__dict__["id"]}, post.__dict__, upsert=True)

    '''=================================================================================================================
    Uploaded & tagged PHOTOS
    ================================================================================================================='''
    def get_tagged_photos(self):

        url = "me/photos/tagged?fields=from,link,created_time,tags{id,name},place,likes.limit(200){id,name}"

        print("Downloading tagged photos...")

        iterator = self.graph.get(url, page=True)

        for data in iterator:
            for p in data["data"]:
                photo = ObjectWithGeoInfo(p, PHOTO_FIELDS)
                self.db.fbPhotos.update({"id": photo.__dict__["id"]}, photo.__dict__, upsert=True)

    def get_uploaded_photos(self):

        url = "me/photos/uploaded?fields=from,link,created_time,tags{id,name},place,likes.limit(200){id,name}," \
              "comments.limit(200)"

        print("Downloading uploaded photos...")

        iterator = self.graph.get(url, page=True)

        for data in iterator:
            for p in data["data"]:
                photo = ObjectWithGeoInfo(p, PHOTO_FIELDS)
                self.db.fbPhotos.update({"id": photo.__dict__["id"]}, photo.__dict__, upsert=True)

    '''=================================================================================================================
    Uploaded & tagged VIDEOS
    ================================================================================================================='''
    def get_uploaded_videos(self):

        url = "me/videos/uploaded?fields=from,description,permalink_url,comments.limit(200),likes.limit(200),place," \
              "created_time,id,tags.limit(200)"

        print("Downloading uploaded videos...")

        iterator = self.graph.get(url, page=True)

        for data in iterator:
            for p in data["data"]:
                video = ObjectWithGeoInfo(p, VIDEO_FIELDS)
                self.db.fbVideos.update({"id": video.__dict__["id"]}, video.__dict__, upsert=True)

    def get_tagged_videos(self):

        url = "me/videos/tagged?fields=from,description,permalink_url,comments.limit(200),likes.limit(200),place," \
              "created_time,id,tags.limit(200)"

        print("Downloading tagged videos...")

        iterator = self.graph.get(url, page=True)

        for data in iterator:
            for p in data["data"]:
                video = ObjectWithGeoInfo(p, VIDEO_FIELDS)
                self.db.fbVideos.update({"id": video.__dict__["id"]}, video.__dict__, upsert=True)

    '''=================================================================================================================
    Liked pages, videos (tv shows & movies), books, and music
    ================================================================================================================='''
    def get_liked_pages(self):

        iterator = self.graph.get("me/likes", page=True, limit=200)

        pages_ids = []
        for data in iterator:
            for p in data["data"]:
                page = SimpleObject(p, PAGE_FIELDS)
                self.db.fbPages.update({"id": page.__dict__["id"]}, page.__dict__, upsert=True)
                pages_ids.append(page.__dict__["id"])

        if len(pages_ids) > 0:
            d = {"user": self.user["id"], "pages": pages_ids}
            self.db.fbUserLikedPages.update({"user": d["user"]}, d, upsert=True)

    def get_watched_videos(self):

        iterator = self.graph.get("me/video.watches", page=True, limit=200)

        videos_ids = []

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

                    video = SimpleObject(p["data"][field], WATCHED_VIDEO_FIELDS)
                    video.type = field
                    self.db.fbWatchedVideos.update({"id": video.__dict__["id"]}, video.__dict__, upsert=True)
                    videos_ids.append(video.__dict__["id"])

        if len(videos_ids) > 0:
            d = {"user": self.user["id"], "watched_videos": videos_ids}
            self.db.fbUserLikedVideos.update({"user": d["user"]}, d, upsert=True)

    def get_listened_musics(self):

        iterator = self.graph.get("me/music.listens", page=True, limit=200)

        musics_ids = []

        for data in iterator:
            for p in data["data"]:
                if "data" in p and "song" in p["data"]:
                    music = SimpleObject(p["data"]["song"], MUSIC_FIELDS)
                    self.db.fbMusic.update({"id": music.__dict__["id"]}, music.__dict__, upsert=True)
                    musics_ids.append(music.__dict__["id"])

        if len(musics_ids) > 0:
            d = {"user": self.user["id"], "listened_musics": musics_ids}
            self.db.fbUserLikedVideos.update({"user": d["user"]}, d, upsert=True)

    def get_read_books(self):

        iterator = self.graph.get("me/books.reads", page=True, limit=200)

        books_ids = []

        for data in iterator:
            for p in data["data"]:
                if "data" in p and "book" in p["data"]:
                    book = SimpleObject(p["data"]["book"], BOOK_FIELDS)
                    self.db.fbBooks.update({"id": book.__dict__["id"]}, book.__dict__, upsert=True)
                    books_ids.append(book.__dict__["id"])

        if len(books_ids) > 0:
            d = {"user": self.user["id"], "read_books": books_ids}
            self.db.fbUserReadBooks.update({"user": d["user"]}, d, upsert=True)

