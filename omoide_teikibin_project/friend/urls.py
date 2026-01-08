from django.urls import path
from .views import *


urlpatterns = [
    path("", MyFriendListView.as_view(), name= "friend_view"),
    path("requests/", RequestListView.as_view(), name= "request_view"),
    path("requests/<str:username>", FriendRequestView.as_view(), name= "request_action"),
    path("search", UserSearchView.as_view(), name= "user_search"),
    
    path("message/", DMListView.as_view(), name= "message"),
    path("message/<str:username>/", DMView.as_view(), name= "message_view"),
    path("message/<str:username>/action", DMSendView.as_view(), name= "message_action"),
]
