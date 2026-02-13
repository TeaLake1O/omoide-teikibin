from django.db.models import Exists, OuterRef, Subquery
from post.serializers import *
from rest_framework.exceptions import PermissionDenied

from .models import Post, Group, Member

from django.db.models import Q
from rest_framework import permissions, generics
from rest_framework.pagination import CursorPagination

from common.views import *
from common.util import post_query

from django.shortcuts import get_object_or_404

#HomePageViewなど無限スクロールと新規投稿取得の両方が必要なviewは、自前クエリで投稿を返すのとページネーションで投稿を返すのにわける


class PostCursorPagination(CursorPagination):
    page_size = 4
    page_size_query_param = "limit" 
    cursor_query_param = "cursor"
    ordering = ("-created_at", "-post_id")

#ホームページを更新するview、カーソルあり
class CursorHomePageView(generics.ListAPIView):
    pagination_class = PostCursorPagination
    #シリアライザ
    serializer_class = HomePageReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        
        me = self.request.user
        
        #Memberのサブクエリ、memberでの条件や、OuterRefで親から引き渡されたgroup_idとgroupを比較してフィルターする
        member = Member.objects.filter(
            member_id = me.id,
            member_id__deleted_at__isnull = True,
            left_at__isnull = True,
            group = OuterRef("group_id")
        )
        
        #migrationする
        qs = (
            Post.objects
            .filter(parent_post__isnull = True,deleted_at__isnull = True,post_images__isnull = False,post_user__deleted_at__isnull = True)
            .exclude(post_images = "")
            #annotateは各行に計算済みのデータを作る行、この場合、memberがTrueかをmember_flgにいれてfilterしている
            #Existsはbool、Subqueryはデータそのもの
            .annotate(member_flg = Exists(member))
            .filter(member_flg = True)
            .select_related("group", "post_user")
        )
        
        return qs

class BaseMypagePostView:
    def get_base_queryset(self):
        username = self.kwargs["username"]
        me = self.request.user
        member = Member.objects.filter(
            member_id =me.id,
            left_at__isnull = True,
            group = OuterRef("group_id")
        )
        qs = Post.objects.filter(
            post_user__username = username,
            deleted_at__isnull = True,
            parent_post__isnull = True,
            post_images__isnull = False,
            post_user__deleted_at__isnull = True
        ).exclude(post_images = ""
        ).annotate(member_flg = Exists(member)
        ).filter(member_flg = True
        ).select_related("group", "post_user")
        return qs


class CursorMypagePostView(BaseMypagePostView,generics.ListAPIView):
    pagination_class = PostCursorPagination
    #シリアライザ
    serializer_class = MypagePostReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.get_base_queryset()

#グループ一覧を表示するView
class GroupListView(generics.ListAPIView):
    
    serializer_class = GroupListReadSerializer
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        
        me = self.request.user

        post = Post.objects.filter(
            group = OuterRef("id"),
            deleted_at__isnull = True
        ).order_by("-created_at")
        
        result = (
            Group.objects
            .filter(member__member = me, member__left_at__isnull = True)
            .annotate(last_post_content = Subquery(post.values("post_content")[:1]),
                last_post_username = Subquery(post.values("post_user__username")[:1]),
                last_post_nickname = Subquery(post.values("post_user__nickname")[:1]),
                last_post_created_at = Subquery(post.values("created_at")[:1]))
            
            #.annotate(is_member = Exists(member))
            #.filter(is_member = True)
        ).order_by("-last_post_created_at")
        return result


#グループの追加画面を表示するView
class GroupCreateUserListView(FriendListView):
    serializer_class = GroupUserFriedReadSerializer

#グループ作成のポスト
class GroupCreateView(generics.CreateAPIView):
    #シリアライザ
    serializer_class = GroupCreateWriteSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    #おまじない
    queryset = Group.objects.none() 
#グループ更新のポスト
class GroupUpdateView(generics.UpdateAPIView):
    
    #シリアライザ
    serializer_class = GroupUpdateWriteSerializer
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    #おまじない
    queryset = Group.objects.all()

#グループに追加できる自身のフレンドを表示するView
class GroupInviteFriendListView(FriendListView):
    
    #シリアライザ
    serializer_class = GroupInviteFriendReadSerializer
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    #FriendListViewを継承してクエリをグループに所属してないメンバーに絞る
    def get_queryset(self):
        me = self.request.user
        
        group_pk = self.kwargs['pk']
        qs = super().get_queryset()
        username = self.request.query_params.get("username")
        
        member_is_user_a =(
            Member.objects
            .filter(
                group_id = group_pk,
                member = OuterRef("user_a"),
                left_at__isnull = True
            )
        )

        member_is_user_b =(
            Member.objects
            .filter(
                group_id = group_pk,
                member = OuterRef("user_b"),
                left_at__isnull = True
            )
        )

        result = (
            qs
            .annotate(
                in_group_a = Exists(member_is_user_a),
                in_group_b = Exists(member_is_user_b)
            ).filter(
                Q(user_a = me, in_group_b = False) |
                Q(user_b = me, in_group_a = False)
            )
        )
        return result

#グループに所属しているメンバー一覧を表示するView
class MemberListAPIView(generics.ListAPIView):
    serializer_class = MemberReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_pk = self.kwargs['pk']
        
        me = self.request.user
        
        result = Member.objects.filter(
            group__pk=group_pk,
            left_at__isnull=True,
        ).select_related('member')
        
        if not result.filter(member = me).exists():
            raise PermissionDenied()
        return result

#グループ内投稿一覧View
class GroupInfoView(generics.RetrieveAPIView):
    serializer_class = GroupReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs['pk']
        obj = get_object_or_404(Group, pk=pk)

        if not obj.member_set.filter(member=self.request.user, left_at__isnull=True).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("このグループに所属していません")

        return obj


class GroupPagination(CursorPagination):
    page_size = 10
    page_size_query_param = "limit" 
    cursor_query_param = "cursor"
    ordering = ("-created_at")
#グループ内投稿を表示するview
class GroupPostsView(generics.ListAPIView):
    serializer_class = PostInGroupReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = GroupPagination
    lookup_field = 'pk'

    def get_queryset(self):
        pk = self.kwargs["pk"]
        group = get_object_or_404(Group, pk=pk)

        is_member = group.member_set.filter(
            member=self.request.user,
            left_at__isnull=True
        ).exists()
        if not is_member:
            raise PermissionDenied("このグループに所属していません")

        return Post.objects.filter(group=group)


#投稿ポスト
class CreatePostView(generics.CreateAPIView):
    #シリアライザ
    serializer_class = PostCreateWriteSerializer
    
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    #おまじない
    queryset = Post.objects.all()

class PostDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        post_id = self.kwargs['post_id']
        obj = get_object_or_404(Post, post_id=post_id)

        if not obj.group.member_set.filter(member=self.request.user, left_at__isnull=True).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("あなたはこの投稿を見る権限がありません。")

        return obj

class CommentListAPIView(generics.ListAPIView):
    serializer_class = PostDetailSerializer
    pagination_class = PostCursorPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, post_id=post_id)

        if not post.group.member_set.filter(member=self.request.user, left_at__isnull=True).exists():
            raise PermissionDenied("あなたはこの投稿のコメントを見る権限がありません。")

        return Post.objects.filter(parent_post=post, deleted_at__isnull=True).select_related('post_user')

