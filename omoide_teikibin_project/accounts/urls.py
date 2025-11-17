from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token

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
         auth_views.LoginView.as_view(template_name='login.html', next_page="/"),
         name='login'),
    
    # ログアウトのビューの呼び出し
    path('logout/',
         auth_views.LogoutView.as_view(template_name='logout.html'),
         name='logout'),
    
    # マイページのビューの呼び出し
    path('mypage/<int:pk>',
         views.MypageView.as_view(),
         name='mypage'),
    
    # ユーザ情報のビューの呼び出し
    path('<int:pk>',
         views.UserInfoView.as_view(),
         name='userinfo'),
    
    # パスワード確認ページのビューの呼び出し
    path('passwordcheck/',
         views.PasswordCheckView.as_view(),
         name='passwordcheck'),
    
    # ユーザー名変更ページのビューの呼び出し
    path('<int:pk>/change/username',
         views.ChangeUsernameView.as_view(),
         name='change_username'),
    
    # パスワード変更ページのビューの呼び出し
    path('<int:pk>/change/password',
         views.ChangePasswordView.as_view(),
         name='change_password'),
    
    # パスワード変更完了ページのビューの呼び出し
    path('<int:pk>/change/password/done',
         views.ChangePasswordDoneView.as_view(),
         name='change_password_done'),
    
    # email変更ページのビューの呼び出し
    path('<int:pk>/change/email',
         views.ChangeEmailView.as_view(),
         name='change_email'),
    
    # アカウント削除ページのビューの呼び出し
    path('<int:pk>/delete',
         views.UserDeleteView.as_view(),
         name='user_delete'),
    
    
    # テスト
    # トークン
    path('test/token',
         views.TestTokenView.as_view(),
         name='test_token'),
    # トークン送信完了
    path('test/tokenup',
         obtain_auth_token,
         name='test_tokenup'),
    path("token-page/",
         views.TestTokenPageView.as_view(),
         name="token-page"),
]