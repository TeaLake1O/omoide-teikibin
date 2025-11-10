from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
CustomUser = settings.AUTH_USER_MODEL

class BlogPost(models.Model):
    blog_post_id = models.AutoField(primary_key=True, verbose_name="ブログ投稿ID")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blog_posts', verbose_name="著者")
    title = models.CharField(max_length=200, verbose_name="タイトル")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        verbose_name = "ブログ投稿"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.title

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True, verbose_name="通知ID")
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', verbose_name="受取人")
    message = models.CharField(max_length=255, verbose_name="メッセージ")
    is_read = models.BooleanField(default=False, verbose_name="既読")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="作成日時")
    
    class Meta:
        verbose_name = "通知"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.message

class Member(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships', verbose_name="ユーザー名")
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='members', verbose_name="グループ")
    joined_at = models.DateTimeField(default=timezone.now, verbose_name="参加日時")
    left_at = models.DateTimeField(blank=True, null=True, verbose_name="退会日時")
    role = models.BooleanField(default=False, verbose_name="役割")
    
    class Meta:
        unique_together = ('username', 'group')
        verbose_name = "メンバー"
    
    def __str__(self):
        return f"{self.user.username} in {self.group.group_name}"
class Group(models.Model):
    group_id = models.AutoField(primary_key=True, verbose_name="グループID")
    group_name = models.CharField(max_length=100, unique=True, verbose_name="グループ名")
    group_description = models.TextField(blank=True, null=True, verbose_name="グループ説明")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="作成日時")
    
    class Meta:
        verbose_name = "グループ"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.group_name
    
    
class Post(models.Model):
    post_id = models.UUIDField(primary_key = True, default = uuid.uuid4, verbose_name="投稿ID")
    post_user = models.ForeignKey(
        CustomUser, 
        on_delete = models.CASCADE, 
        related_name='posts', 
        verbose_name="投稿ユーザー"
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
    
    class Meta:
        verbose_name = "投稿"
        ordering = ["-created_at"]
    
    def __str__(self):

        return f"投稿ID:{self.post_id} - 投稿者:{self.post_user.username}" 

