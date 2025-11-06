from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    deleted_at = models.DateTimeField(blank = True, null = True, verbose_name = "削除日時")
    nickname = models.CharField(blank = True, null  =True, max_length = 30, verbose_name = "ニックネーム")
    birthday = models.DateField(blank = True, null= True, verbose_name = "誕生日")
    user_icon = models.ImageField(null = True, blank= True, verbose_name = "アイコン")
    email = models.EmailField(unique = True,max_length=254, verbose_name = "メールアドレス")




