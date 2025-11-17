from django.db import models
from django.contrib.auth.models import AbstractUser

#uploadtoにわたす用の関数、instanceがmodelのデータとしてくる
def gen_image_path_customuser(instance, filename):
    #拡張子を保持しつつ名前を変更
    ext = filename.split('.')[-1].lower()
    newname = f"user_icon.{ext}"
    return f"users/{instance.username}/{newname}"


class CustomUser(AbstractUser):
    deleted_at = models.DateTimeField(blank = True, null = True, verbose_name = "削除日時")
    nickname = models.CharField(blank = True, null  =True, max_length = 30, verbose_name = "ニックネーム")
    birthday = models.DateField(blank = True, null= True, verbose_name = "誕生日")
    user_icon = models.ImageField(null = True, blank= True, verbose_name = "アイコン", upload_to = gen_image_path_customuser)
    email = models.EmailField(unique = True,max_length=254, verbose_name = "メールアドレス")






