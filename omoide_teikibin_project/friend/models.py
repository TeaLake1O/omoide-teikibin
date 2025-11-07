from django.db import models

from accounts.models import CustomUser
from django.db.models import Q,F

class Friendship(models.Model):
    
    class Status(models.TextChoices):
        PENDING_A2B = "A2B", "A→B申請"
        PENDING_B2A = "B2A", "B→A申請"
        ACCEPTED = "ACPT", "承認"
    
    friend_id = models.AutoField(primary_key=True,verbose_name="フレンド")
    username_a = models.ForeignKey(CustomUser,verbose_name="ユーザーA", related_name = "friendship_as_a", on_delete = models.CASCADE)
    username_b = models.ForeignKey(CustomUser,verbose_name="ユーザーB", related_name = "friendship_as_b", on_delete = models.CASCADE)
    
    status = models.CharField(max_length = 4, choices = Status.choices, default = Status.PENDING_A2B)
    
    created_at = models.DateTimeField(auto_now_add = True, verbose_name="作成日時")
    friend_date = models.DateTimeField(null = True, blank = True, verbose_name = "フレンド成立日")
    
    #Metaはdbの制約を決定する
    class Meta:
        verbose_name = "フレンド"
        #constraintsリストに複数の制約をいれる
        constraints = [
            #登録時のチェック
            #Qでとってきたusername_aとF(同一行)のusername_Bを比較して、同じにならないようにチェックする
            models.CheckConstraint(
                check = ~Q(username_a = F('username_b')),
                name="friend_a_noteq_b",
            ),
            models.CheckConstraint(
                #__ltでless thanになる（より小さい）
                check = Q(username_a__lt = F('username_b')),
                name = "combinations_already_exist",
            ),
            models.UniqueConstraint(
                fields=['username_a', 'username_b'],
                name="friend_unique",
            )
        ]
    def __str__(self):
        return f"{self.username_a}と{self.username_b}のフレンド関係"

class Message(models.Model):
    friendship = models.ForeignKey(Friendship ,verbose_name = "フレンド", on_delete= models.CASCADE)
    message_image = models.ImageField(verbose_name = "メッセージ画像",null = True, blank = True)
    message_text = models.TextField(verbose_name = "メッセージ内容", null = True, blank = True)
    deleted_at = models.DateTimeField(verbose_name = "削除日時", null = True, blank = True)
    send_at = models.DateTimeField(verbose_name = "送信日時", auto_now_add = True)
    sender_a = models.BooleanField(verbose_name="送信者がAか", default=True)
    
    class Meta:
        verbose_name = "メッセージ"
    def __str__(self):
        return f"{self.friendship.username_a}(送信者A)と{self.friendship.username_b}(送信者B)のメッセージ"

