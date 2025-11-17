
from rest_framework import serializers
from common.serializer import *

from post.models import *

from django.db import transaction

from accounts.models import CustomUser

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

#グループ作成画面のシリアライザ、ユーザのフレンド一覧を表示する
class GroupCreateUserFriedSerializer(FriendListSerializer):
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
    
    def create(self, validated_data):
        me = self.context["request"].user
        
        users = validated_data["send_ids"]
        
        image = validated_data["group_image"]
        
        name = validated_data["group_name"]
        
        #トランザクション、複数テーブルがあってかつすべて成功か失敗すべきときはこれをつくる
        with transaction.atomic():
            
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
class GroupUpdateSerializer(serializers.ModelSerializer):
    #リストに入ったid、childでオブジェクトの型を指定、allow_emptyで空を許容しない
    send_ids = serializers.PrimaryKeyRelatedField(
        many = True,
        write_only = True,
        queryset = CustomUser.objects.all()
        )
    delete_user = serializers.PrimaryKeyRelatedField(write_only = True)
    
    class Meta:
        model = Group
        fields = ["id","group_name" ,"group_image", "delete_user","send_ids"]
    
    def validate_send_ids(self, users):
        me = self.context["request"].user
        
        if not users :
            return

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
    
    def validate_delete_user(self, user):
        group_id = self.context["request"].data.get("group_id")
        
        if not user or group_id is None:
            return
        
        is_group_admin = (
            Member.objects
            .filter(group_id = group_id,
                    member = user,
                    role = True
                ).exists()
        )
        if not is_group_admin :
            return


#メンバー一覧のシリアライザ
class MemberReadSerializer(serializers.ModelSerializer):
    member_info = UserInfSerializer(source='member', read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'member', 'member_info']        


class CommentReadSerializer(serializers.ModelSerializer):
    user_info = UserInfSerializer(source='comment_user', read_only=True)
    class Meta:
        model = Post
        fields = ['post_id', 'comment_content', 'created_at', 'user_info', 'post_name', 'post']

    def get_user_info(self, obj):
        return UserInfSerializer(obj.comment_user, context=self.context).data

class PostDetailSerializer(serializers.ModelSerializer):
    user_info = UserInfSerializer(source='post_user', read_only=True)
    comments = CommentReadSerializer(source='parent_post', many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['post_id', 'post_content', 'post_images', 'created_at', 'user_info', 'group', 'comments']

    def get_user_info(self, obj):
        return UserInfSerializer(obj.post_user, context=self.context).data  