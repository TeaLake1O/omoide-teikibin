from rest_framework import serializers
from accounts.models import CustomUser
from .models import Friendship
from django.db.models import Q

#user情報のシリアライザ、後でaccountsに移す
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

#フレンド一覧のシリアライザ、フレンドが成立しているときのみ
class FriendReadSerializer(serializers.ModelSerializer):
    peer = serializers.SerializerMethodField()
    
    class Meta:
        model = Friendship
        fields = ["friend_id", "status", "friend_date", "peer"]
    
    #自身が含まれたフレンドテーブルが作成された相手をpeerとする
    def get_peer(self, obj):
        me = self.context["request"].user
        other = obj.username_b if obj.username_a_id == me.id else obj.username_a
        return UserInfSerializer(other, context=self.context).data

#フレンド申請のシリアライザ、is_request_user_sentを使い申請したユーザを判断する
class FriendRequestSerializer(serializers.ModelSerializer):
    peer = serializers.SerializerMethodField()
    is_request_user_sent = serializers.SerializerMethodField()
    
    class Meta:
        model = Friendship
        fields = ["friend_id", "status", "peer", "is_request_user_sent"]
    
    #自身が含まれたフレンドテーブルが作成された相手をpeerとする
    def get_peer(self, obj):
        me = self.context["request"].user
        other = obj.username_b if obj.username_a_id == me.id else obj.username_a
        return UserInfSerializer(other, context=self.context).data
    
    #送り手が自信かどうかのフラグ
    def get_is_request_user_sent(self, obj):
        me = self.context["request"].user
        if obj.status == Friendship.Status.A2B:
            return obj.username_a_id == me.id
        else:
            return obj.username_b_id == me.id

#フレンド申請、もしくはフレンド承認のpost用シリアライザ
class FriendWriteSerializer(serializers.ModelSerializer):
    
    other_id = serializers.IntegerField()
    #is_positiveはフレンド依頼、フレンド承認のような操作かそうでないかを区別するために使う
    is_positive = serializers.BooleanField()
    
    class Meta:
        model = Friendship
        fields = ["other_id", "is_positive"]
    
    def create(self, validated_data):
        me = self.context["request"].user
        
        other = CustomUser.objects.get(id = validated_data["other_id"])
        
        is_positive = validated_data["is_positive"]

        friendship = Friendship.objects.filter(
            Q(username_a = me, username_b = other) |
            Q(username_a = other, username_b = me)
        ).first()
        #FriendShipに関係がすでにあった場合
        if friendship:
            if is_positive:
                friendship.Status.ACPT
                friendship.save(update_fields = ["status"])
                return friendship
            else:
                friendship.delete()
                return friendship
        
        #まだ関係がつくられていないならデータを作ってreturn
        friendship = Friendship.objects.create(
            username_a = me,
            username_b = other,
            status = "A2B"
        )
        return friendship