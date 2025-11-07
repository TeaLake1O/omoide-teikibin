from django.views.generic import ListView, View, FormView, UpdateView
from .models import Friendship
from django.contrib.auth.mixins import LoginRequiredMixin


class FriendView(ListView,LoginRequiredMixin):
    model = Friendship
    
    template_name = "friend_view.html"
    redirect_field_name = "next"

class FriendRequestView(UpdateView,LoginRequiredMixin):
    def get(self, request):
        q = request.GET["q"]