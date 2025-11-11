# models.py - Đề xuất sửa đổi
from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
CustomUser = settings.AUTH_USER_MODEL


class Member(models.Model):
    username = models.ForeignKey(
        CustomUser,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name="ユーザー名")
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name="グループ")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="参加日時")
    left_at = models.DateTimeField(blank=True, null=True, verbose_name="退会日時")
    role = models.BooleanField(default=False, verbose_name="役割")
    last_viewed_at = models.DateTimeField(blank=True, null=True, verbose_name="最終閲覧日時")
    
    class Meta:
        unique_together = ('username', 'group')
        verbose_name = "メンバー"
    
    def __str__(self):
        user_display = self.username.username if self.username else "No User"
        return f"{user_display} in {self.group.group_name}"
    
    
class Group(models.Model):
    group_id = models.AutoField(primary_key=True, verbose_name="グループID")
    group_name = models.CharField(max_length=100, unique=True, verbose_name="グループ名")
    group_description = models.TextField(blank=True, null=True, verbose_name="グループ説明")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="作成日時")
    update_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    creator_user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='created_groups', 
        verbose_name="作成者ユーザーID"
    )
    class Meta:
        verbose_name = "グループ"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"グループID:{self.group_id} - グループ名:{self.group_name} " 
    
    
class Post(models.Model):
    post_id = models.UUIDField(primary_key = True, default = uuid.uuid4, verbose_name="投稿ID")
    post_user = models.ForeignKey(
        CustomUser,
        on_delete = models.CASCADE, 
        related_name='posts',
        verbose_name="ユーザーID"
    )
    post_content = models.TextField(verbose_name="投稿内容")
    parent_post = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='replies', 
        verbose_name="親投稿"
    )
    group = models.ForeignKey(Group, on_delete = models.CASCADE, related_name='group_posts')
    post_images = models.ImageField(upload_to='post_images/', blank=True, null=True, verbose_name="投稿画像")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="削除日時")
    class Meta:
        verbose_name = "投稿"
        ordering = ["-created_at"] # Đảm bảo tên trường là 'created_at'
    
    def __str__(self):
        return f"投稿ID:{self.post_id} - 投稿者:{self.post_user.username}" 

