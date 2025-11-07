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
    
    # ログインページのビューの呼び出し
    path('login/',
         # ログイン用のテンプレート(フォーム)をレンダリング
         auth_views.LoginView.as_view(template_name='login.html'),
         name='login'),
    
    # ログアウトのビューの呼び出し
    path('logout/',
         auth_views.LogoutView.as_view(template_name='logout.html'),
         name='logout'),
    
    # ユーザ情報のビューの呼び出し
    path('info/',
         views.UserInfoView.as_view(),
         name='userinfo')
]