from flask import make_response
from flask import request, jsonify

from info import constants
from info import redis_store
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




