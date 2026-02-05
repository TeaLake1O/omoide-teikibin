
from rest_framework import serializers
from common.serializer import *

from post.models import *
from notify.models import Notification

from django.db import transaction

from accounts.models import CustomUser

from django.utils import timezone

from django.db.models import Case, When, BooleanField

#ホームページを表示するシリアライザ
class HomePageReadSerializer(PostReadSerializer):
    
    post_user = serializers.SerializerMethodField(read_only = True)
    class Meta(PostReadSerializer.Meta):
        model = Post
        fields = (*PostReadSerializer.Meta.fields ,"post_user")
    
    def get_post_user(self, obj):

        return UserInfSerializer(obj.post_user, context=self.context).data


#マイページを表示するシリアライザ
class MypagePostReadSerializer(PostReadSerializer):
    post_user = serializers.SerializerMethodField(read_only = True)
    class Meta(PostReadSerializer.Meta):
        model = Post
        fields = (*PostReadSerializer.Meta.fields ,"post_user")
    
    def get_post_user(self, obj):
        return UserInfSerializer(obj.post_user, context=self.context).data


#グループ一覧のシリアライザ、最後のメッセージも送る
class GroupListReadSerializer(serializers.ModelSerializer):
    
    last_post_nickname = serializers.CharField(read_only = True)
    last_post_username = serializers.CharField(read_only = True)
    last_post_content = serializers.CharField(read_only = True)
    last_post_created_at = serializers.DateTimeField(read_only = True)
    
    class Meta:
        model = Group
        fields = ["id", "group_name", "group_image", "last_post_nickname", "last_post_username", "last_post_content","last_post_created_at"]


#グループ作成画面のシリアライザ、ユーザのフレンド一覧を表示する
class GroupUserFriedReadSerializer(FriendListSerializer):
    class Meta(FriendListSerializer.Meta):
        pass

#グループ作成のpostシリアライザ
class GroupCreateWriteSerializer(serializers.ModelSerializer):
    
    #リストに入ったid、childでオブジェクトの型を指定、allow_emptyで空を許容しない
    send_ids = serializers.PrimaryKeyRelatedField(
        many = True,
        write_only = True,
        queryset = CustomUser.objects.all()
        )
    
    class Meta:
        model = Group
        fields = ["send_ids","group_name","group_image"]
    
    #送られてきたidのチェックをする
    def validate_send_ids(self, users):
        me = self.context["request"].user

        #重複排除、返すときlistに戻す
        user_id_dict = {user.id:user for user in users}
        send_ids = set(user_id_dict.keys())

        #自分自身がidとして含まれていた場合
        if me.id in send_ids:
            raise serializers.ValidationError("グループ作成に自分自身は指定できません。")
        
        #自身のフレンドを取得する
        friendship = (
            FS.objects
            .filter(Q(user_a = me, user_b__in = send_ids) |
                    Q(user_b = me, user_a__in = send_ids),
                    deleted_at__isnull = True,
                    status = FS.Status.ACPT
            )
        )
        
        #フレンドのユーザのみを抽出する。辞書にして後のifでの検索をはやくする
        friends = {i.user_a_id if i.user_b_id == me.id else i.user_b_id for i in friendship}

        #friendでないユーザを判定してリストに追加する
        not_friends = [j for j in send_ids if j not in friends]
        
        #もしフレンドでないユーザがsend_idsに含まれていたらエラー
        if not_friends:
            raise serializers.ValidationError(f"グループに追加できるユーザはフレンドのみです")

        return list(user_id_dict.values())
    
    #トランザクション、すべて成功か失敗すべきときはこれをつくる
    @transaction.atomic
    def create(self, validated_data):
        me = self.context["request"].user
        
        users = validated_data["send_ids"]
        
        image = validated_data["group_image"]
        
        name = validated_data["group_name"]
            
        creator_name = me.nickname if me.nickname else me.username
        
        #グループを作成
        group_rs = Group.objects.create(
            creator = me,
            group_name = name if (name != "" and name != None) else creator_name + "のグループ",
            group_image = image
        )
        
        #membersをつくる、複数の行を追加するmembersを作ってからbulk_createする
        members = [Member(group = group_rs, member = user) for user in users]
        
        #作成者に権限をつけてmembersに追加
        members.append(Member(group = group_rs, member_id = me.id, role = True))
        
        Member.objects.bulk_create(members)
        
        return group_rs

