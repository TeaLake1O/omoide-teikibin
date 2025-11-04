from django.db import models

from accounts.models import CustomUser

class Friendship(models.Model):
    class Status(models.TextChoices):
        PENDING_A2B = "A2B", "A→B申請"
        PENDING_B2A = "B2A", "B→A申請"
        ACCEPTED = "ACPT", "承認"
    
    
    friend_id = models.AutoField(primary_key=True,verbose_name="フレンド")
    username_a = models.ForeignKey(CustomUser,verbose_name="ユーザーA", related_name = "friendship_as_a", on_delete = models.CASCADE)
    username_b = models.ForeignKey(CustomUser,verbose_name="ユーザーB", related_name = "friendship_as_b", on_delete = models.CASCADE)
    
    status = models.CharField(max_length = 4, )
    
    """
    user_a_request = models.BooleanField(default = False,verbose_name="ユーザA申請")
    user_b_request = models.BooleanField(default = False,verbose_name="ユーザB申請")
    """
    
    created_at = models.DateTimeField(auto_now_add = True,verbose_name="作成日時")
    friend_date = models.DateTimeField(auto_now = True, verbose_name = "フレンド成立日")

class Message(models.Model):
    message_id = models.AutoField(primary_key = True)
    message_image = models.ImageField()
    message_text = models.TextField()
    deleted_at = models.DateTimeField()
    send_at = models.DateTimeField()
    sender_id = models.ForeignKey(CustomUser)
