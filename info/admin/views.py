import time
from datetime import datetime, timedelta

from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from info.admin import admin_blue
from info.models import User
from info.utils.common import user_login_data

@admin_blue.route('/login', methods=['GET','POST'])
@user_login_data
def admin_login():
    if request.method == 'GET':
        # 去 session 中取指定的值
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)
        # 如果用户id存在，并且是管理员，那么直接跳转管理后台主页
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter(User.mobile == username, User.is_admin == True).first()

    if not user:
        return render_template('admin/login.html', errmsg='NOt USER')

    if not user.check_password(password):
        return render_template('admin/login.html', errmsg='not password')

    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['is_admin'] = True
    session['nick_name'] = user.nick_name
    return redirect(url_for('admin.admin_index'))


@admin_blue.route("/index")
@user_login_data
def admin_index():
    user = g.user
    return render_template("admin/index.html",user=user.to_dict())


@admin_blue.before_request
def check_admin():
    is_admin = session.get('is_admin', False)
    if not is_admin and not request.url.endswith('/admin/login'):
        return redirect('/')


@admin_blue.route("/user_count")
def user_count():
    total_count = 0
    mon_count = 0
    day_count = 0
    #　只查询普通用户，因为admin是我们手动添加的，不算潜在的用户
    total_count = User.query.filter(User.is_admin == False).count()
    # 获取到当前时间
    t = time.localtime()
     # 获取到本月的时间
    # 获取到６月１号
    mon_begin = "%d-%02d-01"%(t.tm_year,t.tm_mon)
    # 第一个参数传输时间
    # 第二个参数表示你需要得到的格式化时间
    # 获取到６月１号0分0秒
    mon_begin_date = datetime.strptime(mon_begin,"%Y-%m-%d")

    mon_count = total_count = User.query.filter(User.is_admin == False,User.create_time > mon_begin_date).count()

    # 获取到今天的时间
    day_begin = "%d-%02d-%02d" % (t.tm_year, t.tm_mon,t.tm_mday)
    # 第一个参数传输时间
    # 第二个参数表示你需要得到的格式化时间
    day_begin_date = datetime.strptime(day_begin, "%Y-%m-%d")

    day_count  = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()

    # 统计一个月每天用户的增加数量(活跃用户)
    # 往前面倒腾一个月
    # for i range(0,31):
    #     查询一天:User.create_time >= 今日的0点0分0秒  and User.create_time < 今日的23点59分59秒(明天0点0分0秒)
    # # day_count  = User.query.filter(User.is_admin == False,
    # #                                User.create_time >= 今日的0点0分0秒 and User.create_time < 今日的23点59分59秒(明天0点0分0秒)).count()


    # 获取到今天的时间
    # 2018-06-21
    today_begin = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    # 第一个参数传输时间
    # 第二个参数表示你需要得到的格式化时间
    # 2018-06-21- 00:00:00
    today_begin_date = datetime.strptime(today_begin, "%Y-%m-%d")
    active_count = []
    active_time = []
    for i in  range(0,31):
        # 今天的开始时间 2018-06-21- 00:00:00
        begin_date = today_begin_date - timedelta(days = i)
        # 明天的开始时间 2018-06-22- 00:00:00(今天的结束时间 2018-06-21- 23:59:59)
        end_date = today_begin_date - timedelta(days = (i - 1))

        count = User.query.filter(User.is_admin == False,
                User.create_time >= begin_date ,
                                      User.create_time < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime("%Y-%m-%d"))

    active_count.reverse()
    active_time.reverse()
    data = {
        "total_count":total_count,
        "mon_count":mon_count,
        "day_count":day_count,
        "active_count":active_count,
        "activate_time":active_time
    }
    return render_template("admin/user_count.html",data = data)

