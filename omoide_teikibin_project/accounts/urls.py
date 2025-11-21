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
    path('api/mypage/<int:pk>',
        views.MypageView.as_view(),
        name='mypage'),
    
    # ユーザ情報のビューの呼び出し
    path('api/<int:pk>',
        views.UserInfoView.as_view(),
        name='userinfo'),
    
    # パスワード確認ページのビューの呼び出し
    path('api/passwordcheck/',
        views.PasswordCheckView.as_view(),
        name='passwordcheck'),
    
    # ユーザー名変更ページのビューの呼び出し
    path('api/<int:pk>/change/username',
        views.ChangeUsernameView.as_view(),
        name='change_username'),
    
    # パスワード変更ページのビューの呼び出し
    path('api/<int:pk>/change/password',
        views.ChangePasswordView.as_view(),
        name='change_password'),
    
    # パスワード変更完了ページのビューの呼び出し
    path('api/<int:pk>/change/password/done',
        views.ChangePasswordDoneView.as_view(),
        name='change_password_done'),
    
    # email変更ページのビューの呼び出し
    path('api/<int:pk>/change/email',
        views.ChangeEmailView.as_view(),
        name='change_email'),
    
    # アカウント削除ページのビューの呼び出し
    path('api/<int:pk>/delete',
        views.UserDeleteView.as_view(),
        name='user_delete'),

    #API用
    
    path('api/mypage/<str:username>',views.MypageAPIView.as_view(), name = 'api_user_inf'),
    
    path('api/mypage/<str:username>/change',views.ChangeUserInfAPIView.as_view(), name = 'api_change'),
]