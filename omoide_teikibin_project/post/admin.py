from django.contrib import admin
from .models import Group, Member, Post

admin.site.register(Post)
admin.site.register(Member)
admin.site.register(Group)
