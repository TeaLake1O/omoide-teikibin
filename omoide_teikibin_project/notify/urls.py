from django.urls import path

from .views import *

urlpatterns = [
    path("post", PostNotificationView.as_view(), name = "post_notify"),
    path("post/count", PostNotificationCountView.as_view(), name = "post_notify_count"),
    path("post/mark", PostNotificationMarkReadView.as_view(), name = "post_notify_mark_read"),
    path("friend", NotificationView.as_view(), name = "friend_notify"),
    path("friend/count", NotificationCountView.as_view(), name = "friend_notify_count"),
    path("friend/mark", FriendNotificationMarkReadView.as_view(), name = "friend_notify_mark_read"),
    
]