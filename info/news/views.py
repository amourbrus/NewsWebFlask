from . import news_blue
from info.utils.common import user_login_data
from flask import g, render_template
from info.models import News, Comment, CommentLike
from info.utils.response_code import RET
from flask import request
from info import db
from flask import jsonify


@news_blue.route("/comment_like",methods = ["POST"])
@user_login_data
def comment_like():
    user = g.user
    if not user:
        return jsonify(errno = RET.SESSIONERR,errmsg = "请登陆才能点赞")

    comment_id = request.json.get("comment_id")
    news_id = request.json.get("news_id")
    # 用户点赞的动作,add表示点赞,remove表示取消点赞
    action = request.json.get("action")

    """
      需求:评论点赞:
          1 首先得知道是谁点赞,user.id
          2 需要知道当前点的是哪条评论 comment_id
    """
    comment = Comment.query.get(comment_id)

    if action == "add":
        # 点赞
        comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,CommentLike.user_id == user.id).first()
        if not comment_like:
            # 如果从数据库里面查询出来的值,没有点赞,才能进行点赞,如果已经点赞了,那么就取消点赞
           comment_like = CommentLike()
           comment_like.comment_id = comment_id
           comment_like.user_id = user.id
           db.session.add(comment_like)
           comment.like_count += 1
    else:
        comment_like = CommentLike.query.filter(CommentLike.comment_id == comment_id,
                                                CommentLike.user_id == user.id).first()
        #  取消点赞
        if comment_like:
           db.session.delete(comment_like)
           comment.like_count -= 1

    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "点赞成功")


"""评论"""
@news_blue.route("/news_comment",methods = ["POST"])
@user_login_data
def news_comment():

    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="请登陆")

    news_id = request.json.get("news_id")
    comment_str = request.json.get("comment")
    parent_id = request.json.get("parent_id")
    # 我评论的是哪条新闻
    news = News.query.get(news_id)

    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str
    # 这个地方需要判断,是因为不可能所有的评论都有父类
    if parent_id:
        comment.parent_id = parent_id

    db.session.add(comment)
    db.session.commit()
    return jsonify(errno = RET.OK,errmsg = "评论成功",data = comment.to_dict())

@news_blue.route("/news_collect", methods=["post"])
@user_login_data
def news_collect():
    user = g.user
    # 新闻收藏
    if not user:
        return jsonify(errno=RET.SERVERERR, errmsg="请登录")
    # 需要收藏的新闻id
    news_id = request.json.get("news_id")
    # 获取到用户的动作，是否收藏
    action = request.json.get("action")
    news = News.query.get(news_id)
    if action == "collect":
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    db.session.commit()
    return jsonify(errno=RET.OK, errmsg="收藏成功")



@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    user = g.user
    """

       右边的热门新闻排序

       """
    # 获取到热门新闻,通过点击事件进行倒叙排序,然后获取到前面10新闻
    news_list = News.query.order_by(News.clicks.desc()).limit(10)

    click_news_list = []

    for news_item in news_list if news_list else []:
        click_news_list.append(news_item.to_dict())

    """detail"""
    news = News.query.get(news_id)
    news.clicks += 1

    """新闻收藏"""
    is_collected = False
    if user:
        if news in  user.collection_news:
            is_collected = True

    """获取到所有评论点赞的数据"""

    """ 查询当前新闻的所有评论 """
    comment_list = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()

    # comments = []
    # for item in comment_list:
    #     comment_dict = item.to_dict()
    #     comments.append(comment_dict)

    # 评论点赞数据返回
    comment_like_ids = []
    if user:
        # 查询出当前用户点赞过的评论，　供下一步查询id
        comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()

        # 当前用户点赞过的评论的ｉｄ－－后面做标记用
        comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]

    comments = []  # 这里两个comments是一样的，而且写两次，一次是登录了的，一次是没有
    for comment_item in comment_list:
        # 展示当前新闻的所有评论，需要做一些标记－－－我点赞过的评论
        comment_dict = comment_item.to_dict()
        comment_dict["is_like"] = False
        if comment_item.id in comment_like_ids:
            comment_dict["is_like"] = True
        comments.append(comment_dict)

    data = {
        # 需要在页面展示用户的数据,所有需要把user对象转换成字典
        "user_info": user.to_dict() if user else None,
        "click_news_list": click_news_list,
        "news": news.to_dict(),
        "is_collected": is_collected,
        "comments": comments
    }

    return render_template("news/detail.html", data=data)

