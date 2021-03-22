from django import template
from settings.models import Site, Options
from urllib.parse import quote
import os
import re
import hashlib
from bs4 import BeautifulSoup
from ..utils import is_ends_with_slash
from ..utils import HupiPayment
from django.utils.html import format_html

register = template.Library()


@register.filter
def empty2br(str1):
    tmp_list = []
    for s in str1.splitlines():
        if s:
            tmp_list.append(s)
        else:
            tmp_list.append('<br><br>')
    return os.linesep.join(tmp_list)


@register.filter
def is_highlightjs(str1):
    tmp_list = []
    for s in str1.splitlines():
        if '<pre>' in s:
            tmp_list.append(s.replace('<pre>', "<pre class='pure-highlightjs line-numbers'>"))
        else:
            tmp_list.append(s)
    return os.linesep.join(tmp_list)


@register.filter
def media_replace(str1):
    site_url = Site.objects.get(option_flag="site_url").option_value
    site_url = is_ends_with_slash(site_url)
    tmp_list = []
    for s in str1.splitlines():
        if site_url in s:
            tmp_list.append(s.replace(site_url + '/wp-content/', '/media/'))
        else:
            tmp_list.append(s)
    return os.linesep.join(tmp_list)


@register.filter
def str2number(str1):
    result = re.search(r'(\d+)', str1)
    return result.group(1)


@register.filter
def domain_extractor(str1):
    result = re.search(r'(http://|https://)?(\w+)\.(\w+)\.(\w+)/?', str1)
    return '.'.join(result.groups()[2:4])


@register.filter
def to_slug(str1):
    return quote(str1)


@register.filter
def gen_gavatar_link(email, size):
    gavatar_mirror = Options.objects.get(option_flag='gavatar_mirror').option_value
    if not gavatar_mirror:
        gavatar_url = 'https://www.gravatar.com/avatar/'
    else:
        gavatar_url = gavatar_mirror

    md = hashlib.md5()
    md.update(email.encode('utf-8'))
    return gavatar_url + md.hexdigest() + '?s=' + str(size) + '&r=g'


@register.filter
def is_parent(is_leaf_node):
    if not is_leaf_node:
        return 'parent'
    else:
        return ''


@register.filter
def extract_content(content, num):
    content_html = '<div>' + content + '</div>'
    soup = BeautifulSoup(content_html, 'html5lib')
    return soup.find_all('div')[0].get_text().replace('\n', '')[0:num]


@register.simple_tag
def enable_paywall(content, order_id, callback_url, fee, title):
    replaced_html = """
    <div style="border:2px dotted #009688; 
    width: 800px;height: 200px;vertical-align: middle;display: table-cell;text-align:center;">
        这一部分是收费内容,请<b><a href='{payment_url}'>点击此处</a></b>跳转到微信支付控制台付费后再进行阅读！
        如果你使用手机浏览本篇博客,只需将博文链接复制后发送给微信的文件传输助手,然后打开就能在手机端进行支付了。
        <span style='color:red'>付费后请妥善保存浏览器地址栏中含有order_id的本篇博文链接,订单有效期为3天,
        3天后需重新付费阅读~</span>
    </div>
    """
    hupi = HupiPayment(total_fee=fee,
                       return_callback_url=callback_url,
                       trade_order_id=order_id,
                       title=title)
    payment_url = hupi.pay()
    # 如果虎皮椒微信支付控制台挂掉了，则支付链接为当前页面
    if not payment_url:
        replaced_html = replaced_html.format('#')
    else:
        replaced_html = replaced_html.format(payment_url=payment_url)

    result = re.sub(r'\[\$\](.*?)\[/\$\]', replaced_html, content, flags=re.DOTALL)
    return format_html(result)

