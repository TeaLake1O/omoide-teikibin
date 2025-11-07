from django.views.generic import ListView, View, FormView, UpdateView, CreateView
from .models import Friendship
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


class FriendView(LoginRequiredMixin, ListView):
    model = Friendship
    
    template_name = "friend_view.html"
    
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