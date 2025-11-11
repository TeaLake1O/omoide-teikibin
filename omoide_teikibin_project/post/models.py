from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid


CustomUser = settings.AUTH_USER_MODEL


class Group(models.Model):
    group_name = models.CharField(verbose_name="グループ名", max_length=200)
    creator = models.ForeignKey(CustomUser, on_delete = models.CASCADE, verbose_name="作成者")
    group_description = models.TextField(verbose_name="グループ説明", null = True, blank = True)
    created_at = models.DateTimeField(verbose_name="作成日時", auto_now_add = True)
    updated_at = models.DateTimeField(verbose_name="変更日時", auto_now = True)
    
    def __str__(self):
        return f"グループ名:{self.group_name}"


class Member(models.Model):
    member = models.ForeignKey(CustomUser, on_delete = models.CASCADE, verbose_name="ユーザー名")
    role = models.BooleanField(default = False, verbose_name="権限区分")
    date_joined = models.DateTimeField(auto_now_add = True, verbose_name="参加日時")
    left_at = models.DateTimeField(blank=True, null=True,verbose_name="退会日時")
    last_viewed_at = models.DateTimeField(default = timezone.now, verbose_name="最終閲覧日時")
    group = models.ForeignKey(Group, on_delete = models.CASCADE)
    
    class Meta:
        verbose_name = "メンバー"
        constraints = [
            #groupとusernameの組み合わせをuniqueにして、同一グループへの多重登録を禁止
            models.UniqueConstraint(
                fields=['group', 'member'],
                name='group_unique_pair',
            )
        ]
    
    def __str__(self):
        return f"{self.group.group_name}の所属ユーザ:{self.member.username}"


class Post(models.Model):
    #URLに使うのでUUIDField
    post_id = models.UUIDField(primary_key = True,default = uuid.uuid4, verbose_name="投稿ID")
    post_user = models.ForeignKey(CustomUser, on_delete = models.CASCADE, )
    post_content = models.TextField(verbose_name="投稿内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True,verbose_name="更新日時")
    deleted_at = models.DateTimeField(blank=True, null=True,verbose_name="削除日時")
    post_images = models.ImageField(null=True, blank=True,verbose_name="投稿画像")
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name="親投稿")
    group = models.ForeignKey(Group, on_delete = models.CASCADE)
    
    
    class Meta:
        verbose_name = "投稿"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"投稿者:{self.post_user.username}"