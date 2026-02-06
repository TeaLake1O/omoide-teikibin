from friend.models import *
from friend.serializer import *

from django.db.models import Q,F, Case, When, IntegerField,DateTimeField
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination

from django.db.models import Subquery, OuterRef,Case, When, Value, IntegerField
from django.shortcuts import get_object_or_404

from common.views import FriendListView
from common.util import fs_to_status,Status,UserSearchCursorPagination



class DmPagination(CursorPagination):
    page_size = 10
    page_size_query_param = "limit" 
    cursor_query_param = "cursor"
    ordering = ("-send_at")

#自身のフレンド関係が成立済みのユーザの一覧表示
class MyFriendListView(FriendListView):
    #シリアライザ
    serializer_class = FriendReadSerializer

#自身、もしくは別のユーザのデータを返すget
class RequestListView(generics.ListAPIView):
    #シリアライザ
    serializer_class = FriendRequestSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        
        me = self.request.user
        
        other_ids = (
            Friendship.objects.filter(
                Q(user_a=me) | Q(user_b=me),
                deleted_at__isnull=True,
                user_a__deleted_at__isnull=True,
                user_b__deleted_at__isnull=True,
            )
            .exclude(status=Friendship.Status.ACPT)
            .annotate(
                other_user_id=Case(
                    When(user_a=me, then=F("user_b_id")),
                    default=F("user_a_id"),
                    output_field=IntegerField(),
                )
            )
            .values_list("other_user_id", flat=True)
            .distinct()
        )
        friendship_updated_at_sq = (
            Friendship.objects.filter(
                deleted_at__isnull=True,
                user_a__deleted_at__isnull=True,
                user_b__deleted_at__isnull=True,
            )
            .exclude(status=Friendship.Status.ACPT)
            .filter(
                Q(user_a=me, user_b=OuterRef("pk")) |
                Q(user_b=me, user_a=OuterRef("pk"))
            )
            .values("updated_at")[:1]
        )

        return (
            CustomUser.objects.filter(id__in=other_ids)
            .annotate(updated_at=Subquery(friendship_updated_at_sq, output_field=DateTimeField())).order_by("-updated_at")
        )

#フレンドリクエストを送るView。postはシリアライザとか指定するだけでいい
class FriendRequestView(generics.GenericAPIView):
    #シリアライザ
    serializer_class = FriendWriteSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["put"]
    #validationerrorのときこれがないとエラーが出る
    queryset = Friendship.objects.none() 
    
    def put(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        friendship = ser.save()
        if (friendship is None):
            return Response({
                "status":"none"
            })
        
        elif (friendship.deleted_at is not None):
            return Response({
                "status":"none"
            })
            
        else :
            me = self.request.user
            status:Status = fs_to_status(friendship,me)
            return Response({
            "status": status,
            })
    
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        username = self.kwargs["username"]
        
        ctx["username"] = username
        return ctx
#ユーザを検索するView
class UserSearchView(generics.ListAPIView):
    serializer_class = FriendSearchSerializer
    pagination_class = UserSearchCursorPagination
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        me = self.request.user
        
        username = self.request.query_params.get("username")
        if not username :
            return
        
        qs = CustomUser.objects.filter(username__icontains=username).annotate(
            is_exact=Case(
                When(username__iexact=username, then=Value(2)),
                When(username__istartswith=username, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        
        return qs


#DMのリストを表示するView、相手のiconと最後のメッセージを取得する
class DMListView(generics.ListAPIView):
    serializer_class = DMListReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        last_msg = (
            Message.objects
            .filter(friendship_id=OuterRef("pk"), deleted_at__isnull=True)
            .order_by("-send_at")
        )

        qs = (
            Friendship.objects
            .select_related("user_a", "user_b")
            .filter(Q(user_a=user) | Q(user_b=user))
            .filter(status=Friendship.Status.ACPT)
            .annotate(
                last_msg_id=Subquery(last_msg.values("pk")[:1]),
                last_msg_content=Subquery(last_msg.values("message_text")[:1]),
                last_msg_send_at=Subquery(last_msg.values("send_at")[:1]),
                last_msg_sender_id=Subquery(last_msg.values("sender")[:1]),
            )
            .order_by("-last_msg_send_at")
        )
        return qs


#DMを表示するView、getで受け取ったusernameと自身のDMを表示する
class DMView(generics.ListAPIView):
    pagination_class = DmPagination
    #シリアライザ
    serializer_class = DMReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        other_name = self.kwargs["username"]
        #userがいないなら404
        other = get_object_or_404(CustomUser, username = other_name)
        result = (
            Message.objects
            .filter(
                (Q(friendship__user_a = user) & Q(friendship__user_b = other))|
                (Q(friendship__user_a = other) & Q(friendship__user_b = user))
                )
            .select_related("friendship")
            .filter(~Q(deleted_at__isnull = False))
        )
        return result


#メッセージを送るView。
class DMSendView(generics.CreateAPIView):
    #シリアライザ
    serializer_class = DMWriteSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
