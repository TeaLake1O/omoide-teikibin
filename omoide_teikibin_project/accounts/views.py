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
        if 'cu' in self.request.session:
            print(self.request.session['cu'])
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
        if 'cu' in self.request.session:
            next_url = 'accounts:change_username'
            del self.request.session['cu']
        else:
            next_url = 'accounts:userinfo'
        return reverse_lazy(next_url, kwargs={'pk': self.request.user.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.method == 'POST':
            # print(self.request.GET)
            # print(self.request.POST)
            if "change_username" in self.request.POST:
                self.request.session['cu'] = '1'
                print('change_un')
        
        
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
    