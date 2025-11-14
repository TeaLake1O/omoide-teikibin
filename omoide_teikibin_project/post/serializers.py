
from rest_framework import serializers
from accounts.serialyzer import *

from post.models import *

#ホームページを表示するシリアライザ
class HomePageReadSerializer(serializers.ModelSerializer):
    
    post_user = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Post
        fields = ["post_id","post_content", "post_images", "created_at", "post_user","group"]
    
    def get_post_user(self, obj):
        return UserInfSerializer(obj.post_user, context=self.context).data

#グループ一覧のシリアライザ、最後のメッセージも送る
class GroupListReadSerializer(serializers.ModelSerializer):
    
    last_post_nickname = serializers.CharField(read_only = True)
    last_post_username = serializers.CharField(read_only = True)
    last_post_content = serializers.CharField(read_only = True)
    
    class Meta:
        model = Group
        fields = ["id", "group_name", "group_image", "last_post_nickname", "last_post_username", "last_post_content"]

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


class MemberSerializer(serializers.ModelSerializer):
    member_info = UserInfSerializer(source='member', read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'group', 'member', 'member_info']        

