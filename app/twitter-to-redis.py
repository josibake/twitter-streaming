import redis
import tweepy
import os
import json
import logging

# read env variables
CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
ACCESS_KEY = os.environ['TWITTER_ACCESS_KEY']
ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']
REDIS_HOST = os.environ['REDIS_HOST'] 
REDIS_PORT = os.environ['REDIS_PORT']


logging.basicConfig(format='%(asctime)s - %(message)s')
# set up the redis connection
# doing this before twitter so that if the pod crashes
# we dont try to keep reconnecting to twitter
redis_queue = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
redis_queue.lpush('test','starting redis...')
logging.info("Connected to Redis!")

# setup twitter auth
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

class MyStreamListener(tweepy.StreamListener):
    def __init__(self, queue):
        self.queue = queue
        self.backoff = 1

    def on_data(self, data):
        self.queue.lpush('tweets', data)

    def on_error(self, status):
        logging.error(f"{status}")
        if status == 420:
            time.sleep(self.backoff*60)
            self.backoff = self.backoff*2


# and away we go! 
myStreamListener = MyStreamListener(queue = redis_queue)
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

logging.info("Filtering stream...")
myStream.filter(track=['coronavirus'], is_async=True)
