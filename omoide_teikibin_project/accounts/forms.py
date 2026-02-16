from django import forms
from django.core.validators import RegexValidator
# UserCreationFormクラスをインポート
from django.contrib.auth.forms import UserCreationForm
# models.pyで定義したカスタムUserモデルをインポート
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    '''UserCreationFormのサブクラス
    '''
    username = forms.CharField(
        label='ユーザー名',
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message='ユーザー名は英数字のみで入力してください。'
            )
        ]
    )
    class Meta:
        '''UserCreationFormのインナークラス
        Attributes:
            model:連携するUserモデル
            fields:フォームで使用するフィールド
        '''
        # 連携するUserモデルを設定
        model = CustomUser
        # フォームで使用するフィールドを設定
        # ユーザー名、メールアドレス、パスワード、パスワード(確認用)
        fields = ('username', 'email', 'password1', 'password2')

class PasswordCheckForm(forms.Form):
    '''パスワード入力フォーム(伏字)
    '''
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput(), min_length=8)