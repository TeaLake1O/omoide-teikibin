from django.contrib import admin
from .models import Group, Member, Post, BlogPost, Notification

admin.site.register(Post)
admin.site.register(Member)
admin.site.register(Group)
admin.site.register(BlogPost)
admin.site.register(Notification)
