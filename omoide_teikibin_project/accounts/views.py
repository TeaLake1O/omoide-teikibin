from django.shortcuts import render
from django.contrib.auth.hashers import check_password
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
        # contextの取得
        context = super().get_context_data(**kwargs)

        
        return context
    
# class PasswordCheck(FormView):
#     '''パスワード確認ページのビュー
#     '''
#     # forms.pyで定義したフォームのクラス
#     form_class = PasswordCheckForm
#     success_url = reverse_lazy('accounts:signup_success')
#     # レンダリングするテンプレート
#     template_name = "password_check.html"
    
#     def form_valid(self, form):
#         print(1)
#         return super().form_valid(form)

class PasswordCheck(View):

    template_name = "password_check.html"

    def post(self, request):
            pass_text = request.POST.get("password", "")
           
            if request.user.check_password(pass_text):
                print("ok")
            else:
                print("dame")
