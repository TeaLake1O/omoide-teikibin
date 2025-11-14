from rest_framework import serializers
from accounts.models import CustomUser
from friend.models import Friendship as FS
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
        if obj == me :
            return "me"
        
        fs = (
            FS.objects
            .filter((Q(user_a = me) & Q(user_b = obj)) | (Q(user_a = obj)|Q(user_b = me)))
            .filter(deleted_at__isnull = True)
            .first()
        )
        
        if not fs:
            return None
        else:
            match fs.status:
                case FS.Status.A2B:
                    return "outgoing" if fs.user_a == me else "incoming"
                case FS.Status.B2A:
                    return "outgoing" if fs.user_b == me else "incoming"
                case FS.Status.ACPT:
                    return "friend"

#user情報の汎用シリアライザ
class MiniUserInfSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ["id", "username", "icon_url","nickname" ]
    
    #絶対URL取得用
    def get_icon_url(self, obj):
        
        f = getattr(obj, "user_icon", None)
        if not f:
            return None
        req = self.context.get("request")
        return req.build_absolute_uri(f.url) if req else f.url
#user情報の汎用シリアライザ、こっちはnicknameとusernameだけ
class MiniUserInfNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "nickname" ]

