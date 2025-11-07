from django.views.generic import ListView
from .models import Friendship

class FriendView(ListView):
    model = Friendship
    
    template_name = "friend_view.html"