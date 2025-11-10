from django.views.generic import ListView, View, FormView, UpdateView, CreateView

from .models import Friendship
from friend.serialyzer import FriendReadSerializer, FriendRequestSerializer, FriendWriteSerializer

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from rest_framework import permissions, generics

#自身のフレンド関係が成立済みのユーザの一覧表示
class FriendView(generics.ListAPIView):
    #シリアライザ
    serializer_class = FriendReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        f = (
            Friendship.objects
            .filter(Q(username_a = user) | Q(username_b = user))
            .filter(status = Friendship.Status.ACPT)
            .select_related("username_a", "username_b")
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
            .filter(Q(username_a = user) | Q(username_b = user))
            .filter(status__in = [
                Friendship.Status.A2B,
                Friendship.Status.B2A,
            ])
            .select_related("username_a", "username_b")
            .order_by("-friend_date")
        )
        return f

#フレンドリクエストを送る。postはシリアライザとか指定するだけでいい
class FriendRequestView(generics.CreateAPIView):
    #シリアライザ
    serializer_class = FriendWriteSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]