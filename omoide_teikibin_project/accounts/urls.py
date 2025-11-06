from django.urls import path
from . import views
# viewsをインポートしてauth_viewという名前で利用する
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    # サインアップページのビューの呼び出し
    path('signup/',
         views.SignUpView.as_view(),
         name='signup'),
    
    # サインアップ完了ページのビューの呼び出し
    path('signup_success/',
         views.SignUpSuccessView.as_view(),
         name='signup_success'),
    
    # ログインページの表示
    path('login/',
         # ログイン用のテンプレート(フォーム)をレンダリング
         auth_views.LoginView.as_view(template_name='login.html'),
         name='login'),
]