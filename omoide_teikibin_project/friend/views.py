from friend.models import *
from friend.serialyzer import *

from django.db.models import Q
from rest_framework import permissions, generics

from django.db.models import Subquery, OuterRef
from django.shortcuts import get_object_or_404


#自身のフレンド関係が成立済みのユーザの一覧表示
class FriendListView(generics.ListAPIView):
    #シリアライザ
    serializer_class = FriendReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        result = (
            Friendship.objects
            .filter(Q(user_a = user) | Q(user_b = user))
            .filter(status = Friendship.Status.ACPT)
            .filter(deleted_at__isnull = True)
            .select_related("user_a", "user_b")
            .order_by("-friend_date")
        )
        return result
#自身、もしくは別のユーザのデータを返すget
class RequestListView(generics.ListAPIView):
    #シリアライザ
    serializer_class = FriendRequestSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        result = (
            Friendship.objects
            .filter(Q(user_a = user) | Q(user_b = user))
            .filter(status__in = [
                Friendship.Status.A2B,
                Friendship.Status.B2A,
            ])
            .select_related("user_a", "user_b")
            .order_by("-friend_date")
        )
        return result
#フレンドリクエストを送るView。postはシリアライザとか指定するだけでいい
class FriendRequestView(generics.CreateAPIView):
    #シリアライザ
    serializer_class = FriendWriteSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    #validationerrorのときこれがないとエラーが出る
    queryset = Friendship.objects.none() 

class UserSearchView(generics.ListAPIView):
    serializer_class = FriendSearchSerializer
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        me = self.request.user
        
        username = self.request.query_params.get("username")
        
        if not username :
            return
        
        #11/13ここからやる
        
        result = (
            CustomUser.objects
            .filter(username__icontains = username)
        )
        return result

#DMのリストを表示するView、相手のiconと最後のメッセージを取得する
class DMListView(generics.ListAPIView):
    #シリアライザ
    serializer_class = DMListReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        #メッセージごとの最新の主キーを取る
        last_msg_id = (
            Message.objects
            #friendship（外部キー）と一致するfriendship_idを抽出
            .filter(friendship = OuterRef('friendship_id'))
            .filter(deleted_at__isnull = True)
            .order_by('-send_at')
            .values('pk')[:1]
        )
        
        user = self.request.user
        result = (
            Message.objects
            .select_related("friendship", "friendship__user_a", "friendship__user_b", "sender")
            .filter(Q(friendship__user_a = user) | Q(friendship__user_b = user))
            .filter(friendship__status = Friendship.Status.ACPT)
            .annotate(last_msg_id = Subquery(last_msg_id))
            .filter(pk = F("last_msg_id"))
            .order_by("-send_at")
        )
        return result
#DMを表示するView、getで受け取ったusernameと自身のDMを表示する
class DMView(generics.ListAPIView):
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
            .order_by("-send_at")
        )
        return result
#メッセージを送るView。
class DMSendView(generics.CreateAPIView):
    #シリアライザ
    serializer_class = DMWriteSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
