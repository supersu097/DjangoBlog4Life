from django.contrib import admin
from .models import FriendLink
from .models import Options, Site


# Register your models here.


@admin.register(FriendLink)
class FriendLinkAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_url']


@admin.register(Options)
class OptionsAdmin(admin.ModelAdmin):
    list_display = ['option_flag', 'option_name', 'option_value']
    readonly_fields = ('option_flag', )


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['option_flag', 'option_name', 'option_value']
    readonly_fields = ('option_flag',)
