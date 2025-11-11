from rest_framework import serializers
from accounts.models import CustomUser
from .models import Friendship, Message
from django.db.models import Q

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


#フレンド一覧のシリアライザ、フレンドが成立しているときのみ
class FriendReadSerializer(serializers.ModelSerializer):
    peer = serializers.SerializerMethodField()
    
    class Meta:
        model = Friendship
        fields = ["friend_id", "status", "friend_date", "peer"]
    
    #自身が含まれたフレンドテーブルが作成された相手をpeerとする
    def get_peer(self, obj):
        me = self.context["request"].user
        other = obj.user_b if obj.user_a_id == me.id else obj.user_a
        return MiniUserInfSerializer(other, context=self.context).data
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
        other = obj.user_b if obj.user_a_id == me.id else obj.user_a
        return MiniUserInfSerializer(other, context=self.context).data
    
    #送り手が自信かどうかのフラグ
    def get_is_request_user_sent(self, obj):
        me = self.context["request"].user
        if obj.status == Friendship.Status.A2B:
            return obj.user_a_id == me.id
        else:
            return obj.user_b_id == me.id
#フレンド申請、もしくはフレンド承認のpost用シリアライザ
class FriendWriteSerializer(serializers.ModelSerializer):
    
    other_id = serializers.IntegerField(write_only = True)
    #is_positiveはフレンド依頼、フレンド承認のような操作かそうでないかを区別するために使う
    is_positive = serializers.BooleanField(write_only = True)
    
    class Meta:
        model = Friendship
        fields = ["other_id", "is_positive"]
    
    def create(self, validated_data):
        me = self.context["request"].user
        
        other = CustomUser.objects.get(id = validated_data["other_id"])
        
        is_positive = validated_data["is_positive"]

        friendship = Friendship.objects.filter(
            Q(user_a = me, user_b = other) |
            Q(user_a = other, user_b = me)
        ).first()
        #FriendShipに関係がすでにあった場合
        if friendship:
            if is_positive:
                friendship.status = Friendship.Status.ACPT
                friendship.save(update_fields = ["status"])
                return friendship
            else:
                friendship.delete()
                return friendship
        
        #まだ関係がつくられていないならデータを作ってreturn
        friendship = Friendship.objects.create(
            user_a = me,
            user_b = other,
            status = "A2B"
        )
        return friendship


#DM一覧のシリアライザ
class DMListReadSerializer(serializers.ModelSerializer):
    
    message_id = serializers.IntegerField(source="pk", read_only = True)
    other = serializers.SerializerMethodField(read_only = True)
    last_message = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = Message
        fields = ["message_id", "other", "last_message"]
    
    #自身が含まれたフレンドテーブルが作成された相手をpeerとする
    def get_other(self, obj):
        me = self.context["request"].user
        f = obj.friendship
        other = f.user_a if f.user_b_id == me.id else f.user_b
        return MiniUserInfSerializer(other, context=self.context).data
    
    #最後のメッセージを取得
    def get_last_message(self, obj):
        me = self.context["request"].user
        f = obj.friendship
        
        msg = (
            Message.objects
            .filter(friendship = f)
            .order_by("-send_at")
            .first()
        )
        print(msg)
        if not msg or (msg.message_text is None and msg.message_image is None) : return None
        
        return {
            "message" : msg.message_text,
            "send_at" : msg.send_at
        }
#DM表示のシリアライザ
class DMReadSerializer(serializers.ModelSerializer):
    sender_inf = serializers.SerializerMethodField(read_only = True)
    
    class Meta:
        model = Message
        fields = ["id", "message_image", "message_text", "send_at", "sender_inf"]
    
    #自身が含まれたフレンドテーブルが作成された相手をpeerとする
    def get_sender_inf(self, obj):
        return MiniUserInfSerializer(obj.sender, context=self.context).data
#DM送信用のシリアライザ
class DMWriteSerializer(serializers.ModelSerializer):
    message_text = serializers.CharField(write_only = True)
    message_image = serializers.ImageField(write_only = True)
    
    class Meta:
        model = Message
        fields = ["message_text", "message_image"]

    def create(self, validated_data):
        me = self.context["request"].user
        
        m = Message.objects.create(
            sender = me,
            message_text = validated_data["message_text"],
            message_image = validated_data["message_image"],
        )
        return m
