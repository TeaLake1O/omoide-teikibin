from .models import CustomUser, NewEmail
from .forms import CustomUserCreationForm, PasswordCheckForm
from django.contrib.auth import authenticate
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, CreateView, FormView, UpdateView
from rest_framework.authtoken.models import Token

#追加import
from rest_framework import permissions, generics
from django.db.models import Subquery, OuterRef
from post.models import *
from django.db.models import Prefetch
from .serializer import *


class SignUpView(CreateView):
    '''サインアップページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'signup.html'
    # forms.pyで定義したフォームのクラス
    form_class = CustomUserCreationForm
    # サインアップ完了後のリダイレクト先のURLパターン
    success_url = reverse_lazy('accounts:signup_token')
    
    def form_valid(self, form):
        # formオブジェクトのフィールドの値をデータベースに保存
        user = form.save()
        user.deleted_at = timezone.now()  # emailが未認証なので一旦削除日時登録
        self.object = user
        
        # セッションに保存
        self.request.session['username'] = user.username
        self.request.session['email'] = user.email
        
        # 戻り値はスーパークラスのform_valid()の戻り値(HttpResponseRedirect)
        return super().form_valid(form)

class SignUpTokenView(TemplateView):
    '''サインアップトークン送信ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'signup_token.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.session['username']
        context['email'] = self.request.session['email']
        return context
    
    def post(self, request, *args, **kwargs):
        username = request.session['username']
        email = request.session.get('email')
        # メールの再送信
        if 'resend' in request.POST:
            return self.send_token(request, username, email)
        # 通常送信
        password = request.POST.get('password')
        # contextの設定
        context = self.get_context_data()
        
        if password == None:
            context['message'] = 'パスワードを入力してください'
            return self.render_to_response(context)
        
        user = authenticate(username=username, password=password)
        if user is None:
            context['error_message'] = 'パスワードが違います'
            return self.render_to_response(context)
        
        return self.send_token(request, username, email)
    
    # トークン送信処理
    def send_token(self, request, username, email):
        context = self.get_context_data()
        user = CustomUser.objects.get(username=username)
        # すでに登録完了時
        if not user.deleted_at:
            context['already_send'] = '既に登録は完了しています'
            return self.render_to_response(context)
        # 既存レコードがあるか確認、なければ登録
        new_email_obj, created = NewEmail.objects.get_or_create(
            user=user,
            defaults={'new_email': email}
        )
        # 再送信かどうか
        if not created:
            # 既存レコードを更新
            new_email_obj.new_email = email
            new_email_obj.token = uuid.uuid4()
            new_email_obj.created_at = timezone.now()
            new_email_obj.save()
            # 再送信時に user を取得
            user = CustomUser.objects.get(username=username)
            success_text = 'メールを再送信しました'
        else:
            success_text = 'メールを送信しました'

        # URL生成
        token_url = request.build_absolute_uri(
            reverse('accounts:tokenup') + f'?token={new_email_obj.token}'
        )
        message = f'''以下のリンクをクリックしてトークンを確認してください：

{token_url}

このメールに心当たりがない場合は削除してください。
'''
        send_mail(
            subject='あなたのトークンリンク',
            message=message,
            from_email='noreply@example.com',
            recipient_list=[email],
        )
        context['success_message'] = success_text
        return self.render_to_response(context)

