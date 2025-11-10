from django import forms
from .models import Post

class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('post_content', 'post_images', 'group') 
        
        widgets = {
            'post_content': forms.Textarea(attrs={'placeholder': '今何を考えている？', 'required': 'required'}),
        }   
        
        from django import forms
from .models import Group # Import model Group

class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('group_name', 'group_description')