# coding = 'utf-8'

from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse

COMMENT_STATUS_CHOICES = (
    ('closed', 'closed'),
    ('opened', 'opened'),
)

COMMENT_APPROVED_CHOICES = (
    ('approved', 'approved'),
    ('refused', 'refused'),
)

IS_WORDPRESS = (
    ('yes', 'yes'),
    ('no', 'no')
)


class Category(models.Model):
    category_name = models.CharField(max_length=200)

    def __str__(self):
        if self.category_name:
            return self.category_name

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name


class Tag(models.Model):
    tag_name = models.TextField(max_length=100)

    def __str__(self):
        if self.tag_name:
            return self.tag_name

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name


class PostManager(models.Manager):
    def distinct_date(self):  # 该管理器定义了一个distinct_date方法，目的是找出所有的不同日期
        distinct_date_list = []  # 建立一个列表用来存放不同的日期 年-月
        date_list = self.values('post_date')  # 根据文章字段date_publish找出所有文章的发布时间
        for date in date_list:  # 对所有日期进行遍历，当然这里会有许多日期是重复的，目的就是找出多少种日期
            date = date['post_date'].strftime('%Y年%m月')  # 取出一个日期改格式为 ‘xxx年/xxx月 存档’
            if date not in distinct_date_list:
                distinct_date_list.append(date)
        return distinct_date_list


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_date = models.DateTimeField(auto_now_add=True)
    comment_status = models.CharField(choices=COMMENT_STATUS_CHOICES,
                                      default=('opened', 'opened'), max_length=20)
    content = RichTextUploadingField(config_name='default')
    tag = models.ManyToManyField('Tag', blank=True)
    category = models.ForeignKey(Category, related_name='category', null=True, on_delete=models.CASCADE)
    objects = PostManager()
    is_wordpress = models.CharField(choices=IS_WORDPRESS, default=('yes', 'yes'), max_length=10)
    price = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = '\u200B' + verbose_name
        ordering = ["-post_date"]

    def __str__(self):
        if self.title:
            return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.slug)])


class Comments(MPTTModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    comment_date = models.DateTimeField(auto_now=True)
    content = models.TextField(max_length=1000)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    approved = models.CharField(choices=COMMENT_APPROVED_CHOICES,
                                default=('refused', 'refused'), max_length=20)

    def __str__(self):
        if self.content:
            return self.content

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
        ordering = ["-comment_date"]
