# post/urls.py
from django.urls import path
from . import views
from post.views import *

app_name = 'post'

urlpatterns = [
    path('', HomePageView.as_view(), name='homepage'),
    path('list_page/', views.post_list_page, name='post_list_page'),  # <- Đây là tên đúng
    path('detail/<uuid:post_id>/', views.post_detail_page, name='post_detail_page'),
    path('create_page/', views.PostCreatePageView.as_view(), name='create_post_page'),
    
    
    # API
    path('api/list/', views.PostListAPIView.as_view(), name='post_list_api'),
    path('api/detail/<uuid:pk>/', views.PostDetailAPIView.as_view(), name='post_detail_api'),
    path('api/create/', views.PostCreateAPIView.as_view(), name='post_create_api'),

    # Groups
    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('groups/create/', views.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/join/', views.join_group, name='group_join'),
    path('groups/<int:pk>/leave/', views.leave_group, name='group_leave'),
]
