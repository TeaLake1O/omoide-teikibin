
from rest_framework import serializers
from post.models import *
from accounts.models import CustomUser
from friend.models import Friendship

from django.db.models import Q

#user情報の汎用シリアライザ
class UserInfSerializer(serializers.ModelSerializer):
    
    icon_url = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ["id", "username", "icon_url","nickname", "status"]
    
    #絶対URL取得用
    def get_icon_url(self, obj):
        
        f = getattr(obj, "user_icon", None)
        if not f:
            return None
        req = self.context.get("request")
        return req.build_absolute_uri(f.url) if req else f.url
    
    def get_status(self, obj):
        
        me = self.context["request"].user
        
        fs = (
            Friendship.objects
            .filter((Q(user_a = me) & Q(user_b = obj)) | (Q(user_a = obj)|Q(user_b = me)))
            .filter(deleted_at__isnull = True)
            .first()
        )
        
        if not fs:
            return None
        else:
            return fs.status
        



class HomePageReadSerializer(serializers.ModelSerializer):
    
    post_user = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Post
        fields = ["post_id","post_content", "post_images", "created_at", "post_user"]
    
    def get_post_user(self, obj):
        return UserInfSerializer(obj.post_user, context=self.context).data

class PostSerializer(serializers.ModelSerializer):
    post_user__username = serializers.ReadOnlyField(source='post_user.username')

    class Meta:
        model = Post
        fields = (
            'post_id',
            'post_user', 
            'post_user__username', 
            'post_content', 
            'created_at', 
            'updated_at'
        )
        read_only_fields = ('post_id', 'post_user', 'created_at', 'updated_at')