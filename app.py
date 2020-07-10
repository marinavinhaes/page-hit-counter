import os
import socket
import traceback
from flask import Flask
from redis import Redis

hostname = socket.gethostname()
app = Flask(__name__)


@app.route('/')
def default():
    REDIS_HOST = os.environ['REDIS_HOST']
    REDIS_PORT = os.environ['REDIS_PORT']

    redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
    redis.incr(hostname)
    hits = redis.get(hostname)
    return '{0} recebeu {1} visitas'.format(hostname, hits)

@app.route('/healthcheck')
def healthcheck():
    return 'OK'


if __name__ == "__main__":
    app.run(host= "0.0.0.0", debug=False)
