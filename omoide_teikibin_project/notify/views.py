from django.db.models import Exists, OuterRef, Subquery
from .serializers import *
from rest_framework.exceptions import PermissionDenied

from post.models import Post,Group,Member
from friend.models import Friendship as FS


from django.db.models import Q
from rest_framework import permissions, generics

from common.views import *
from common.util import post_query

from django.shortcuts import get_object_or_404
from rest_framework.pagination import CursorPagination
from rest_framework.views import APIView
from rest_framework.response import Response

class NotifyCursorPagination(CursorPagination):
    page_size = 10
    page_size_query_param = "limit" 
    cursor_query_param = "cursor"
    ordering = ("-created_at", "-notify_id")


class PostNotificationView(generics.ListAPIView):
    pagination_class = NotifyCursorPagination
    #シリアライザ
    serializer_class = PostNotifyReadSerializer
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        
        me = self.request.user
        qs = (
            Notification.objects
            .filter(user = me,status = Notification.Status.POST,post__isnull = False)
        )
        return qs

class PostNotificationCountView(APIView):
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        
        me = self.request.user
        
        qs = (
            Notification.objects
            .filter(user = me,status = Notification.Status.POST,is_read = False,post__isnull = False)
        )
        
        return Response({"count": qs.count()})

class PostNotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        me = request.user
        updated = (
            Notification.objects
            .filter(
                user=me,
                status=Notification.Status.POST,
                is_read=False,
            )
            .update(is_read=True)
        )
        return Response({"updated": updated})


class NotificationView(generics.ListAPIView):
    pagination_class = NotifyCursorPagination
    #シリアライザ
    serializer_class = NotifyReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        
        me = self.request.user
        
        #Memberのサブクエリ、memberでの条件や、OuterRefで親から引き渡されたgroup_idとgroupを比較してフィルターする
        qs = (
            Notification.objects
            .filter(user=me,
                    status__in = [Notification.Status.FRIEND ,Notification.Status.MESSAGE])
        )
        return qs

class NotificationCountView(APIView):
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        
        me = self.request.user
        
        qs = (
            Notification.objects
            .filter(user=me,
                    status__in = [Notification.Status.FRIEND ,Notification.Status.MESSAGE],
                    is_read = False)
        )
        
        return Response({f"count":qs.count()})

class FriendNotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        me = request.user
        updated = (
            Notification.objects
            .filter(
                user=me,
                status=Notification.Status.POST,
                is_read=False,
            )
            .update(is_read=True)
        )
        return Response({"updated": updated})

