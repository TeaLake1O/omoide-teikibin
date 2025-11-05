from django.db import models

from accounts.models import CustomUser
from django.db.models.functions import Least, Greatest
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
    
    created_at = models.DateTimeField(auto_now_add = True,verbose_name="作成日時")
    friend_date = models.DateTimeField(null = True,verbose_name = "フレンド成立日")
    
    #Metaはdbの制約を決定する
    class Meta:
        #constraintsリストに複数の制約をいれる
        constraints = [
            #UniqueConstraintはユニーク制約やインデックスを決める
            #今回は、LeastとGreatestにusernameをいれることで大きい方と小さい方としてわけて正規化できる
            models.UniqueConstraint(
                expressions=[
                    Least('username_a', 'username_b'),
                    Greatest('username_a', 'username_b'),
                ],
                name='friend_unique',
            ),
            #登録時のチェック
            
            models.CheckConstraint(
                check = ~Q(username_a = F('username_b')),
                name='friend_a_noteq_b',
            ),
        ]

class Message(models.Model):
    message_id = models.AutoField(primary_key = True)
    message_image = models.ImageField()
    message_text = models.TextField()
    deleted_at = models.DateTimeField()
    send_at = models.DateTimeField()
    sender_id = models.ForeignKey(CustomUser)
