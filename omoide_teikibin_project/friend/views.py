from friend.models import *
from friend.serialyzer import *

from django.db.models import Q
from rest_framework import permissions, generics

from django.db.models import Subquery, OuterRef


#自身のフレンド関係が成立済みのユーザの一覧表示
class FriendListView(generics.ListAPIView):
    #シリアライザ
    serializer_class = FriendReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        f = (
            Friendship.objects
            .filter(Q(user_a = user) | Q(user_b = user))
            .filter(status = Friendship.Status.ACPT)
            .select_related("user_a", "user_b")
            .order_by("-friend_date")
        )
        return f

#自身、もしくは別のユーザのデータを返すget
class RequestListView(generics.ListAPIView):
    #シリアライザ
    serializer_class = FriendRequestSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        f = (
            Friendship.objects
            .filter(Q(user_a = user) | Q(user_b = user))
            .filter(status__in = [
                Friendship.Status.A2B,
                Friendship.Status.B2A,
            ])
            .select_related("user_a", "user_b")
            .order_by("-friend_date")
        )
        return f

#フレンドリクエストを送る。postはシリアライザとか指定するだけでいい
class FriendRequestView(generics.CreateAPIView):
    #シリアライザ
    serializer_class = FriendWriteSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]

class DMListView(generics.ListAPIView):
    #シリアライザ
    serializer_class = DMListReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        #メッセージごとの最新の主キーを取る
        last_msg_id = (
        Message.objects
        .filter(friendship = OuterRef('friendship_id'))
        .order_by('-send_at')
        .values('pk')[:1]
        )
        #11/10ここを勉強し直す
        user = self.request.user
        f = (
            Message.objects
            .select_related("friendship", "friendship__user_a", "friendship__user_b")
            .filter(Q(friendship__user_a = user) | Q(friendship__user_b = user))
            .filter(friendship__status = Friendship.Status.ACPT)
            .annotate(last_msg_id = Subquery(last_msg_id))
            .filter(pk = F("last_msg_id"))
            .order_by("-send_at")
        )
        return f