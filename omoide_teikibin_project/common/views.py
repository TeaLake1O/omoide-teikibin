from rest_framework import generics,permissions
from accounts.models import CustomUser
from friend.models import Friendship
from django.db.models import Q



#ユーザを検索するView、
class UserSearchView(generics.ListAPIView):
    #継承する
    #serializer_class = 
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        me = self.request.user
        
        username = self.request.query_params.get("username")
        
        if not username :
            #ListAPIViewでnoneを返すとエラーなのでこれを返す
            CustomUser.objects.none
        
        result = (
            CustomUser.objects
            .filter(username__icontains = username)
        )
        return result


#自身のフレンド関係が成立済みのユーザの一覧表示
class FriendListView(generics.ListAPIView):
    #シリアライザ、継承する
    #serializer_class = FriendReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        me = self.request.user
        
        username = self.request.query_params.get("username")
        
        result = (
            Friendship.objects
            .filter(Q(user_a = me) | Q(user_b = me),
                    status = Friendship.Status.ACPT,
                    deleted_at__isnull = True,
                )
            .select_related("user_a", "user_b")
            .order_by("-friend_date")
        )
        return result if not username else result.filter(
            Q(user_a = me, user_b__username__icontains = username) |
            Q(user_b = me, user_a__username__icontains = username)
        )