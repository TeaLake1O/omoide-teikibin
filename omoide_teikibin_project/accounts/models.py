from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    deleted_at = models.DateTimeField(default = None, blank = True, null = True, verbose_name = "削除日時")
    nickname = models.CharField(blank = True, null  =True, max_length = 30, verbose_name = "ニックネーム")
    birthday = models.DateField(blank = True, null= True, verbose_name = "誕生日")
    user_icon = models.ImageField(default = None, null = True, blank= True, verbose_name = "アイコン")
    email = models.EmailField(unique = True,max_length=254, verbose_name = "メールアドレス")
    

"""
class FriendShip(models.Model):
    friend_id = models.AutoField(primary_key=True,verbose_name="フレンド")
    username_a = models.ForeignKey(max_length=150,unique=True,verbose_name="ユーザーA")
    username_b = models.ForeignKey(max_length=150,unique=True,verbose_name="ユーザーB")
    user_a_request = models.BooleanField(default=False,verbose_name="ユーザA申請")
    user_b_request = models.BooleanField(default=False,verbose_name="ユーザB申請")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="作成日時")"""
