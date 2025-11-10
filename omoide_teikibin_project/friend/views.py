from django.views.generic import ListView, View, FormView, UpdateView, CreateView

from .models import Friendship
from friend.serialyzer import UserFriendSerializer

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from rest_framework import permissions, generics


class FriendView(generics.ListAPIView):
    model = Friendship
    #シリアライザ
    serializer_class = UserFriendSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        f = (
            Friendship.objects
            .filter(Q(username_a = user) | Q(username_b = user))
            .filter(status = "ACPT")
            .select_related("username_a", "username_b")
            .order_by("-friend_date")
        )
        return f

class FriendRequestView(UpdateView,LoginRequiredMixin):
    def get(self, request):
        q = request.GET["q"]