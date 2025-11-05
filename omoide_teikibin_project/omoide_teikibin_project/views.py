from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import EmailMessage

from .models import BlogPost, Group, Member, Post, Notification
from .forms import ContactForm

# ======================
#  ホームページ(Index)
# ======================
class IndexView(ListView):
    template_name = 'index.html'                      # テーブル画面
    model = BlogPost
    context_object_name = 'posts'                     # テンプレートで使う変数名
    queryset = BlogPost.objects.order_by('-posted_at')# 新しい順に表示
    paginate_by = 4                                   # 1ページあたり4件表示


# ======================
#  グループ一覧
# ======================
class GroupListView(ListView):
    template_name = 'group_list.html'
    model = Group
    context_object_name = 'groups'
    queryset = Group.objects.all().order_by('name')


# ======================
#  友達リスト
# ======================
class FriendListView(ListView):
    template_name = 'friend_list.html'
    model = Member
    context_object_name = 'friends'
    queryset = Member.objects.all().order_by('name')


# ======================
#  お知らせリスト
# ======================
class NotificationListView(ListView):
    template_name = 'notification_list.html'
    model = Notification
    context_object_name = 'notifications'
    queryset = Notification.objects.order_by('-created_at')
    paginate_by = 5


# ======================
#  投稿リスト
# ======================
class PostListView(ListView):
    template_name = 'post_list.html'
    model = Post
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-created_at')
    paginate_by = 3


# ======================
#  お問い合わせフォーム
# ======================
class ContactView(FormView):
    template_name = 'contact.html'              # テンプレート
    form_class = ContactForm                    #  フォームクラス
    success_url = reverse_lazy('blogapp:contact')  # 送信成功後のリダイレクト先

    def form_valid(self, form):
        # フォームデータの取得
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        title = form.cleaned_data['title']
        message = form.cleaned_data['message']

        # メールの内容作成
        subject = f'お問い合わせ: {title}'
        content = (
            f"送信者名: {name}\n"
            f"メールアドレス: {email}\n"
            f"タイトル: {title}\n"
            f"メッセージ:\n{message}"
        )

        # メールの送信設定
        from_email = 'admin@example.com'
        to_list = ['admin@example.com']

        # メール送信
        email_message = EmailMessage(
            subject=subject,
            body=content,
            from_email=from_email,
            to=to_list
        )
        email_message.send()

        # 成功メッセージの表示
        messages.success(self.request, 'お問い合わせは正常に送信されました。')

        # フォームが有効な場合は親クラスのform_validを呼び出す
        return super().form_valid(form)
