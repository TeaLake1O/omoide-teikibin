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

class PostNotificationView(generics.ListAPIView):
    pagination_class = None
    #シリアライザ
    serializer_class = PostNotifyReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        
        me = self.request.user
        
        friend = (
            Friendship.objects
                .filter(
                    status = Friendship.Status.ACPT,
                    deleted_at__isnull = True,
                    user_a__deleted_at__isnull = True,
                    user_b__deleted_at__isnull = True,
                )
                .filter(
                    Q(user_a=me, user_b_id=OuterRef("actor_id")) | Q(user_b=me, user_a_id=OuterRef("actor_id"))
                )
            
        )
        
        #Memberのサブクエリ、memberでの条件や、OuterRefで親から引き渡されたgroup_idとgroupを比較してフィルターする
        qs = (
            Notification.objects
            .filter(user=me,post__isnull = False,
                    status=Notification.Status.POST,
                    post__deleted_at__isnull = True,
                    post__post_user__deleted_at__isnull = True
                )
            .exclude(post__post_images = "")
            #annotateは各行に計算済みのデータを作る行、この場合、memberがTrueかをmember_flgにいれてfilterしている
            #Existsはbool、Subqueryはデータそのもの
            .annotate(friend_flg = Exists(friend))
            .filter(friend_flg= True)
        )
        before = self.request.query_params.get("before")
        after  = self.request.query_params.get("after")
        limit = self.request.query_params.get("limit")
        
        return post_query(before=before, after=after, raw_limit=limit,qs=qs)