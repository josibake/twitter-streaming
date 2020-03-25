FROM python:3.7

# install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy in everything else:
ADD app/controller.py /app/controller.py
ADD app/redis-to-elastic.py /app/redis-to-elastic.py
ADD app/twitter-to-redis.py /app/twitter-to-redis.py

# set working directory and run script
WORKDIR /app
CMD ["python3", "controller.py"]
