from django.db import models


class FriendLink(models.Model):
    site_name = models.CharField(max_length=100)
    site_url = models.CharField(max_length=200)

    def __str__(self):
        if self.site_name:
            return self.site_name

    class Meta:
        verbose_name = "友情链接"
        verbose_name_plural = verbose_name


class Options(models.Model):
    option_name = models.CharField(max_length=50)
    option_value = models.TextField(max_length=20000, null=True, blank=True)
    option_flag = models.CharField(max_length=100)

    def __str__(self):
        if self.option_name:
            return self.option_name

    class Meta:
        verbose_name = "杂项设置"
        verbose_name_plural = verbose_name


class Site(models.Model):
    option_flag = models.CharField(max_length=50)
    option_name = models.CharField(max_length=50)
    option_value = models.TextField(max_length=2000, null=True, blank=True)

    def __str__(self):
        if self.option_name:
            return self.option_name

    class Meta:
        verbose_name = "站点设置"
        verbose_name_plural = '\u200B' + verbose_name
