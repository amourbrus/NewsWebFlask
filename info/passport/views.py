import random

from datetime import datetime
from flask import make_response
from flask import request, jsonify
from flask import session

from info import constants, db
from info import redis_store
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from . import passport_blue


@passport_blue.route("/image_code")
def imageCode():
    print(request.url)
    code_id = request.args.get("code_id")
    print(code_id)

    if not code_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # re1,图片验证码的名字　re2, 图片验证码的内容　re3　验证码的图片
    name, text, image = captcha.generate_captcha()
    print("图片验证码的内容---"+ text)
    # 存数据到redis 　para1 key, 唯一，刚好使用图片生产的ｕｕｉｄ,　第二个是value, 第三个是过期时间
    redis_store.set("sms_code_" + code_id, text, constants.SMS_CODE_REDIS_EXPIRES)

    # 初始化一个响应体
    resp = make_response(image)

    return resp


@passport_blue.route("/sms_code", methods=["post"])
def sms_code():
    print("web font send the address--->"+request.url)
    # 获取用户填写的手机号
    mobile = request.json.get("mobile")
    # get 用户填写的图片验证码
    image_code_user = request.json.get("image_code")
    # 获取图片验证码的编号
    image_code_id = request.json.get("image_code_id")

    # 获取到redis中存的ｕｕｉｄ,　做比对用
    redis_image_id = redis_store.get("sms_code_" + image_code_id)

    if not redis_image_id:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期")

    # 判断用户输入的验证码是否有问题
    if image_code_user.lower() != redis_image_id.lower():
        return jsonify(errno=RET.PARAMERR, errmsg="验证码输入错误---")

    # 随机生成验证码, testing
    code_random = random.randint(0,999999)
    # 保证生成的是6位
    sms_code = "%06d"%code_random
    print("短信验证码---" + sms_code)

    redis_store.set("code_" + mobile, sms_code, 300)

    # statusCode = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # if statusCode != 0:
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信数百")

    return jsonify(errno=RET.OK, errmsg="send success")


# 注册
@passport_blue.route("/register",methods = ["POST"])
def register():
    mobile = request.json.get("mobile")
    # 用户输入的手机验证码
    smscode = request.json.get("smscode")
    password = request.json.get("password")

    # if not re.match("1[345678]\d{9}",mobile):
    #     return jsonify(errno = RET.PARAMERR,errmsg = "手机号码输入错误")

    # 校验手机验证码
    # 从redis里面获取数据里面缓存的手机验证码
    redis_sms_code = redis_store.get("code_"+mobile)

    if redis_sms_code != smscode:
        return jsonify(errno = RET.PARAMERR,errmsg = "验证码输入错误")

    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password
    # datetime.now() 获取到当前的时间,存储到数据库
    user.last_login = datetime.now()

    db.session.add(user)
    db.session.commit()
    # 把用户注册的数据设置给session
    session["mobile"] = user.mobile
    session["user_id"] = user.id
    session["nick_name"] = user.mobile

    return jsonify(errno = RET.OK,errmsg = "注册成功")


@passport_blue.route("/login" ,methods = ["POST"])
def login():
    mobile = request.json.get("mobile")
    # ctrl + d 复制
    password = request.json.get("password")

    user = User.query.filter(User.mobile == mobile).first()

    if not user:
        return jsonify(errno = RET.NODATA,errmsg = "please register first .. ")

    # 检查密码是否正确
    if not user.check_password(password):
        return jsonify(errno = RET.PARAMERR,errmsg = "please type into true password")

    db.session.commit()

    # 把用户注册的数据设置给session

    session["mobile"] = user.mobile
    session["user_id"] = user.id
    session["nick_name"] = user.mobile

    # 最后用户登陆的时间
    user.last_login = datetime.now()

    return jsonify(errno = RET.OK,errmsg = "login success")


@passport_blue.route("/logout", methods=["post"])
def logout():
    # 退出,清空session里面的数据
    session.pop("mobile",None)
    session.pop("user_id",None)
    session.pop("nick_name",None)
    return jsonify(errno = RET.OK,errmsg = "退出成功")

