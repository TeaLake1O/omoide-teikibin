
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    post_user__username = serializers.ReadOnlyField(source='post_user.username')

    class Meta:
        model = Post
        fields = (
            'post_id',
            'post_user', 
            'post_user__username', 
            'post_content', 
            'created_at', 
            'updated_at'
        )
        read_only_fields = ('post_id', 'post_user', 'created_at', 'updated_at')