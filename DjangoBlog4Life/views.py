#!/usr/bin/env python3
# coding = 'utf-8'
"""
@Time    : 2020/12/18-22:36
@Author  : sharp
@FileName: views.py
@Software: PyCharm
@Blog    ：https://www.sharpgan.com/
"""

from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView
from blog.models import Post, Category, Tag, Comments
from settings.models import Site, Options
from urllib.parse import unquote
from DjangoBlog4Life.secret_keys import ADMIN_URL_SECRET
from blog.forms import CommentsFormForLoggedIn, CommentsFormForNotLoggedIn
from django.contrib.auth.models import User
from blog.utils import send_email4comment, send_email4order
from blog.utils import get_order_id, is_ends_with_slash
from blog.utils import HupiPayment
from datetime import datetime
from django.http import HttpResponse 


class PaginatorBase(object):
    @staticmethod
    def get_curr_page(items_list, page_num, items_per_page):
        paginator = Paginator(items_list, items_per_page)
        try:
            current_page = paginator.page(page_num)
        except EmptyPage:
            current_page = paginator.page(1)
        except PageNotAnInteger:
            current_page = paginator.page(1)
        return current_page, paginator


class IndexPaginator(TemplateView, PaginatorBase):
    site_description = Site.objects.get(option_flag='site_description').option_value
    site_keywords = Site.objects.get(option_flag='site_keywords').option_value

    def get(self, request, page_num=1, **kwargs):
        posts_list = Post.objects.all()
        current_page, paginator = self.get_curr_page(posts_list, page_num, 8)
        site_url = Site.objects.get(option_flag="site_url").option_value

        context = {'curr_page': current_page,
                   'prefix': '',
                   'is_index': 'YES',
                   'page_count': paginator.num_pages,
                   'page_url': site_url,
                   'page_description': self.site_description,
                   'page_keywords': self.site_keywords}
        return render(request, 'index.html', context)


class CategoryPaginator(TemplateView, PaginatorBase):
    def get(self, request, slug, page_num=1):
        cate_name = unquote(slug)
        category_id = Category.objects.get(category_name=cate_name).id
        posts_list = Post.objects.filter(category_id=category_id)
        current_page, paginator = self.get_curr_page(posts_list, page_num, 4)
        category_literal = '分类：'
        paginator_title = category_literal + cate_name
        prefix = '/category/{}'.format(slug)
        context = {'curr_page': current_page,
                   'is_index': 'NO',
                   'paginator_title': paginator_title,
                   'prefix': prefix,
                   'page_count': paginator.num_pages,
                   'page_title': cate_name,
                   'page_url': prefix,
                   'page_description': paginator_title,
                   'page_keywords': cate_name}
        return render(request, 'index.html', context)


class ArchivePaginator(TemplateView, PaginatorBase):
    site_description = Site.objects.get(option_flag='site_description').option_value
    site_keywords = Site.objects.get(option_flag='site_keywords').option_value

    def get(self, request, year, month, page_num=1):
        posts_list = Post.objects.filter(post_date__icontains=str(year) + '-' + str(month).zfill(2))
        current_page, paginator = self.get_curr_page(posts_list, page_num, 4)
        archive_literal = '月份：'
        title = archive_literal + '{0}-{1}'.format(year, month)
        url = '/{0}/{1}'.format(year, month)
        context = {'curr_page': current_page,
                   'paginator_title': title,
                   'prefix': url,
                   'page_count': paginator.num_pages,
                   'page_title': title,
                   'page_url': url,
                   'page_keywords': self.site_keywords,
                   'page_description': self.site_description,
                   'is_index': 'NO'}
        return render(request, 'index.html', context)


class TagPaginator(TemplateView, PaginatorBase):
    def get(self, request, slug, page_num=1):
        tag_name = unquote(slug)
        tag = Tag.objects.get(tag_name=tag_name)
        posts_list = tag.post_set.all()
        current_page, paginator = self.get_curr_page(posts_list, page_num, 4)
        url = '/{0}/{1}'.format('tag', tag_name)
        tag_literal = '标签：'
        context = {'prefix': url,
                   'is_index': 'NO',
                   'page_title': tag_name,
                   'page_count': paginator.num_pages,
                   'curr_page': current_page,
                   'page_url': url,
                   'page_description': tag_literal + tag_name,
                   'page_keywords': tag_name,
                   'paginator_title': tag_literal + tag_name + ' ({})'.format(tag.post_set.count()), }
        return render(request, 'index.html', context)


class FullTextSearch(TemplateView, PaginatorBase):
    def get(self, request, page_num=1, *args):
        query_str = request.GET.get('q')
        search_literal = "搜索关键字："
        if not query_str:
            response = redirect('/')
            return response
        else:
            posts_list = Post.objects.filter(content__icontains=query_str)
            current_page, paginator = self.get_curr_page(posts_list, page_num, 4)
            context = {
                'is_index': 'NO',
                'page_count': paginator.num_pages,
                'query_str': query_str,
                'page_url': '/search?q=' + query_str,
                'page_title': search_literal + query_str,
                'page_keywords': query_str,
                'page_description': search_literal + query_str,
                'curr_page': current_page,
                'paginator_title': search_literal + query_str + ' ({})'.format(posts_list.count()),
            }
            return render(request, 'search.html', context)

