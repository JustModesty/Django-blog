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
logging.basicConfig(filename='blog.log')

# 视图函数
def article_list(request):
    articles = ArticlePost.objects.all()
    context = {'articles': articles}
    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    # context = {'article': article}

    # 将markdown语法渲染成HTML样式
    article.body = markdown.markdown(article.body,
                                     extension=['markdown.extensions.extra', 'markdown.extensions.highlight', ])
    context = {'article': article}
    return render(request, 'article/detail.html', context)


def article_create(request):
    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            # logging.debug()
            new_article.author = User.objects.get(id=1)
            new_article.save()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        context = {'article_post_form': article_post_form}
        return render(request, 'article/create.html', context)


def article_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    article.delete()
    return redirect("article:article_list")
