from rest_framework import serializers
from .models import Notification
from post.models import Post

from common.serializer import MiniUserInfSerializer

class PostMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["post_id", "post_content", "post_images","group"]

class NotifyReadSerializer(serializers.ModelSerializer):
    
    actor = MiniUserInfSerializer(read_only = True)
    class Meta:
        model = Notification
        fields = ["notify_id","status","actor","message","is_read","created_at"]

class PostNotifyReadSerializer(NotifyReadSerializer):
    
    post_detail = PostMiniSerializer(source = "post",read_only = True)
    
    
    class Meta(NotifyReadSerializer.Meta):
        model = Notification
        fields = ["notify_id","status","actor","message","is_read","created_at","post_detail"]

