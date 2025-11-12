from django.shortcuts import render
from django.contrib.sessions.models import Session
from django.views.generic import TemplateView, DetailView, CreateView, FormView, View
from .models import CustomUser
from .forms import CustomUserCreationForm, PasswordCheckForm
from django.urls import reverse_lazy

class SignUpView(CreateView):
    '''サインアップページのビュー
    '''
    # forms.pyで定義したフォームのクラス
    form_class = CustomUserCreationForm
    # レンダリングするテンプレート
    template_name = "signup.html"
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
    template_name = "signup_success.html"

class MypageView(DetailView):
    '''マイページのビュー
    '''
    model = CustomUser
    # レンダリングするテンプレート
    template_name = "mypage.html"

class UserInfoView(DetailView):
    '''ユーザ情報ページのビュー
    '''
    model = CustomUser
    # レンダリングするテンプレート
    template_name = "user_info.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 不要なsessionの更新
        if 'change' in self.request.session:
            self.request.session['change'] = '0'
            print(self.request.session['change'])
        return context
    
class PasswordCheckView(FormView):
    '''パスワード確認ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = "password_check.html"
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
                next_url = 'accounts:userinfo'
            # email変更ページへ
            elif self.request.session['change'] == 'email':
                next_url = 'accounts:userinfo'
            else:
                next_url = 'accounts:userinfo'
            del self.request.session['change']
        return reverse_lazy(next_url, kwargs={'pk': self.request.user.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ボタン押下時、session更新
        if self.request.method == 'POST':
            if "change_username" in self.request.POST:
                self.request.session['change'] = 'username'
            elif "change_password" in self.request.POST:
                self.request.session['change'] = 'password'
            elif "change_email" in self.request.POST:
                self.request.session['change'] = 'email'
            print(self.request.session['change'])
        
        # 前のページのURL(ユーザー情報ページ)
        previous_url = 'http://127.0.0.1:8000/api/accounts/'+str(self.request.user.id)
        
        # contextに設定
        context['previous'] = previous_url
        
        return context
    
    def form_valid(self, form):
        # 入力を取得
        pass_text = self.request.POST.get("password", "")
        
        # パスワードが正しいかチェック
        if self.request.user.check_password(pass_text):
            return super().form_valid(form)
        else:
            return super().form_invalid(form)
        
class ChangeUsernameView(TemplateView):
    '''ユーザー名変更ページのビュー
    '''
    # レンダリングするテンプレート
    template_name = "change_username.html"
    