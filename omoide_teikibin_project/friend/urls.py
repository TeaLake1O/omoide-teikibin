from django.urls import path
from .views import *


urlpatterns = [
    path("", FriendView.as_view(), name= "friend_view"),
    path("requests/", RequestListView.as_view(), name= "request_view"),
    path("action/", FriendRequestView.as_view(), name= "request_action"),
]
