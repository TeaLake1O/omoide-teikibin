from django.contrib import admin

from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'user_icon',"email")  # iconを表示
    list_display_links = ('id', 'username')
admin.site.register(CustomUser, CustomUserAdmin)