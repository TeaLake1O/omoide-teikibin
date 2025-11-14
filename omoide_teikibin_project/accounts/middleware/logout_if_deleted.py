from django.contrib.auth import logout
from django.shortcuts import redirect

class LogoutIfDeletedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # ログイン済 & deleted_at がセットされている → ログアウト
        if user.is_authenticated and user.deleted_at:
            logout(request)
            return redirect('accounts:login')  # ログインページにリダイレクト

        return self.get_response(request)