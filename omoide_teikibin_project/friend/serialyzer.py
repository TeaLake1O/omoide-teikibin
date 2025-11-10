from rest_framework import serializers
from accounts.models import CustomUser
from .models import Friendship

class UserInfSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ["id", "username", "icon_url","nickname", "birthday" ]
    
    #絶対URL取得用
    def get_icon_url(self, obj):
        
        f = getattr(obj, "user_icon", None)
        if not f:
            return None
        req = self.context.get("request")
        return req.build_absolute_uri(f.url) if req else f.url

class UserFriendSerializer(serializers.ModelSerializer):
    #readonly、読み取りの時しか出力しない
    username_a = UserInfSerializer(read_only=True)
    username_b = UserInfSerializer(read_only=True)
    
    #writeonly、入力でのみ受け付ける
    username_a_id = serializers.PrimaryKeyRelatedField(
        source="username_a", queryset = CustomUser.objects.all(), write_only=True)
    username_b_id = serializers.PrimaryKeyRelatedField(
        source="username_b", queryset = CustomUser.objects.all(), write_only=True)
    
    class Meta:
        model = Friendship
        fields = ["friend_id", "username_a", "username_b", "status", "username_a_id","username_b_id" ]