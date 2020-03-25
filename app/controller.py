import os

script = os.environ['PROCESSING_SCRIPT']

if script == 'redis-to-elastic':
    os.system("python redis-to-elastic.py")
elif script == 'twitter-to-redis':
    os.system("python twitter-to-redis.py")
else:
    print("unknown script %s" % script)
