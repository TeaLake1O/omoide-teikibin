from django.db import models
from django.utils import timezone
 
class Group(models.Model):
    group_id = models.CharField(
        max_length=100,verbose_name="グループID")
    group_name = models.CharField(
        max_length=200,verbose_name="グループ名")
    group_description = models.TextField(blank=True,
        verbose_name="グループ説明")
    created_at = models.DateTimeField(
        auto_now_add=True,verbose_name="作成日時")
    creator = models.CharField(
        max_length=100,verbose_name="作成者")
 
class Member(models.Model):
    username = models.CharField(max_length=100,verbose_name="ユーザー名")
    role = models.CharField(max_length=50,verbose_name="役割")
    date_joined = models.DateTimeField(default=timezone.now,verbose_name="参加日時")
    left_at = models.DateTimeField(default=None, blank=True, null=True,verbose_name="退会日時")
    lastviewed_at = models.DateTimeField(default=timezone.now,verbose_name="最終閲覧日時")
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
   
 
class Post(models.Model):
    title = models.CharField(max_length=200,verbose_name="タイトル")
    post_content = models.TextField(verbose_name="投稿内容")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True,verbose_name="更新日時")
    deleted_at = models.DateTimeField(default=None, blank=True, null=True,verbose_name="削除日時")
    post_images = models.ImageField(default=None, null=True, blank=True,verbose_name="投稿画像")
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,verbose_name="親投稿")
    post_id = models.CharField(max_length=100,verbose_name="投稿ID")
    author = models.CharField(max_length=100,verbose_name="投稿者")
    