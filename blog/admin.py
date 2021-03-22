from django.contrib import admin
from .models import Post
from .models import Tag
from .models import Category
from .models import Comments


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'post_date', 'comment_status']
    search_fields = ['title', 'slug']
    filter_horizontal = ('tag',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name']


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['post', 'approved', 'user_name', 'email', 'content', 'comment_date']
    list_filter = ('approved',)
