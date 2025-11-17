from .models import CustomUser
from .forms import CustomUserCreationForm, PasswordCheckForm
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, CreateView, FormView, UpdateView
from rest_framework.authtoken.models import Token

class SignUpView(CreateView):
    '''サインアップページのビュー
    '''
    # forms.pyで定義したフォームのクラス
    form_class = CustomUserCreationForm
    # レンダリングするテンプレート
    template_name = 'signup.html'
    # サインアップ完了後のリダイレクト先のURLパターン
    success_url = reverse_lazy('accounts:signup_success')
    
    
    def form_valid(self, form):
        '''CreateViewクラスのform_valid()をオーバーライド
        
        フォームのバリエーションを通過したときに呼ばれる
        フォームデータの登録を行う
        
        paramaters:
            form(django.forms.Form):
            form_classに格納されているCustomUserCreationFormオブジェクト
        Return:
            HttpResponseRedirectオブジェクト:
            スーパークラスのform_valid()の戻り値を返すことで、
            success_urlで設定されているURLにリダイレクトさせる
        '''
        # formオブジェクトのフィールドの値をデータベースに保存
        user = form.save()
        self.object = user
        # 戻り値はスーパークラスのform_valid()の戻り値(HttpResponseRedirect)
        return super().form_valid(form)

class SignUpSuccessView(TemplateView):
    '''サインアップ完了ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'signup_success.html'

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

class ChangeEmailView(UpdateView):
    '''email変更ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'change_username.html'
    model = CustomUser
    fields = ('email',)
    # 完了ボタン押下後のリダイレクト先のURLパターン
    def get_success_url(self):
        return reverse_lazy('accounts:userinfo', kwargs={'pk': self.request.user.pk})

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
        print(0)
        if step == 1:
            # 最初の確認後 → 2回目の確認画面へ
            request.session['delete_step'] = 2
            return self.get(request, *args, **kwargs)

        elif step == 2:
            # 最終確認後 → 削除実行
            request.session['delete_step'] = 3
            user = request.user
            user.deleted_at = timezone.now()  # ← 現在時刻を保存
            user.save(update_fields=['deleted_at'])
            return self.get(request, *args, **kwargs)

# 砂場
class TestTokenView(TemplateView):
    '''トークンテストページのビュー
    '''
    # レンダリングするテンプレート
    template_name = 'test_token.html'
    
    def post(self, request, *args, **kwargs):
        # ログイン中のユーザーを取得
        username = request.POST.get('username')
        password = request.POST.get('password')
class TestTokenPageView(TemplateView):
    '''トークンテストページのビュー
    '''
    # レンダリングするテンプレート
    template_name = "test_tokenpage.html"