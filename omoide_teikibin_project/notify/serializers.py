from rest_framework import serializers
from .models import Notification
from post.models import Post

class PostMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["post_id", "post_content", "post_images"]

class PostNotifyReadSerializer(serializers.ModelSerializer):
    
    post_detail = PostMiniSerializer(source = "post",read_only = True)
    
    
    class Meta:
        model = Notification
        fields = ["notify_id","status","actor","message","is_read","created_at","post_detail"]

