from dotenv import load_dotenv
load_dotenv()
import os
import redis
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # open new terminal and run following
    # python -c 'import os; print(os.urandom(16))'
    # copy the output string you get (e.g. b'_5#y2L"F4Q8z\n\xec]/')
    # create '.env' file in root
    # in this file add the following line
    # SECRET_KEY= 
    # paste your output string after the equal sign
    # SECRET_KEY = os.environ['SECRET_KEY']
    SECRET_KEY = b'x81\xee(\xc7\x1f\xc5\x8d\xf5\x10]\xc4\x87$\xd7\xd3w'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    # download redis (or alternatively use docker - https://testdriven.io/blog/flask-server-side-sessions/)
    # https://redis.io/docs/getting-started/installation/
    # open new terminal and run your redis server
    # there should be info about which url/port its running on, e.g. 127.0.0.1:6379
    # open .env and add following line
    # REDIS_URL='redis://127.0.0.1:6379' 
    # edit url/port if necessary
    # SESSION_REDIS = redis.from_url(os.environ['REDIS_URL'])
    SESSION_REDIS = redis.from_url('redis://red-cfik4chgp3jh03khtvt0:6379')
