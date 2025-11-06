from django.urls import path
from . import views
<<<<<<< HEAD
=======
# viewsをインポートしてauth_viewという名前で利用する
>>>>>>> 8691ce8742cc5ef2ffce424babcfe2f704c14119
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    # サインアップページのビューの呼び出し
    path('signup/',
        views.SignUpView.as_view(),
        name='signup'),
    
    # サインアップ完了ページのビューの呼び出し
    path('signup_success/',
<<<<<<< HEAD
        views.SignUpSuccessView.as_view(),
        name='signup_success'),
    path('login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'),
=======
         views.SignUpSuccessView.as_view(),
         name='signup_success'),
    
    # ログインページの表示
    path('login/',
         # ログイン用のテンプレート(フォーム)をレンダリング
         auth_views.LoginView.as_view(template_name='login.html'),
         name='login'),
>>>>>>> 8691ce8742cc5ef2ffce424babcfe2f704c14119
]