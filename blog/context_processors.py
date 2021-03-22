#!/usr/bin/env python3
# coding = 'utf-8'
"""
@Time    : 2020/12/27-11:55
@Author  : sharp
@FileName: context_processors.py.py
@Software: PyCharm
@Blog    ：https://www.sharpgan.com/
"""
import math
import datetime
from settings.models import Site, Options
from django.contrib.auth.models import User
from urllib.parse import quote
from blog.models import Category, Post, Comments, Tag
from settings.models import FriendLink
from .utils import is_ends_with_slash


class CategoryProcessor(object):
    @staticmethod
    def get_category_list():
        category_list = []
        for cat in Category.objects.all():
            count = Post.objects.filter(category_id=cat.id).count()
            category_list.append({'name': cat.category_name,
                                  'slug': quote(cat.category_name),
                                  'count': count, 'id': cat.id})
        return category_list


class CommentsProcessor(object):
    @staticmethod
    def get_recent_comments():
        comments_num = int(Site.objects.get(option_flag='recent_comment_num').option_value)
        comments_list = []
        comm_approved = Comments.objects.filter(
            approved='approved').order_by('-comment_date')[0: comments_num]
        for comm in comm_approved:
            post = Post.objects.get(id=comm.post_id)
            post_title = post.title
            post_slug = post.slug
            comments_list.append({'username': comm.user_name,
                                  'content': comm.content,
                                  'comment_id': comm.id,
                                  'post_title': post_title,
                                  'post_slug': post_slug,
                                  'comment_date': comm.comment_date,
                                  'email': comm.email})
        return comments_list


class ArchiveProcessor(object):
    @staticmethod
    def get_archive_list_and_count():
        archive_list_and_count = []
        archive_list = Post.objects.distinct_date()
        for ar in archive_list:
            year = ar[0:4]
            month = ar[5:7]
            count = Post.objects.filter(post_date__icontains=year + '-' + month).count()
            archive_list_and_count.append({'year': year,
                                           'month': month,
                                           'archive_count': count})
        return archive_list_and_count


class TagCloudProcessor(object):
    @staticmethod
    def get_tag_cloud_list():
        tags_list = Tag.objects.all()
        order = 1
        tag_dict_list = []
        for tag in tags_list:
            tag_count = tag.post_set.count()
            if tag_count >= 1:
                tag_dict_list.append({'tag_name': tag.tag_name, 'tag_id': tag.id,
                                      'tag_count': tag.post_set.count(),
                                      'tag_slug': quote(tag.tag_name),
                                      'order': order})
            order = order + 1
        return tag_dict_list

    def compute_tag_cloud_size(self):
        tag_dict_list = self.get_tag_cloud_list()
        tag_count_list = [tag['tag_count'] for tag in tag_dict_list]
        count_max = max(tag_count_list)
        font_min = 8
        font_max = 22
        tag_dict_list_with_font_size = []
        for tag_dict in tag_dict_list:
            if count_max > 1:
                tag_count = math.log(tag_dict['tag_count'])
                tag_dict['font_size'] = tag_count / math.log(count_max) * (font_max - font_min) + font_min
            else:
                tag_dict['font_size'] = font_min
            tag_dict_list_with_font_size.append(tag_dict)

        return tag_dict_list_with_font_size


def add_variable_to_context(request):
    curr_year = datetime.datetime.now().year
    superuser = User.objects.filter(is_superuser=True)[0]
    superuser_name = superuser.username.lower()
    superuser_email = superuser.email
    police_num = Site.objects.get(option_flag="police_num").option_value
    icp_num = Site.objects.get(option_flag="icp_num").option_value
    footer_desc = Site.objects.get(option_flag="footer_desc").option_value
    site_name = Site.objects.get(option_flag="site_name").option_value
    site_url = Site.objects.get(option_flag='site_url').option_value
    site_separator = Site.objects.get(option_flag='site_separator').option_value
    site_beginning = Site.objects.get(option_flag='site_beginning').option_value
    site_subtitle = Site.objects.get(option_flag='site_subtitle').option_value
    site_brand_title = Site.objects.get(option_flag='site_brand_title').option_value
    site_brand_desc = Site.objects.get(option_flag='site_brand_desc').option_value
    site_sidebar_adsense = Options.objects.get(option_flag='site_sidebar_adsense').option_value
    google_or_baidu_analytics_code = Options.objects.get(option_flag='google_or_baidu_analytics_code').option_value
    anti_adblock_hint = Options.objects.get(option_flag='anti_adblock_hint').option_value
    github_link = Site.objects.get(option_flag='github_link').option_value
    friend_link_list = FriendLink.objects.all()
    cate = CategoryProcessor()
    comment = CommentsProcessor()
    archive = ArchiveProcessor()
    tag = TagCloudProcessor()
    context = {'site_name': site_name,
               'police_num': police_num,
               'icp_num': icp_num,
               'footer_desc': footer_desc,
               'site_separator': site_separator,
               'site_beginning': site_beginning,
               'superuser_name': superuser_name,
               'curr_year': curr_year,
               'category_list': cate.get_category_list(),
               'site_url': is_ends_with_slash(site_url),
               'archive_list_and_count': archive.get_archive_list_and_count(),
               'comments_list_sidebar': comment.get_recent_comments(),
               'tag_cloud_list': tag.compute_tag_cloud_size(),
               'superuser_email': superuser_email,
               'site_subtitle': site_subtitle,
               'site_brand_desc': site_brand_desc,
               'site_brand_title': site_brand_title,
               'friend_link_list': friend_link_list,
               'site_sidebar_adsense': site_sidebar_adsense,
               'google_or_baidu_analytics_code': google_or_baidu_analytics_code,
               'anti_adblock_hint': anti_adblock_hint,
               'github_link': github_link}
    return context
