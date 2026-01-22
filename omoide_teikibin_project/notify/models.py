import uuid
from django.db import models
from django.conf import settings
from accounts.models import CustomUser
from post.models import Group,Post
from django.db import models
from typing import Literal,Optional

NotifyStatus = Literal["post","friend","message","else"]

#uploadtoにわたす用の関数、instanceがmodelのデータとしてくる
def gen_image_path_message(instance, filename):
    #拡張子を保持しつつ名前を変更
    ext = filename.split('.')[-1].lower()
    newname = f"{uuid.uuid4().hex}.{ext}"
    return f"notify/{instance.notify_id}/{newname}"

class Notification(models.Model):
    class Status(models.TextChoices):
        POST = "post", "post"
        FRIEND = "friend", "friend"
        MESSAGE = "message", "message"
        ELSE = "else", "else"
    
    notify_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser,verbose_name="ユーザ", related_name = "notify_user", on_delete = models.CASCADE)
    actor = models.ForeignKey(CustomUser,verbose_name="送信者", related_name = "notify_actor", on_delete = models.CASCADE)
    message = models.CharField(verbose_name = "メッセージ内容",max_length=100)
    is_read = models.BooleanField(verbose_name="既読",default=False)
    created_at = models.DateTimeField(auto_now_add = True,verbose_name="通知日時")
    status = models.CharField(verbose_name="通知状態",
        max_length=10,
        choices=Status.choices,
        default=Status.ELSE,
        db_index=True,)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)

