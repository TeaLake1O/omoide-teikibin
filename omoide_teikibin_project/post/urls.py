from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [
    # URLs for JSON API
    path('api/posts/', views.PostListAPIView.as_view(), name='post_list_api'),
    path('api/post/<int:pk>/', views.PostDetailAPIView.as_view(), name='post_detail_api'),
    path('api/groups/', views.GroupListAPIView.as_view(), name='group_list_api'),
]
