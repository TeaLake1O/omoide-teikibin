from common.serializer import *
from datetime import date


class MypageUserInfSerializer(UserInfSerializer):
    
    user_post = PostReadSerializer(many = True, read_only = True)
    
    class Meta(UserInfSerializer.Meta):
        model = CustomUser
        fields = (*UserInfSerializer.Meta.fields ,"user_post")

class ChangeUserInfWriteSerializer(serializers.ModelSerializer):
    
    nickname = serializers.CharField(
        write_only = True,
        allow_null = True,
        required = False,
    )
    
    birthday = serializers.DateField(
        write_only = True,
        allow_null = True,
        required = False,
    )
    icon = serializers.ImageField(
        write_only = True,
        allow_null = True,
        required = False,
    )
    
    class Meta:
        model = CustomUser
        fields = ["nickname", "birthday", "icon"]
    
    def validate_nickname(self, nickname :str):
        
        if nickname is None :
            return None
        
        return nickname.strip()
    
    def validate_birthday(self, birthday):
        
        if birthday is None:
            return None
        
        today = date.today()
        
        if birthday > today :
            raise serializers.ValidationError("日付が不正です")
        
        return birthday

    def validate(self, attrs):
        
        me = self.context["request"].user
        if me.pk != self.instance.pk:
            raise serializers.ValidationError("変更できるのは自身のみです")
        
        return attrs
    
    def update(self, instance :CustomUser, validated_data):
        
        #null、つまり指定しないなら更新しない
        if "nickname" in validated_data:
            nickname = validated_data["nickname"]
            if nickname not in ("", None):
                instance.nickname = nickname
            
        if "birthday" in validated_data:
            birthday = validated_data["birthday"]
            if birthday is not None:
                instance.birthday = birthday
        
        if "icon" in validated_data:
            icon = validated_data["icon"]
            if icon is not None:
                instance.user_icon = icon

        instance.save()
        
        return instance

class UserInfReadSerializer(DetailUserInfSerializer):
    
    class Meta(DetailUserInfSerializer.Meta):
        pass
