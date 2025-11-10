# post/views.py - Đề xuất sửa đổi (Sử dụng DRF)
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
import json

# Import các thư viện DRF cần thiết
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated

# Local imports
from .serializers import PostSerializer
from .models import Post, Group, Member, Notification
from .forms import PostCreationForm, GroupCreationForm

# ===== Page Rendering Views (Giữ nguyên) =====
def homepage(request):
    return render(request, 'homepage.html')

@login_required
def post_list_page(request):
    return render(request, 'post_list.html')

@login_required
def post_detail_page(request, post_id): # Note: This is redefined later, but let's keep it for now if used by old urls.
    post = get_object_or_404(Post, post_id=post_id)
    return render(request, 'post_detail.html', {'post': post})


# ===== API Views (Dùng DRF) =====

# 1. API LIST
class PostListAPIView(ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

# 2. API DETAIL
class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'pk' # Tự động tìm kiếm bằng pk (post_id)

# 3. API CREATE (Đơn giản hóa logic)
class PostCreateAPIView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated] # Chỉ người dùng đã đăng nhập mới được tạo

    def perform_create(self, serializer):
        # Tự động gán người dùng hiện tại là post_user
        serializer.save(post_user=self.request.user)

# ===== Class-Based Views for Page Rendering =====

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post_list.html' 
    context_object_name = 'posts' # Biến được truyền vào template: posts
    # Tự động lấy Post.objects.all().order_by('-created_at') (theo Meta ordering trong models.py)

# --- Group Views ---

class GroupListView(LoginRequiredMixin, ListView):
    """Trang hiển thị danh sách tất cả các nhóm"""
    model = Group
    template_name = 'group_list.html'
    context_object_name = 'groups'

class GroupDetailView(LoginRequiredMixin, DetailView):
    """Trang chi tiết của một nhóm"""
    model = Group
    template_name = 'group_detail.html'
    context_object_name = 'group'
    # 'pk' (primary key) sẽ được tự động lấy từ URL

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        
        # Lấy danh sách thành viên của nhóm
        context['members'] = Member.objects.filter(group=group, left_at__isnull=True) 
        
        # Lấy các bài đăng thuộc nhóm này (sử dụng related_name 'group_posts' đã thêm)
        context['posts'] = group.group_posts.all().order_by('-created_at')[:20] 
        
        # Kiểm tra xem người dùng hiện tại có phải là thành viên không
        context['is_member'] = Member.objects.filter(
            group=group, 
            member=self.request.user,
            left_at__isnull=True
        ).exists()
        return context

class GroupCreateView(LoginRequiredMixin, CreateView):
    """Trang tạo nhóm mới"""
    model = Group
    form_class = GroupCreationForm
    template_name = 'group_form.html'
    # Sau khi tạo thành công, chuyển đến trang chi tiết của nhóm đó
    
    def form_valid(self, form):
        # Tự động gán người tạo nhóm (creator) là người dùng hiện tại
        form.instance.creator = self.request.user
        # Lưu đối tượng group
        self.object = form.save() 
        
        # Tự động thêm người tạo nhóm làm thành viên (Member) đầu tiên
        Member.objects.create(
            member=self.request.user,
            group=self.object,
            role=True # Giả sử người tạo là admin (role=True)
        )
        # Chuyển hướng đến trang chi tiết
        return redirect(self.get_success_url())

    def get_success_url(self):
        # Lấy URL của trang chi tiết nhóm vừa tạo
        return reverse_lazy('post:group_detail', kwargs={'pk': self.object.pk})

# --- Logic Tham gia/Rời nhóm ---

@login_required
def join_group(request, pk):
    """View xử lý logic khi người dùng tham gia nhóm"""
    group = get_object_or_404(Group, pk=pk)
    
    # Tạo hoặc cập nhật (nếu đã từng tham gia rồi rời đi)
    Member.objects.update_or_create(
        group=group,
        member=request.user,
        defaults={'left_at': None, 'role': False} # Mặc định là thành viên thường
    )
    return redirect('post:group_detail', pk=pk)

@login_required
def leave_group(request, pk):
    """View xử lý logic khi người dùng rời nhóm"""
    group = get_object_or_404(Group, pk=pk)
    
    # Tìm và đánh dấu là đã rời đi (soft delete)
    Member.objects.filter(group=group, member=request.user).update(left_at=timezone.now())
    return redirect('post:group_detail', pk=pk)


class PostCreatePageView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreationForm
    template_name = 'create_post.html'
    success_url = reverse_lazy('post:post_list_page')

    def form_valid(self, form):
        form.instance.post_user = self.request.user
        # Giả sử form.instance.group đã được chọn trong form
        # (Bạn cần thêm 'group' vào PostCreationForm fields)
        
        response = super().form_valid(form) # Lưu bài đăng
        
        # --- BẮT ĐẦU LOGIC TẠO THÔNG BÁO ---
        new_post = self.object
        group = new_post.group
        
        # Lấy tất cả thành viên trong nhóm, TRỪ người vừa đăng bài
        members_to_notify = Member.objects.filter(
            group=group, 
            left_at__isnull=True
        ).exclude(member=self.request.user)
        
        notification_message = f"{self.request.user.username} đã đăng một bài viết mới trong nhóm {group.group_name}."
        
        # Tạo thông báo hàng loạt
        notifications = []
        for member_obj in members_to_notify:
            notifications.append(
                Notification(
                    username=member_obj.member, # Người nhận thông báo
                    notification_status="New Post", # Trạng thái
                    notification_message=notification_message,
                    Group=group,
                    title="Bài đăng mới"
                    # Bạn có thể thêm link đến bài đăng nếu muốn
                )
            )
        
        if notifications:
            Notification.objects.bulk_create(notifications)
        # --- KẾT THÚC LOGIC TẠO THÔNG BÁO ---
            
        return response

class NotificationListView(LoginRequiredMixin, ListView):
    """Hiển thị danh sách thông báo CHƯA ĐỌC của người dùng"""
    model = Notification
    template_name = 'notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        # Chỉ lấy thông báo của người dùng hiện tại và chưa đọc
        return Notification.objects.filter(
            username=self.request.user, 
            is_read=False
        ).order_by('-created_at')

@login_required
def mark_notification_as_read(request, pk):
    """Đánh dấu một thông báo là đã đọc"""
    notification = get_object_or_404(Notification, pk=pk, username=request.user)
    notification.is_read = True
    notification.save()
    
    # TODO: Chuyển hướng người dùng đến nơi hợp lý (ví dụ: bài đăng liên quan hoặc trang thông báo)
    return redirect('post:notification_list')