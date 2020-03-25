import os
import redis
from elasticsearch import Elasticsearch, helpers
import json
from datetime import datetime
import logging

def get_centroid(coordinates):
    x, y = zip(*coordinates)
    l = len(x)
    return sum(x)/l, sum(y)/l
        
def convert_tweet_to_document(tweet):
    
    text = tweet['extended_tweet']['full_text'] if 'extended_tweet' in tweet else tweet['text']
    hashtags = tweet['extended_tweet']['entities']['hashtags'] if 'extended_tweet' in tweet else tweet['entities']['hashtags']
    idx = tweet['id']
    ts = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
    body = {'event_timestamp': ts}
    
    if hashtags:
        text = remove_by_indices(text, hashtags)
        tags = [h['text'] for h in hashtags]
        body.update({'text': text, 'tags': tags})
    else:
        body.update({'text': text})
    
    coordinates = parse_location_data(tweet)
    body.update(coordinates)
        
    return idx, body

def remove_by_indices(text, indices):
    '''
    Strips out unwanted text using the start and stop indices
    '''
    
    # get all the start and stop indices of unwanted text
    slices = [{'i':h['indices'][0], 'j':h['indices'][1]} for h in indices]
    
    # sort from last to first so none of the indices change
    slices = sorted(slices, key=lambda s: s['i'], reverse=True)
    
    for s in slices:
        text = text[:s['i']] + text[s['j']:]
        
    return ' '.join(text.split())
    
def parse_location_data(tweet):
    if tweet['place']:
        coordinates = tweet['place']['bounding_box']['coordinates'][0]
        lon, lat = get_centroid(coordinates)
        country_code = tweet['place']['country_code']
        full_name = tweet['place']['full_name']
        coordinates = {
            'name': full_name, 
            'country_code': country_code,
            'location': {
                'lon': lon,
                'lat': lat,
            }
        }
    elif tweet['coordinates']:
        coordinates = {
            'location': {
                'lat': tweet['coordinates']['coordinates'][1],
                'lon': tweet['coordinates']['coordinates'][0],
            }
        }
    elif tweet['geo']:
        coordinates = {
            'location': {
                'lat': tweet['geo']['coordinates'][0],
                'lon': tweet['geo']['coordinates'][1],
            }
        }
    else:
        coordinates = {}
        
    return coordinates

def process_queue(queue):
    max_bulk = 1000
    count = 0    
    while count < max_bulk:
        tweet = json.loads(queue.brpop('tweets')[1])
        
        if any(k in tweet for k in ('limit','delete','retweeted_status')):
            continue

        try:
            idx, doc = convert_tweet_to_document(tweet)
            count += 1
            yield idx, doc
        except KeyError:
            logging.warning(f"Could not parse document: {tweet}")
        except:
            logging.error(f"Something went wrong!")
            raise


# setup logging, probably should move this out at some point
logging.basicConfig(format='%(asctime)s - %(message)s')

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']
ELASTICSEARCH_HOST = os.environ['ELASTICSEARCH_HOST']
ELASTICSEARCH_PORT = os.environ['ELASTICSEARCH_PORT']

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
es_header = [{
     'host': ELASTICSEARCH_HOST,
     'port': ELASTICSEARCH_PORT,
    }]

# use the bulk load to ES and a generator on redis
es = Elasticsearch(es_header)

while True:
    
    # keep running, running, running 
    k = ({
        "_index": "twitter-stream",
        "_type" : "tweets",
        "_id"   : idx,
        "_source": doc,
    } for idx, doc in process_queue(r))

    helpers.bulk(es, k)