def order_notify(request, slug):
     if request.method == 'POST':
        order_status = request.POST.get('status')
        order_fee = request.POST.get('total_fee')
        order_id = request.POST.get('trade_order_id')
        order_title = request.POST.get('order_title')
        if order_status == 'OD': 
            send_email4order(fee=order_fee, title=order_title, order_id=order_id)
            return HttpResponse('success') 
 
def article_detail(request, slug, comment_page_num=1):
    def save_data(form, user_name, email, is_approved):
        post_id = Post.objects.get(slug=slug).id
        comment_parent_id_form = form.cleaned_data['comment_parent']
        comment_parent_id_obj = None if comment_parent_id_form == 0 \
            else Comments.objects.get(id=comment_parent_id_form)
        comment_content = form.cleaned_data['comment_content']
        comment_obj = Comments(post_id=post_id,
                               user_name=user_name,
                               email=email,
                               content=comment_content,
                               parent=comment_parent_id_obj,
                               approved=is_approved)
        comment_obj.save()

    def check_date(order_id):
        try:
            order_date = datetime.strptime(order_id[0:14], '%Y%m%d%H%M%S')
            now_date = datetime.now()
            delta_date = now_date - order_date
            if delta_date.total_seconds() > 259200:
                return 'NOT_PAY'
            else:
                return 'PAID'
        except ValueError:
            return 'NOT_PAY'

    comment_anchor = None
    paginator = PaginatorBase()
    curr_post = Post.objects.get(slug=slug)
    site_url = Site.objects.get(option_flag='site_url').option_value
    order_id = str(get_order_id())
    full_article_url = is_ends_with_slash(site_url) + '/' + slug
    # below is for dev use
    # full_article_url = 'http://127.0.0.1:8000/' + slug
    callback_url = full_article_url + '?order_id=' + order_id
    does_pay = 'NOT_PAY'
    if request.method == 'POST':
        if request.user.is_authenticated:
            comment_anchor = '#respond'
            form = CommentsFormForLoggedIn(request.POST)
            user_name = request.user
            email = User.objects.get(username=user_name).email
            if form.is_valid():
                save_data(form=form, user_name=user_name,
                          email=email, is_approved='approved')
        else:
            comment_anchor = '#respond'
            form = CommentsFormForNotLoggedIn(request.POST)
            if form.is_valid():
                save_data(form=form,
                          user_name=form.cleaned_data['user_name'],
                          email=form.cleaned_data['user_email'],
                          is_approved='refused')
                send_email4comment(form=form, curr_post=curr_post)
                form.add_error(field='comment_content', error="你的评论正在被站长审核中...")
    else:
        if request.user.is_authenticated:
            form = CommentsFormForLoggedIn()
        else:
            form = CommentsFormForNotLoggedIn()

        order_id4check = request.GET.get('order_id', default='None')
        if order_id4check != 'None':
            hupi = HupiPayment(total_fee=curr_post.price,
                               return_callback_url=callback_url,
                               trade_order_id=order_id4check,
                               title=curr_post.title)
            try:
                pay_check = hupi.check()
                if pay_check:
                    does_pay = 'PAID'
                    send_email4order(fee=curr_post.price,
                                     title=curr_post.title,
                                     order_id=order_id4check)
                # 检查订单是否超过3天
                does_pay = check_date(order_id4check)
            # 以下对错误订单号进行处理
            except TypeError:
                pass

    posts_list = Post.objects.all()
    category_name = Category.objects.get(id=curr_post.category_id).category_name
    tag_list = Tag.objects.filter(post=curr_post.id)
    next_post = posts_list.filter(id__gt=curr_post.id).order_by('id').first()
    previous_post = posts_list.filter(id__lt=curr_post.id).order_by('-id').first()
    site_comment_switch = Site.objects.get(option_flag='site_comment_switch').option_value
    comments_list = Comments.objects.filter(post_id=curr_post.id, approved='approved')
    curr_comment_page, _ = paginator.get_curr_page(comments_list, comment_page_num, 20)
    before_content_adsense = Options.objects.get(option_flag='before_content_adsense').option_value
    after_content_adsense = Options.objects.get(option_flag='after_content_adsense').option_value
    context = {'curr_post': curr_post,
               'is_index': 'NO',
               'category_name': category_name,
               'tag_list': tag_list,
               'next_post': next_post,
               'previous_post': previous_post,
               'page_description': curr_post.content,
               'page_keywords': ','.join([tag.tag_name for tag in tag_list]),
               'page_url': '/' + slug,
               'page_title': curr_post.title,
               'comment_is_enabled': curr_post.comment_status,
               'site_comment_switch': site_comment_switch,
               'curr_user': request.user,
               'comments_list': comments_list,
               'curr_comment_page': curr_comment_page,
               'admin_url_secret': ADMIN_URL_SECRET,
               'comment_form': form,
               'anchor': comment_anchor,
               'before_content_adsense': before_content_adsense,
               'after_content_adsense': after_content_adsense,
               'order_id': order_id,
               'callback_url': callback_url,
               'does_pay': does_pay
               }
    return render(request, 'article.html', context)
