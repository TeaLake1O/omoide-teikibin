from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [

    path('list_page/', views.PostListView.as_view(), name='post_list_page'), 
    path('detail/<uuid:post_id>/', views.post_detail_page, name='post_detail_page'), 
    path('create_page/', views.PostCreatePageView.as_view(), name='create_post_page'), 

    path('api/list/', views.PostListAPIView.as_view(), name='post_list_api'), 
    path('api/detail/<uuid:pk>/', views.PostDetailAPIView.as_view(), name='post_detail_api'), 
    path('api/create/', views.create_post, name='create_post_api'), 

    path('', views.homepage, name='homepage'),
    

    # --- Group URLs ---
    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('groups/create/', views.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/join/', views.join_group, name='join_group'),
    path('groups/<int:pk>/leave/', views.leave_group, name='leave_group'), 
    # --- Notification URLs --- 
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_as_read, name='mark_notification_read'),
]