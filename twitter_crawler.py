import tweepy
from pymongo import MongoClient
from tqdm import tqdm

from utils.mongo_data import MONGO_HOST

'''
This class downloads the following information from Twitter for the specified user:
- profile
- followers
- friends
- tweets
- favorites

It assumes the presence of a running MONGODB database called mdfTwitter, and creates the following collections:
- tweets : contains the raw json files of the downloaded tweets
- users : raw json objects which represent the downloaded users' profiles
- followers : for each downloaded user, it contains a document with the list of her followers
- friends : for each downloaded user, it contains a document with the list of her friends
- favorites : for each downloaded user, it contains a document with the list of tweets she liked in the past
'''

APP_CONSUMER_KEY = '5jZS19ffLeQWMQGNoeltOid1o'
APP_CONSUMER_SECRET = 'pqgysx4g3kpH7SxWQffF9cVFNmrymSBLgUb89Rt7JD6D8oE0EP'


class TwitterCrawler:

    def __init__(self, twitter_token, twitter_secret):

        auth = tweepy.OAuthHandler(APP_CONSUMER_KEY, APP_CONSUMER_SECRET)
        auth.set_access_token(twitter_token, twitter_secret)

        self.api = tweepy.API(auth)

        client = MongoClient(MONGO_HOST)
        self.db = client.mdfTwitter

        self.user = self.api.me()


    '''
    Downloads the user's profile, and saves it into the users collection.
    See the User object: https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/user-object
    '''
    def get_profile(self):
        self.db.users.update({"id": self.user._json["id"]}, self.user._json, upsert=True)
        return self.user


    '''
    Downloads the followers of the specified user.
    For each follower, it creates a new document into the users collection or updates an already existing one.
    In addition, it creates (or updates) the following document inside the followers collection:
    {
        "id": user_id (the id of the target user),
        "followers" = [] (list of the followers' ids)
    }
    '''
    def get_followers(self):

        followers = []
        for follower in tqdm(tweepy.Cursor(self.api.followers).items(), desc="Downloading followers"):
            self.db.users.update({"id": follower._json["id"]}, follower._json, upsert=True)
            followers.append(follower.id)

            self.db.followers.update({"id": self.user.id}, {"id": self.user.id, "followers": followers}, upsert=True)


    '''
    Downloads the friends of the specified user.
    For each friend, it creates a new document into the users collection or updates an already existing one.
    In addition, it creates (or updates) the following document inside the friends collection:
    {
        "id": user_id (the id of the target user),
        "friends" = [] (list of the friends' ids)
    }
    '''
    def get_friends(self):

        friends = []
        for friend in tqdm(tweepy.Cursor(self.api.friends).items(), desc="Downloading friends"):
            self.db.users.update({"id": friend._json["id"]}, friend._json, upsert=True)
            friends.append(friend.id)

            self.db.friends.update({"id": self.user.id}, {"id": self.user.id, "friends": friends}, upsert=True)


    '''
    Downloads the tweets created by the specified user.
    For each tweet, it creates a new document into the tweets collection or updates an already existing one.
    '''
    def get_tweets(self):

        for tweet in tqdm(tweepy.Cursor(self.api.user_timeline).items(), desc="Downloading tweets"):
            self.db.tweets.update({"id": tweet._json["id"]}, tweet._json, upsert=True)

            if hasattr(tweet, "retweeted_status"):
                retweeted_status = tweet.retweeted_status._json
                self.db.tweets.update({"id": retweeted_status["id"]}, retweeted_status, upsert=True)

            if hasattr(tweet, "quoted_status"):
                quoted_status = tweet.quoted_status
                self.db.tweets.update({"id": quoted_status["id"]}, quoted_status, upsert=True)

            if hasattr(tweet, "in_reply_to_status_id") and tweet.in_reply_to_status_id is not None:
                replied_tweet = self.api.get_status(tweet.in_reply_to_status_id)._json
                self.db.tweets.update({"id": replied_tweet["id"]}, replied_tweet, upsert=True)


    '''
    Downloads the list of tweets liked by the specified user.
    For each tweet, it creates a new document into the tweets collection or updates an already existing one.
    In addition, it creates (or updates) the following document inside the favorites collection:
    {
        "id": user_id (the id of the target user),
        "favorites" = [] (list of the favorite tweets' ids)
    }
    '''
    def get_favorites(self):

        favorites = []
        for tweet in tqdm(tweepy.Cursor(self.api.favorites).items(), desc="Downloading favorites"):
            self.db.tweets.update({"id": tweet._json["id"]}, tweet._json, upsert=True)
            favorites.append(tweet._json["id"])

            self.db.favorites.update({"id": self.user.id}, {"id": self.user.id, "favorites": favorites}, upsert=True)