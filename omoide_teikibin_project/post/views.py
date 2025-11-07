from django.http import JsonResponse
from django.views import View
from .models import Post, Group


class PostListAPIView(View):
    """
    投稿のリストをJSONとして返すAPIエンドポイント。
    """
    def get(self, request, *args, **kwargs):
        # 作成者のユーザー名を含む必要なフィールドを取得します
        posts = Post.objects.order_by('-created_at').values(
    'post_id', 'post_user__username', 'post_content', 'created_at'
)

        return JsonResponse(list(posts), safe=False)


class PostDetailAPIView(View):
    """
    特定の投稿の詳細をJSONとして返すAPIエンドポイント。
    """
    def get(self, request, pk, *args, **kwargs):
        post_data = Post.objects.filter(pk=pk).values(
    'post_id',
    'post_user__username',
    'post_content',
    'created_at',
    'updated_at'
).first()


        if not post_data:
            # 投稿が見つからない場合は404ステータスを返す
            return JsonResponse({'error': 'Post not found'}, status=404)
        return JsonResponse(post_data)


class GroupListAPIView(View):
    """
    グループのリストをJSONとして返すAPIエンドポイント。
    """
    def get(self, request, *args, **kwargs):
        groups = Group.objects.values('id', 'group_name', 'group_description', 'created_at')
        return JsonResponse(list(groups), safe=False)