#グループ設定変更のpostシリアライザ
class GroupUpdateWriteSerializer(serializers.ModelSerializer):
    #リストに入ったid、childでオブジェクトの型を指定
    send_ids = serializers.PrimaryKeyRelatedField(
        many = True,
        write_only = True,
        queryset = CustomUser.objects.all(),
        required=False
        )
    
    delete_user = serializers.PrimaryKeyRelatedField(
        write_only = True,
        queryset = CustomUser.objects.all(),
        required = False,
        allow_null = True
        )
    
    give_authority_user = serializers.PrimaryKeyRelatedField(
        write_only = True,
        queryset = CustomUser.objects.all(),
        required = False,
        allow_null = True
    )
    
    class Meta:
        model = Group
        fields = ["id","group_name" ,"group_image", "delete_user","send_ids", "give_authority_user"]
    
    #コンストラクタをオーバーライドする、クエリー節約のため
    def __init__(self, *args, **kwargs):
        #これをしないとぶっ壊れる
        super().__init__(*args, **kwargs)

        self.request_user_is_member:bool | None = None
        self.request_user_is_admin:bool | None = None
    
    #この関数で、自身がそのグループに属していないとエラー
    def _require_member(self):
        
        user = self.context["request"].user
        
        if not self.instance :
            raise serializers.ValidationError("グループが特定できません")
        
        if self.request_user_is_member is None:
            self.request_user_is_member = self.instance.is_member(user)
            
        if self.request_user_is_member is False:
            raise serializers.ValidationError("この操作を行う権限がありません")
    
    def _require_admin(self):
        
        user = self.context["request"].user
        
        if not self.instance:
            raise serializers.ValidationError("グループが特定できません")
        
        if self.request_user_is_admin is None:
            self.request_user_is_admin = self.instance.is_admin(user)
            
        if self.request_user_is_admin is False:
            raise serializers.ValidationError("この操作を行う権限がありません")
    
    #追加するユーザデータのバリデーション
    def validate_send_ids(self, users):
        me = self.context["request"].user
        self._require_member()
        
        if not users:
            return []

        #重複排除、返すときlistに戻す
        user_id_dict = {user.id:user for user in users}
        send_ids = set(user_id_dict.keys())

        #自分自身がidとして含まれていた場合
        if me.id in send_ids:
            raise serializers.ValidationError("ユーザ追加に自分自身は指定できません。")
        
        #自身のフレンドを取得する
        friendship = (
            FS.objects
            .filter(Q(user_a = me, user_b__in = send_ids) |
                    Q(user_b = me, user_a__in = send_ids),
                    deleted_at__isnull = True,
                    status = FS.Status.ACPT
            )
        )
        
        #フレンドのユーザのみを抽出する。辞書にして後のifでの検索をはやくする
        friends = {i.user_a_id if i.user_b_id == me.id else i.user_b_id for i in friendship}

        #friendでないユーザを判定してリストに追加する
        not_friends = [j for j in send_ids if j not in friends]
        
        #もしフレンドでないユーザがsend_idsに含まれていたらエラー
        if not_friends:
            raise serializers.ValidationError(f"グループに追加できるユーザはフレンドのみです")

        return list(user_id_dict.values())
    
    #ソフトデリートするユーザのバリデーション
    def validate_delete_user(self, user):
        if user is None:
            return None
        
        self._require_admin()
        
        if not self.instance.is_member(user):
            raise serializers.ValidationError("指定されたユーザはメンバーではありません")
        
        group_has_author = (
            Member.objects
            .exclude(member_id = user.id)
            .filter(
                group = self.instance,
                role = True,
                left_at__isnull = True
            ).exists()
        )
        if not group_has_author:
            raise serializers.ValidationError("グループに管理者が一人以上必要です")
        
        return user
    
    #権限付与するユーザのvalidation
    def validate_give_authority_user(self, user):
        
        if user is None:
            return None
        if user == self.context["request"].user:
            raise serializers.ValidationError("自身の権限を変更することはできません")
        
        self._require_admin()
        if not self.instance.is_member(user):
            raise serializers.ValidationError("指定されたユーザはメンバーではありません")
        return user
    
    #デコレータで原子性担保
    @transaction.atomic
    def update(self, instance, validated_data):
        self._require_member()
        
        #null、つまり指定しないなら更新しない
        if "group_name" in validated_data:
            name = validated_data["group_name"]
            if name not in ("", None):
                instance.group_name = name
            
        if "group_image" in validated_data:
            image = validated_data["group_image"]
            if image is not None:
                instance.group_image = image

        instance.save()
        
        users = validated_data.get("send_ids", None)
        delete_user = validated_data.get("delete_user", None)
        give_authority_user = validated_data.get("give_authority_user", None)
        
        #give_authority_userがあるなら、権限をトグルする
        if give_authority_user is not None:
            qs =Member.objects.filter(
                group = instance,
                member = give_authority_user,
                left_at__isnull = True,
            )
            qs.update(
                    #DjangoORMの機能、条件分岐でトグルできる
                    role = Case(
                        When(role = True, then = False),
                        default = True,
                        output_field = BooleanField()
                    )
                )
        
        #delete_userがあるならleft_atに時間を入れてソフトデリート
        if delete_user is not None:
            Member.objects.filter(
                group = instance,
                member = delete_user,
                left_at__isnull = True
            ).update(left_at = timezone.now())
        
        #追加のユーザが存在したら追加する
        if users is not None:
            
            #元いたユーザを検索
            om_list = list(
                Member.objects.filter(group = instance)
            )
            #辞書でまわすことでソフトデリートされてるメンバーを特定できる
            old_member = {m.member_id : m for m in om_list}
            
            #元いたメンバーかを都度確認してそうでないならリストに挿入
            new_members = []
            #ソフトデリートされてかつそのユーザが再度追加された場合、このリストに挿入する
            delete_cancel = []
            
            for user in users:
                m = old_member.get(user.id)
                if m is not None:
                    if m.left_at is not None:
                        delete_cancel.append(m.id)
                    else:
                        raise serializers.ValidationError("すでにグループに存在するユーザは追加できません")
                else:
                    new_members.append(Member(group = instance, member = user))
            
            if new_members:
                Member.objects.bulk_create(new_members)
            if delete_cancel:
                Member.objects.filter(
                    left_at__isnull = False,
                    id__in = delete_cancel,
                    group = instance
                    ).update(left_at = None)
        
        return instance

