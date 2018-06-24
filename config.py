import redis


class Config(object):   # 5
    SECRET_KEY = "AYHGFAUSGH897afg"   # SECRET_KEY
    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/anewdata"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis 数据库　　ip 和 端口
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # flask session
    # session类型：redis
    SESSION_TYPE = "redis"
    # session的过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2
    # 初始化session-redis
    # 这个redis是用户存储flask_session
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 开启session签名
    SESSION_USE_SIGNER = True


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}