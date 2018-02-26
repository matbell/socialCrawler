from facepy import GraphAPI

from model.fbmodel import Post
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


