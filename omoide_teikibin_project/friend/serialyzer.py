from rest_framework import serializers

from accounts.models import CustomUser
from common.serialyzer import *
from .models import Friendship, Message

from django.db.models import Q
from django.utils import timezone



#フレンド一覧のシリアライザ、フレンドが成立しているときのみ
class FriendReadSerializer(FriendListSerializer):
    class Meta(FriendListSerializer.Meta):
        pass

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
        
        #friendShipに関係がすでにあった場合
        if friendship:
            #ポジティブがTrueの場合、friendShipの有無をすでに判定しているため、承認をさす(ソフトデリートは除く)
            if is_positive:
                #friendテーブルがソフトデリートサれていた場合、statusを変えてソフトデリートを解除
                if friendship.deleted_at is not None:
                    friendship.status = Friendship.Status.A2B if friendship.user_a_id == me.id else Friendship.Status.B2A
                    friendship.deleted_at = None
                    friendship.save(update_fields = ["status", "deleted_at"])
                    return friendship
                #自身が承認を行える場合、承認する
                elif (friendship.status == Friendship.Status.A2B and friendship.user_b_id == me.id) or (friendship.status == Friendship.Status.B2A and friendship.user_a_id == me.id):
                    friendship.status = Friendship.Status.ACPT
                    friendship.save(update_fields = ["status"])
                    return friendship
                #すでにフレンドの場合
                elif friendship.status == Friendship.Status.ACPT:
                    raise serializers.ValidationError("既にフレンドです")
                #自身が承認を行えない場合
                else:
                    raise serializers.ValidationError("承認は相手ユーザのみ行えます")
            #is_positiveがfalse、つまりフレンド関係の解消や申請の拒否の場合、ソフトデリートする
            else:
                friendship.deleted_at = timezone.now()
                friendship.save(update_fields = ["deleted_at"])
                return friendship
        
        #まだ関係がつくられていないならデータを作ってreturn
        friendship = Friendship.objects.create(
            user_a = me,
            user_b = other,
            status = "A2B"
        )
        return friendship

#ユーザを検索するシリアライザ、postのUseInfSerializerを継承する
class FriendSearchSerializer(UserInfSerializer):
    class Meta(UserInfSerializer.Meta):
        pass

#DM一覧のシリアライザ
class DMListReadSerializer(serializers.ModelSerializer):
    
    message_id = serializers.IntegerField(source="pk", read_only = True)
    other = serializers.SerializerMethodField(read_only = True)
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    sender_nickname = serializers.CharField(source="sender.nickname", read_only=True)
    
    class Meta:
        model = Message
        fields = ["message_id", "other", "message_text", "send_at", "sender_id", "sender_username", "sender_nickname"]
    
    #自身が含まれたフレンドテーブルが作成された相手をpeerとする
    def get_other(self, obj):
        me = self.context["request"].user
        f = obj.friendship
        other = f.user_a if f.user_b_id == me.id else f.user_b
        return MiniUserInfSerializer(other, context=self.context).data

#DM表示のシリアライザ
class DMReadSerializer(serializers.ModelSerializer):
    sender_inf = serializers.SerializerMethodField(read_only = True)
    friendship_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Message
        fields = ["id", "message_image", "message_text", "send_at", "sender_inf", "friendship_id"]
    
    #自身が含まれたフレンドテーブルが作成された相手をpeerとする
    def get_sender_inf(self, obj):
        return MiniUserInfSerializer(obj.sender, context=self.context).data

#DM送信用のシリアライザ
class DMWriteSerializer(serializers.ModelSerializer):
    
    friendship_id = serializers.PrimaryKeyRelatedField(source = "friendship", queryset = Friendship.objects.all() , write_only = True)
    message_text = serializers.CharField(required = True, allow_blank = True, write_only = True)
    message_image = serializers.ImageField(required = True, allow_null = True, write_only = True)
    
    class Meta:
        model = Message
        fields = ["friendship_id", "message_text", "message_image"]
    #バリデーション
    def validate(self, attrs):
        me = self.context["request"].user
        fs = attrs.get("friendship")
        image = attrs.get("message_image")
        text = attrs.get("message_text")
        
        #フレンドシップに自身が入っていなかったら
        if me.id not in (fs.user_a_id, fs.user_b_id):
            raise serializers.ValidationError("このメッセージを送信する権限がありません")
        
        #フレンド関係が成立していなかったら
        if fs.status != Friendship.Status.ACPT or fs.deleted_at is not None:
            raise serializers.ValidationError("このメッセージを送信する権限がありません")
        
        #もしimageとtextの両方が空だったら
        if image is None and (text.strip() == "" or text is None):
            raise serializers.ValidationError("テキストか画像のどちらかのデータが必要です")
        elif text is not None and  text.strip() == "":
            attrs["message_text"] = None
        
        return attrs

    def create(self, validated_data):
        me = self.context["request"].user
        
        m = Message.objects.create(
            sender = me,
            **validated_data
        )
        return m
