from common.serializer import *


class MypageUserInfSerializer(UserInfSerializer):
    
    is_me = serializers.SerializerMethodField(read_only = True)
    
    user_post = PostReadSerializer(many = True, read_only = True)
    
    class Meta(UserInfSerializer.Meta):
        fields = (*UserInfSerializer.Meta.fields ,"is_me","user_post")
    
    def get_is_me(self, obj):
        is_me =self.context["is_me"]
        return is_me