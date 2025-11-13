from django.db.models import Exists, OuterRef
from post.serializers import *

# post/views.py 
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView


# Import các thư viện DRF cần thiết
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

# Local imports
from .serializers import PostSerializer
from .models import Post, Group, Member
from .forms import PostCreationForm, GroupCreationForm

from django.db.models import Q
from rest_framework import permissions, generics

class HomePageView(generics.ListAPIView):
    #シリアライザ
    serializer_class = HomePageReadSerializer
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        
        me = self.request.user
        
        #Memberのサブクエリ、memberでの条件や、OuterRefで親から引き渡されたgroup_idとgroupを比較してフィルターする
        member = Member.objects.filter(
            member_id = me.id,
            left_at__isnull = True,
            group = OuterRef("group_id")
        )
        
        MAX_GET_POST = 5
        
        #migrationする
        f = (
            Post.objects
            .filter(parent_post__isnull = True)
            .filter(deleted_at__isnull = True)
            #annotateは各行に計算済みのデータを作る行、この場合、memberがTrueかをmember_flgにいれてfilterしている
            .annotate(member_flg = Exists(member))
            .filter(member_flg = True)
            .select_related("group", "post_user")
            .order_by("-created_at")[:MAX_GET_POST]
        )
        return f

# ===== HOMEPAGE =====
def homepage(request):
    return render(request, 'homepage.html')

# ===== PAGE VIEWS =====
@login_required
def post_list_page(request):
    return render(request, 'post_list.html')

@login_required
def post_detail_page(request, post_id): # Note: This is redefined later, but let's keep it for now if used by old urls.
    post = get_object_or_404(Post, post_id=post_id)
    return render(request, 'post_detail.html', {'post': post})

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post_list.html' 
    context_object_name = 'posts' 
    
class PostCreatePageView(LoginRequiredMixin, CreateView):
    """投稿作成ページビュー"""
    model = Post
    form_class = PostCreationForm
    template_name = 'create_post.html'
    success_url = reverse_lazy('post:post_list_page')

    def form_valid(self, form):
        form.instance.post_user = self.request.user
        return super().form_valid(form)    

# ===== API Views  =====

# 1. API LIST
class PostListAPIView(ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

# 2. API DETAIL
class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'pk' 

# 3. API CREATE 
class PostCreateAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        serializer.save(post_user=self.request.user)

# ===== Class-Based Views for Page Rendering =====


# --- Group Views ---


class GroupListView(LoginRequiredMixin, ListView):
    """全部のグループを表示するビュー"""
    model = Group
    template_name = 'group_list.html'
    context_object_name = 'groups'

class GroupDetailView(LoginRequiredMixin, DetailView):
    """グループの詳細ページ"""
    model = Group
    template_name = 'group_detail.html'
    context_object_name = 'group'
    # 'pk' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        
        # グループの現在のメンバーを取得
        context['members'] = Member.objects.filter(group=group, left_at__isnull=True) 
        
        context['posts'] = group.group_posts.all().order_by('-created_at')[:20] 
        
        context['is_member'] = Member.objects.filter(
            group=group, 
            member=self.request.user,
            left_at__isnull=True
        ).exists()
        return context

class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupCreationForm
    template_name = 'group_form.html'
    # 作成成功後のリダイレクト先はform_validで指定
    
    def form_valid(self, form):

        form.instance.creator = self.request.user

        self.object = form.save() 
        
        Member.objects.create(
            member=self.request.user,
            group=self.object,
            role=True # 管理者権限
        )
        #移動先のURLにリダイレクト
        return redirect(self.get_success_url())

    def get_success_url(self):
        # 移動先のURLをグループ詳細ページに設定
        return reverse_lazy('post:group_detail', kwargs={'pk': self.object.pk})

# --- グループ参加・退会ビュー ---

@login_required
def join_group(request, pk):
    
    group = get_object_or_404(Group, pk=pk)
    
    # 作成または更新して、ユーザーをグループに参加させる
    Member.objects.update_or_create(
        group=group,
        member=request.user,
        defaults={'left_at': None, 'role': False} 
    )
    return redirect('post:group_detail', pk=pk)

@login_required
def leave_group(request, pk):

    group = get_object_or_404(Group, pk=pk)
    
    # 参加記録のleft_atフィールドを更新して退会日時を設定
    Member.objects.filter(group=group, member=request.user).update(left_at=timezone.now())
    return redirect('post:group_detail', pk=pk)

