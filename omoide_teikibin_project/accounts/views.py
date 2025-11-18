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
    '''サインアップ完了ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'signup_token.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.session['username']
        context['email'] = self.request.session['email']
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
        pass_text = self.request.POST.get("password", "")
        
        # パスワードが正しいかチェック
        if self.request.user.check_password(pass_text):
            return super().form_valid(form)
        else:
            return super().form_invalid(form)
        
class ChangeUsernameView(UpdateView):
    '''ユーザー名変更ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'change_password.html'
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
        # contextの設定
        context = self.get_context_data()
        # ログイン中のユーザーを取得
        username = request.user
        password = request.POST.get('password')
        email = request.POST.get('email')
        if password == None and email == None:
            context["message"] = "パスワードと新しいメールアドレスを入力してください"
            return self.render_to_response(context)
        elif email == request.user.email:
            context["error_message"] = "同じメールアドレスです"
            return self.render_to_response(context)
        try: 
            CustomUser.objects.get(email=email)
            context["error_message"] = "既に使用されているメールアドレスです。"
            return self.render_to_response(context)
        except CustomUser.DoesNotExist:
            pass
            
        user = authenticate(username=username, password=password)
        if user is None:
            context["error_message"] = "ユーザー名またはパスワードが違います"
            return self.render_to_response(context)
        
        # NewEmailに新しいメールアドレスを保存、トークンを生成
        req = NewEmail.objects.create(
                user=user,
                new_email=email
            )
        
        # 送信するURL(トークンとemailを付随)
        token_url = request.build_absolute_uri(reverse("accounts:tokenup") + f"?token={req.token}")
        # メール本文
        message=f'''以下のリンクをクリックしてトークンを確認してください：
        
{token_url}

このメールに心当たりがない場合は削除してください。
'''
        # メール送信
        send_mail(
            subject="あなたのトークンリンク",
            message=message,
            from_email="noreply@example.com",
            recipient_list=[email],
        )
        context["success_message"] = "メールを送信しました！"
        
        return self.render_to_response(context)

class TokenUpView(TemplateView):
    '''トークンURLページのビュー
    '''
    # レンダリングするテンプレート
    template_name = "tokenup.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # URL パラメータ token を取得
        token_key = self.request.GET.get("token")
        user = self.request.user
        if not token_key:
            context["error_message"] = "トークンが指定されていません。"
            return context
       
        try:     # トークンの照合
            req = NewEmail.objects.get(token=token_key)
            
            # emailの変更
            old_email = user.email
            user.email = req.new_email
            user.save()
            # このリクエストを削除（再利用禁止）
            req.delete()
            # contextに設定
            context["token_valid"] = True
            print('旧：', old_email)
            print('新：', user.email)
            
        except NewEmail.DoesNotExist:
            context["error_message"] = "トークンが無効か、存在しません。"
            
        return context

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
        