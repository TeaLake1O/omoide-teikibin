from django.views.generic import ListView, View, FormView, UpdateView
from .models import Friendship
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


class FriendView(ListView,LoginRequiredMixin):
    model = Friendship
    
    template_name = "friend_view.html"
    redirect_field_name = "next"
    
    def get_queryset(self):
        user = self.request.user
        return (
            Friendship.objects
            .filter(Q(username_a = user) | Q(username_b = user))
            .filter(status = "ACPT")
            .select_related("username_a", "username_b")
            .order_by("")
        )

class FriendRequestView(UpdateView,LoginRequiredMixin):
    def get(self, request):
        q = request.GET["q"]