from . import news_blue
from info.utils.common import user_login_data
from flask import g, render_template
from info.models import News


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

    data = {
        # 需要在页面展示用户的数据,所有需要把user对象转换成字典
        "user_info": user.to_dict() if user else None,
        "click_news_list": click_news_list,
        "news": news.to_dict(),
    }
    return render_template("news/detail.html", data=data)

