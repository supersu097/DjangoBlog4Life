"""DjangoBlog4Life URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from .secret_keys import ADMIN_URL_SECRET
from blog.models import Post

article_dict = {
    'queryset': Post.objects.all(),
}

urlpatterns = [path('admin_{}/'.format(ADMIN_URL_SECRET), admin.site.urls),
               # index page and it's paginator
               path('', views.IndexPaginator.as_view()),
               path('page/<int:page_num>/', views.IndexPaginator.as_view()),
               # search page and it's paginator
               path('search/', views.FullTextSearch.as_view()),
               path('search/page/<int:page_num>/', views.FullTextSearch.as_view()),
               # article page
               path('<slug:slug>/', views.article_detail, name='article_detail'),
               # comment reply
               path('<slug:slug>/reply/', views.article_detail),
               # order notify
               path('<slug:slug>/notify/', views.order_notify),
               # comments' paginator
               path('<slug:slug>/comment/page/<int:comment_page_num>/', views.article_detail),
               # category page and it's paginator
               path('category/<str:slug>/', views.CategoryPaginator.as_view()),
               path('category/<str:slug>/page/<str:page_num>/', views.CategoryPaginator.as_view()),
               # tag page and it's paginator
               path('tag/<str:slug>/', views.TagPaginator.as_view()),
               path('tag/<str:slug>/page/<str:page_num>/', views.TagPaginator.as_view()),
               # archive page and it's paginator
               path('archive/<int:year>/<int:month>/', views.ArchivePaginator.as_view()),
               path('archive/<int:year>/<int:month>/page/<int:page_num>/', views.ArchivePaginator.as_view()),
               #
               path('ckeditor/', include('ckeditor_uploader.urls')),
               path('captcha/', include('captcha.urls')),
               path('sitemap.xml', sitemap,
                    {'sitemaps': {'blog': GenericSitemap(article_dict, priority=0.6)}})
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
