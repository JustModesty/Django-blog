from django.shortcuts import render

# 导入 HttpResponse 模块
from django.http import HttpResponse

from .models import ArticlePost
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown
import logging
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

logging.basicConfig(filename='blog.log')


# 视图函数
def article_list(request):
    # 修改变量名称（articles -> article_list）
    # article_list = ArticlePost.objects.all()
    # article_list = ""

    # 根据GET请求中查询条件
    # 返回不同排序的对象数组
    if request.GET.get('order') == 'total_views':
        article_list = ArticlePost.objects.all().order_by('-total_views')
        order = 'total_views'
    else:
        article_list = ArticlePost.objects.all()
        order = 'normal'

    paginator = Paginator(article_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)

    context = {'articles': articles, 'order': order}
    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    # context = {'article': article}
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 将markdown语法渲染成HTML样式
    article.body = markdown.markdown(article.body,
                                     extension=['markdown.extensions.extra', 'markdown.extensions.highlight', ])
    context = {'article': article}
    return render(request, 'article/detail.html', context)


# 检查登录
@login_required(login_url='/userprofile/login/')
def article_create(request):
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            # logging.debug()
            # 指定目前登录的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            new_article.save()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        context = {'article_post_form': article_post_form}
        return render(request, 'article/create.html', context)


@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    article.delete()
    return redirect("article:article_list")


# 更新文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)

    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = {'article': article, 'article_post_form': article_post_form}
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)
