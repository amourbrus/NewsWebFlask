from logging.handlers import RotatingFileHandler

import logging

from flask import g
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config, DevelopmentConfig, ProductionConfig, config_map
from flask import Flask
import redis
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from flask_session import Session

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)




db = SQLAlchemy()
redis_store = None

def create_app(config_name):
    app = Flask(__name__)

    class_name = config_map.get(config_name)
    app.config.from_object(class_name)

    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=class_name.REDIS_HOST, port=class_name.REDIS_PORT, decode_responses=True)

    from info.utils.common import index_class
    app.add_template_filter(index_class, "indexClass")

    Session(app)

    CSRFProtect(app)

    # 往浏览器写入csrf_token
    @app.after_request
    def after_request(response):
        # 调用函数生成　csrf_token
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token", csrf_token)
        return response

    from info.utils.common import user_login_data  # 待解决：这个放到开头会报错
    # 当前的４０４页面表示全局所有的，所以把当前代码写到__init__
    # errorhandler：表示捕获http异常
    @app.errorhandler(404)
    @user_login_data
    def not_found(e):
        user = g.user
        data = {
            "user_info": user.to_dict() if user else None
        }
        return render_template("news/404.html", data=data)

    # 注册蓝图
    from info.index import index_blue
    app.register_blueprint(index_blue)

    from info.passport import passport_blue
    app.register_blueprint(passport_blue)

    from info.news import news_blue
    app.register_blueprint(news_blue)

    from info.user import profile_blue
    app.register_blueprint(profile_blue)

    from info.admin import admin_blue
    app.register_blueprint(admin_blue)

    return app