#グループに追加できるフレンドを返すシリアライザ
class GroupInviteFriendReadSerializer(FriendListSerializer):
    
    class Meta(FriendListSerializer.Meta):
        pass

#メンバー一覧のシリアライザ
class MemberReadSerializer(serializers.ModelSerializer):
    member_info = UserInfSerializer(source='member', read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'member', 'member_info']        

#グループ情報のシリアライザ
class GroupReadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Group
        fields = ["id", "group_name", "group_image", "group_description"]
    

class PostInGroupReadSerializer(PostReadSerializer):
    post_user = serializers.SerializerMethodField(read_only = True)
    class Meta(PostReadSerializer.Meta):
        model = Post
        fields = PostReadSerializer.Meta.fields + ["post_user","parent_post"]
    def get_post_user(self, obj):
        return UserInfSerializer(obj.post_user, context=self.context).data

#投稿のpostシリアライザ
class PostCreateWriteSerializer(serializers.ModelSerializer):
    
    parent_post = serializers.PrimaryKeyRelatedField(
        write_only = True,
        queryset = Post.objects.all(),
        allow_null = True,
        required = False,
    )
    
    class Meta:
        fields = ["post_images", "post_content","parent_post","group"]
        model = Post

    def validate_post_images(self, image):
        
        return image
    def validate_post_content(self, text):
        
        return text
    def validate(self, attrs):
        
        group = attrs.get("group")
        parent_post = attrs.get("parent_post")
        image = attrs.get("post_images")
        text = attrs.get("post_content")
        me = self.context["request"].user
        
        is_group_member = (
            Member.objects
            .filter(
                group = group, 
                member = me,
                left_at__isnull = True
            ).exists()
        )
        if not is_group_member:
            raise serializers.ValidationError("このグループに所属していません")
        
        if text in (None, "") and image is None:
            raise serializers.ValidationError("テキストか画像のいずれかが必要です")
        
        if parent_post is not None:
            if parent_post.group.id != group.id:
                raise serializers.ValidationError("親投稿が不正です")
            if parent_post.deleted_at is not None:
                raise serializers.ValidationError("親投稿が不正です")
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        
        me = self.context["request"].user
        image_in_request = validated_data.get("post_images") 
        
        post_rs = Post.objects.create(
            post_user = me,
            **validated_data
        )
        
        if image_in_request:
            def _create_notifications():
                user_ids = (
                    Member.objects
                    .filter(group=post_rs.group, left_at__isnull=True,member__deleted_at__isnull= True)
                    .exclude(member=me)
                    .values_list("member_id", flat=True)
                )
                notifies = [
                    Notification(
                        user_id=uid,
                        actor=me,
                        status=Notification.Status.POST,
                        post=post_rs,
                        message=f"{me.nickname if me.nickname else me.username}さんが投稿しました",
                    )
                    for uid in user_ids
                ]
                Notification.objects.bulk_create(notifies)
            transaction.on_commit(_create_notifications)
        
        return post_rs


class CommentReadSerializer(serializers.ModelSerializer):
    user_info = UserInfSerializer(source='post_user', read_only=True)

    class Meta:
        model = Post
        fields = ['post_id',"parent_post" , 'post_content', 'post_images', 'created_at', 'user_info', 'group']

class PostDetailSerializer(serializers.ModelSerializer):
    user_info = UserInfSerializer(source='post_user', read_only=True)
    class Meta:
        model = Post
        fields = ['post_id', 'post_content', 'post_images', 'created_at', 'user_info', 'group']

    def get_user_info(self, obj):
        return UserInfSerializer(obj.post_user, context=self.context).data  
    def get_comments(self, obj):
        return CommentReadSerializer(obj.post_user, context=self.context).data 