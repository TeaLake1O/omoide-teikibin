# post/urls.py
from django.urls import path
from . import views
from friend.views import FriendListView
from post.views import *

app_name = 'post'

urlpatterns = [
    path('home', CursorHomePageView.as_view(), name='homepage'),
    path('mypage/<str:username>/post', CursorMypagePostView.as_view(), name='mypage'),
    path('group', GroupListView.as_view(), name='group_list'),
    path('group/create', GroupCreateUserListView.as_view(), name='group_create_userlist'),
    path('group/create/action', GroupCreateView.as_view(), name='group_create_action'),
    path('group/<int:pk>/update/action', GroupUpdateView.as_view(), name='group_update_action'),
    path("group/<int:pk>/member", MemberListAPIView.as_view(), name = "member_list"),
    path("group/<int:pk>/member/friend", GroupInviteFriendListView.as_view(), name = "invite_friend"),
    
    path("group/action", CreatePostView.as_view(), name = "create_post"),
    
    path('group/<int:pk>', views.GroupInfoView.as_view(), name='group_detail_page'),
    path('group/<int:pk>/posts', views.GroupPostsView.as_view(), name='group_detail_posts'),
    
    path('detail/<uuid:post_id>/comments/', CommentListAPIView.as_view(), name='comment_list_api'),
    path('detail/<uuid:post_id>/', PostDetailAPIView.as_view(), name='post_detail_page')
]
