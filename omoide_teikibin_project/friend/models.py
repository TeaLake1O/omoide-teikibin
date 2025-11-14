from django.db import models

from accounts.models import CustomUser
from django.db.models import Q,F
import uuid
from django.utils import timezone

#uploadtoにわたす用の関数、instanceがmodelのデータとしてくる
def gen_image_path_message(instance, filename):
    #拡張子を保持しつつ名前を変更
    ext = filename.split('.')[-1].lower()
    newname = f"{uuid.uuid4().hex}.{ext}"
    return f"users/{instance.friendship}/{instance.friendship_id}/{timezone.now():%Y/%m/%d}/{newname}"



class Friendship(models.Model):
    
    class Status(models.TextChoices):
        A2B = "A2B", "A→B申請"
        B2A = "B2A", "B→A申請"
        ACPT = "ACPT", "承認"
    
    friend_id = models.AutoField(primary_key=True,verbose_name="フレンド")
    user_a = models.ForeignKey(CustomUser,verbose_name="ユーザーA", related_name = "friendship_as_a", on_delete = models.CASCADE)
    user_b = models.ForeignKey(CustomUser,verbose_name="ユーザーB", related_name = "friendship_as_b", on_delete = models.CASCADE)
    
    status = models.CharField(max_length = 4, choices = Status.choices, default = Status.A2B)
    
    created_at = models.DateTimeField(auto_now_add = True, verbose_name="作成日時")
    friend_date = models.DateTimeField(null = True, blank = True, verbose_name = "フレンド成立日")
    
    deleted_at = models.DateTimeField(null = True, blank = True, verbose_name = "フレンド解消日")
    
    #Metaはdbの制約を決定する
    class Meta:
        verbose_name = "フレンド"
        #constraintsリストに複数の制約をいれる
        constraints = [
            #登録時のチェック
            #Qでとってきたusername_aとF(同一行)のusername_Bを比較して、同じにならないようにチェックする
            models.CheckConstraint(
                check = ~Q(user_a = F('user_b')),
                name="friend_a_noteq_b",
            ),
            models.CheckConstraint(
                #__ltでless thanになる（より小さい）
                check = Q(user_a__lt = F('user_b')),
                name = "combinations_already_exist",
            ),
            models.UniqueConstraint(
                fields=['user_a', 'user_b'],
                name="friend_unique",
            )
        ]
    def __str__(self):
        return f"{self.user_a}と{self.user_b}のフレンド関係"

class Message(models.Model):
    friendship = models.ForeignKey(Friendship ,verbose_name = "フレンド", on_delete= models.CASCADE)
    message_image = models.ImageField(verbose_name = "メッセージ画像",null = True, blank = True, upload_to = gen_image_path_message)
    message_text = models.TextField(verbose_name = "メッセージ内容", null = True, blank = True)
    deleted_at = models.DateTimeField(verbose_name = "削除日時", null = True, blank = True)
    send_at = models.DateTimeField(verbose_name = "送信日時", auto_now_add = True)
    sender = models.ForeignKey(CustomUser, verbose_name="送信者", on_delete= models.CASCADE)
    
    class Meta:
        verbose_name = "メッセージ"
        constraints = [
            models.CheckConstraint(
                check = Q(sender = F('friendship__user_a')) | Q(sender = F('friendship__user_b')),
                name="friendship_has_sender",
            ),
        ]
    def __str__(self):
        return f"{self.friendship.user_a}(送信者A)と{self.friendship.user_b}(送信者B)のメッセージ"