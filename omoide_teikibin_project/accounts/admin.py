from django.contrib import admin

from .models import CustomUser, NewEmail

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'user_icon',"email")
    list_display_links = ('id', 'username')


class NewEmailAdmin(admin.ModelAdmin):
    list_display = ('user', 'new_email', 'token')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(NewEmail, NewEmailAdmin)
