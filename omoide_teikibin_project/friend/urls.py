from django.urls import path
from .views import *

urlpatterns = [
    path("view", FriendView.as_view()),
]
