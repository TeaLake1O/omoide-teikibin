from django.urls import path

from .views import *

urlpatterns = [
    path("post", PostNotificationView.as_view(), name = "post_notify"),
    path("friend", NotificationView.as_view(), name = "friend_notify"),
]