class TokenUpView(TemplateView):
    '''トークンURLページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'tokenup.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # URL パラメータ token を取得
        token_key = self.request.GET.get('token')
        if not token_key:
            context['error_message'] = 'トークンが指定されていません。'
            return context
       
        try:     # トークンの照合
            req = NewEmail.objects.get(token=token_key)
            username = req.user
            user = CustomUser.objects.get(username=username)
            # データの更新
            if user.email == req.new_email:  # 新規登録の場合
                user.deleted_at = None
                url = reverse('accounts:login')
                message = 'ログインページへ'
            else:   # email変更の場合
                user.email = req.new_email
                url = reverse('index')
                message = 'ホームページへ'
            user.save()
            # このリクエストを削除（再利用禁止）
            req.delete()
            # contextに設定
            context['token_valid'] = True
            context['username'] = username
            context['url'] = url
            context['link_message'] = message
            
        except NewEmail.DoesNotExist:
            context['error_message'] = 'トークンが無効か、存在しません。'
            
        return context

class MypageView(DetailView):
    '''マイページのビュー
    '''
    model = CustomUser
    # レンダリングするテンプレート
    template_name = 'mypage.html'

class UserInfoView(DetailView):
    '''ユーザ情報ページのビュー
    '''
    model = CustomUser
    # レンダリングするテンプレート
    template_name = 'user_info.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 不要なsessionの更新
        if 'change' in self.request.session:
            self.request.session['change'] = '0'
            print(self.request.session['change'])
        if 'delete_step' in self.request.session:
            self.request.session['delete_step'] = 1
            print(self.request.session['delete_step'])
        return context

class PasswordCheckView(FormView):
    '''パスワード確認ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'password_check.html'
    # forms.pyで定義したフォームのクラス
    form_class = PasswordCheckForm
    # パスワード認証後のリダイレクト先のURLパターン
    def get_success_url(self):
        # session内容からURLを分岐
        if 'change' in self.request.session:
            # ユーザー名変更ページへ
            if self.request.session['change'] == 'username':
                next_url = 'accounts:change_username'
            # パスワード変更ページへ
            elif self.request.session['change'] == 'password':
                next_url = 'accounts:change_password'
            # email変更ページへ
            elif self.request.session['change'] == 'email':
                next_url = 'accounts:change_email'
            # アカウント削除ページへ
            elif self.request.session['change'] == 'user_delete':
                next_url = 'accounts:user_delete'
            else:
                next_url = 'accounts:userinfo'
            del self.request.session['change']
        print(self.request.session, next_url)
        return reverse_lazy(next_url, kwargs={'pk': self.request.user.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ボタン押下時、session更新
        if self.request.method == 'POST':
            if 'change_username' in self.request.POST:
                self.request.session['change'] = 'username'
            elif 'change_password' in self.request.POST:
                self.request.session['change'] = 'password'
            elif 'change_email' in self.request.POST:
                self.request.session['change'] = 'email'
            elif 'delete' in self.request.POST:
                self.request.session['change'] = 'user_delete'
            print(self.request.session['change'])
        
        return context
    
    def form_valid(self, form):
        # 入力を取得
        pass_text = self.request.POST.get('password', '')
        # contextの設定
        context = self.get_context_data()
        # パスワードが正しいかチェック
        if self.request.user.check_password(pass_text):
            return super().form_valid(form)
        else:
            context['error_message'] = 'パスワードが間違っています'
            return self.render_to_response(context)

class ChangeUsernameView(UpdateView):
    '''ユーザー名変更ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'change_username.html'
    model = CustomUser
    fields = ('username',)
    # 完了ボタン押下後のリダイレクト先のURLパターン
    def get_success_url(self):
        return reverse_lazy('accounts:userinfo', kwargs={'pk': self.request.user.pk})

class ChangePasswordView(PasswordChangeView):
    '''パスワード変更ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'change_password.html'
    
    # パスワード変更後のリダイレクト先のURLパターン
    def get_success_url(self):
        return reverse_lazy('accounts:change_password_done', kwargs={'pk': self.request.user.pk})

class ChangePasswordDoneView(PasswordChangeDoneView):
    '''パスワード変更完了ページのビュー
    '''
    template_name = 'change_password_done.html'

class ChangeEmailView(TemplateView):
    '''email変更ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'change_email.html'
    
    def post(self, request, *args, **kwargs):
        username = request.user
        # メールの再送信
        if 'resend' in request.POST:
            req = NewEmail.objects.get(user=request.user)
            email = req.new_email
            return self.send_token(request, username, email)
        # 通常送信
        # ログイン中のユーザーを取得
        password = request.POST.get('password')
        email = request.POST.get('email')
        # contextの設定
        context = self.get_context_data()
        if password == None and email == None:
            context['message'] = 'パスワードと新しいメールアドレスを入力してください'
            return self.render_to_response(context)
        elif email == request.user.email:
            context['error_message'] = '同じメールアドレスです'
            return self.render_to_response(context)
        try:    # 新しいメールアドレスが使用されていないかチェック
            CustomUser.objects.get(email=email)
            context['error_message'] = '既に使用されているメールアドレスです。'
            return self.render_to_response(context)
        except CustomUser.DoesNotExist:
            pass
            
        user = authenticate(username=username, password=password)
        if user is None:
            context['error_message'] = 'ユーザー名またはパスワードが違います'
            return self.render_to_response(context)
        return self.send_token(request, username, email)
        
    # トークン送信処理
    def send_token(self, request, username, email):
        context = self.get_context_data()
        user = CustomUser.objects.get(username=username)
        # すでに登録完了時
        if user.email == email:
            context['already_send'] = '既に登録は完了しています'
            return self.render_to_response(context)
        # 既存レコードがあるか確認、なければ登録
        new_email_obj, created = NewEmail.objects.get_or_create(
            user=user,
            defaults={'new_email': email}
        )
        # 再送信かどうか
        if not created:
            # 既存レコードを更新
            new_email_obj.new_email = email
            new_email_obj.token = uuid.uuid4()
            new_email_obj.created_at = timezone.now()
            new_email_obj.save()
            # 再送信時に user を取得
            user = CustomUser.objects.get(username=username)
            success_text = 'メールを再送信しました'
        else:
            success_text = 'メールを送信しました'

        # URL生成
        token_url = request.build_absolute_uri(
            reverse('accounts:tokenup') + f'?token={new_email_obj.token}'
        )
        message = f'''以下のリンクをクリックしてトークンを確認してください：

{token_url}

このメールに心当たりがない場合は削除してください。
'''
        send_mail(
            subject='あなたのトークンリンク',
            message=message,
            from_email='noreply@example.com',
            recipient_list=[email],
        )
        context['success_message'] = success_text
        return self.render_to_response(context)

class UserDeleteView(TemplateView):
    '''アカウント削除ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'user_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # contextに設定
        context['step'] = self.request.session.get('delete_step', 1)
        context['cancel_url'] = reverse('accounts:userinfo', args=[self.request.user.pk])
        return context
    
    def post(self, request, *args, **kwargs):
        '''削除フローの制御'''
        step = request.session.get('delete_step', 1)
        if step == 1:
            # 最初の確認後 → 2回目の確認画面へ
            request.session['delete_step'] = 2
            return self.get(request, *args, **kwargs)

        elif step == 2:
            # 最終確認後 → 削除実行
            request.session['delete_step'] = 3
            user = request.user
            user.deleted_at = timezone.now()  # 現在時刻を保存
            user.save(update_fields=['deleted_at'])
            return self.get(request, *args, **kwargs)


class MypageAPIView(generics.RetrieveAPIView):
    
    #シリアライザ
    serializer_class = MypageUserInfSerializer
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    lookup_field = "username"
    
    def get_queryset(self):
        
        me = self.request.user
        username = self.kwargs["username"]
        
        user_post = (
            Post.objects
            .filter(
                post_user__username = username,
                deleted_at__isnull = True,
                group__member__member = me
            ).order_by("-created_at")
        )
        
        rs = (
            CustomUser.objects
            .filter(
                username = username,
                deleted_at__isnull = True,
                #投稿のような複数あるデータはprefetch_relatedを使う
            ).prefetch_related(
                Prefetch("post_set",
                        queryset = user_post,
                        to_attr="user_post",
                    )
            )
        )
        return rs
    
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        me = self.request.user
        username = self.kwargs["username"]
        
        ctx["is_me"] = me.is_authenticated and me.username == username
        return ctx

class ChangeUserInfAPIView(generics.UpdateAPIView):
    
    #シリアライザ
    serializer_class = ChangeUserInfWriteSerializer
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    lookup_field = "username"
    
    queryset = CustomUser.objects.all()

class UserInfAPIView(generics.RetrieveAPIView):
    
    #シリアライザ
    serializer_class = UserInfReadSerializer
    
    #未ログインで403を返す
    permission_classes = [permissions.IsAuthenticated]
    
    lookup_field = "username"
    
    def get_queryset(self):
        
        me = self.request.user
        
        rs = (
            CustomUser.objects
            .filter(
                username = me.username,
                deleted_at__isnull = True
            )
        )
        return rs
    
