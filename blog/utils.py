#!/usr/bin/env python
# encoding=utf-8
"""
@author: v_linlgan
@contact: v_linlgan@tencent.com
@software: Pycharm 2020.2
@file: utils.py
@time: 2021/2/3-12:46
@desc:
"""
import re
from random import randint
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from settings.models import Site
from bs4 import BeautifulSoup
import hashlib
import time
import requests
from urllib.parse import urlencode, unquote_plus
from settings.models import Options


def is_ends_with_slash(str1):
    result = re.search('/$', str1)
    if result:
        return str1[:-1]
    else:
        return str1


def send_email4comment(form, curr_post):
    comment_content = form.cleaned_data['comment_content']
    site_url = Site.objects.get(option_flag='site_url').option_value
    site_url = is_ends_with_slash(site_url)
    superuser = User.objects.filter(is_superuser=True)[0]
    superuser_email = superuser.email
    comment_content_html = '<div>' + comment_content + '</div>'
    soup = BeautifulSoup(comment_content_html, 'html5lib')
    comment_content_text = soup.find_all('div')[0].get_text().replace('\n', '')
    send_mail(
        '【{}】收到了新的评论！'.format(curr_post.title),
        '{0}\n{1}'.format(site_url + '/' + curr_post.slug,
                          comment_content_text),
        settings.EMAIL_HOST_USER,
        [superuser_email],
        fail_silently=False)


def send_email4order(fee, title, order_id):
    superuser = User.objects.filter(is_superuser=True)[0]
    superuser_email = superuser.email
    send_mail(f'收到{fee}元付费阅读订单',
              f'{title}\n订单编号：{order_id}',
              settings.EMAIL_HOST_USER,
              [superuser_email],
              fail_silently=False)


def get_order_id():
    def random_with_n_digits(n):
        range_start = 10 ** (n - 1)
        range_end = (10 ** n) - 1
        return randint(range_start, range_end)

    base_code = datetime.now().strftime('%Y%m%d%H%M%S')
    return base_code + str(random_with_n_digits(8))


class HupiPayment(object):
    AppId = Options.objects.get(option_flag='hupi_appid').option_value
    AppSecret = Options.objects.get(option_flag='hupi_app_secret').option_value
    pay_api_url = 'https://api.xunhupay.com/payment/do.html'
    query_api_url = 'https://api.xunhupay.com/payment/query.html'

    def __init__(self, total_fee, return_callback_url,
                 trade_order_id, title):
        self.return_callback_url = return_callback_url
        self.total_fee = total_fee
        self.trade_order_id = trade_order_id
        self.title = title

    @staticmethod
    def k_sort(d):
        return [(k, d[k]) for k in sorted(d.keys())]

    def curl(self, data, url):
        data['hash'] = self.sign(data)
        site_url = Site.objects.get(option_flag="site_url").option_value
        headers = {"Referer": site_url}
        r = requests.post(url, data=data, headers=headers)
        return r

    def sign(self, attributes):
        attributes = self.k_sort(attributes)
        m = hashlib.md5()
        m.update((unquote_plus(urlencode(attributes)) + self.AppSecret).encode(encoding='utf-8'))
        sign = m.hexdigest()
        return sign

    def pay(self):
        data = {
            "version": "1.1",
            "lang": "zh-cn",
            "plugins": "django",
            "appid": self.AppId,
            "trade_order_id": self.trade_order_id,
            "payment": 'wechat',
            "is_app": "Y",
            "total_fee": self.total_fee,
            "title": self.title,
            "description": "",
            "time": str(int(time.time())),
            "notify_url": self.return_callback_url.split('?')[0] + '/notify',  # 回调URL（订单支付成功后，WP开放平台会把支付成功消息异步回调到这个地址上）
            "return_url": self.return_callback_url,  # 支付成功url(订单支付成功后，浏览器会跳转到这个地址上)
            "callback_url": self.return_callback_url.split('?')[0],  # 商品详情URL或支付页面的URL（移动端，商品支付失败时，会跳转到这个地址上）
            "nonce_str": str(int(time.time())),  # 随机字符串(一定要每次都不一样，保证请求安全)
        }
        pay_order = self.curl(data, self.pay_api_url)
        if pay_order.json()['errmsg'] == 'success!':
            return pay_order.json()['url']
        return False

    def check(self):  # 回调检测
        data = {
            "appid": self.AppId,
            "out_trade_order": self.trade_order_id,
            "time": str(int(time.time())),
            "nonce_str": str(int(time.time())),  # 随机字符串(一定要每次都不一样，保证请求安全)
        }
        result = self.curl(data, self.query_api_url)
        if result.json()['data']['status'] == "OD":  # OD(支付成功)，WP(待支付),CD(已取消)
            return True
        return False
